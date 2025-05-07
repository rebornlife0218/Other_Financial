# https://medium.com/@The-Quant-Trading-Room/quant-traders-toolkit-fundamental-data-on-steroids-a-300-value-absolutely-free-full-code-bc9784b9fec6

import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import numpy as np
import requests

# View Dataframe as an interactive table in Jupyter Notebook
# from itables import init_notebook_mode
# init_notebook_mode(all_interactive=True)

# 公司 CIK 資料取得
def get_companies_dct(headers):
    
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    companyTickers = requests.get(tickers_url, headers=headers)
    company_dct = companyTickers.json()
    cik_dct = {k:v for k,v in 
               [(company_dct[x]['ticker'], 
                str(company_dct[x]['cik_str']).zfill(10))   # 確保 CIK 是 10 位數，方便組合 API URL
                for x in company_dct]}

    return cik_dct

# 將 frame（期間）轉換為可排序的浮點數
def convert_frame(x):

    if len(x) == 6:
        x_con = float(x[2:]) + .3   # 年報
    else:
        if x[-1] =='I':
            x_con = float('.'.join(x[2:-1].split('Q')))
        else:
            x_con = float('.'.join(x[2:].split('Q')))

    return x_con

# 取得公司財報 XBRL 資料
def get_data(ticker, cik):
    
    company_url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    companyFacts = requests.get(company_url, headers=headers)
    cFacts = companyFacts.json()
    facts = cFacts['facts']
    
    # 提取 10-Q 和 10-K 中的資料並整理為表格
    Q10K10_values = [(f"{t}_{u}",
                      [(i['end'], i['val'], i['filed'], i['frame'])
                        if 'frame' in i.keys() 
                        else (i['end'], i['val'], i['filed'], np.nan)
                       for i in facts[c][t]['units'][u] 
                       if i['form'] in ['10-Q', '10-K', '10-Q/A', '10-K/A']
                      ]
                     )
                     for c in facts.keys()
                     for t in facts[c].keys()
                     for u in facts[c][t]['units'].keys()
                    ]
    Q10K10_values_d = {k:v for k,v in Q10K10_values}
    
    comp_df = pd.DataFrame()
    
    tag_lst = list(Q10K10_values_d.keys())
    for tag in tqdm(tag_lst):
        columns = ['end', 'val', 'filed', 'frame']
        df = pd.DataFrame(Q10K10_values_d[tag], columns=columns)
        df = df.dropna()
        df.index = pd.to_datetime(df.filed)
        df = df.drop(columns=['filed', 'end'])  
        df = df.sort_index(ascending=True)
        df.frame = df.frame.apply(lambda x: convert_frame(x))
        df = df.reset_index()
        
        # 移除不相關的更新
        current_period = 0
        kept_indices = []
        for row in df.iterrows():
            if row[1].frame >= current_period:
                kept_indices.append(row[0])
                current_period = row[1].frame
        df = df.loc[df.index.isin(kept_indices)]
        
        # 移除非最新報告，避免相同 filing date 重複紀錄
        bool_series = df.duplicated(subset='filed', keep='last')
        df = df[~bool_series]
        df = df.rename(columns={'val': tag})
        
        # 合併所有欄位
        if comp_df.empty:
            comp_df = df
        else:
            comp_df = pd.merge(comp_df, df, 
                               on=['filed', 'frame'], 
                               how='outer', copy=False)
    
    # Sort all information in ascending order of filing date
    comp_df.index = pd.to_datetime(comp_df.filed)
    comp_df = comp_df.drop(columns=['filed'])
    comp_df = comp_df.sort_index(ascending=True)
    comp_df = comp_df.reset_index(drop=False)
    
    # 每次報告的行都填入最近的可用值
    comp_df = comp_df.ffill(axis=0)     # 向前填補缺漏值

    # 刪除 frame 與 filed 欄，留下指標本身
    bool_series = comp_df.duplicated(subset='filed', keep='last')
    comp_df = comp_df[~bool_series]
    comp_df.index = comp_df.filed
    comp_df = comp_df.drop(columns=['frame','filed'])
        
    return(comp_df)

headers = {'User-Agent': "YOUR@EMAIL.HERE"}
cik_dct = get_companies_dct(headers)
ticker = 'AAPL'
cik = cik_dct[ticker]
comp_df = get_data(ticker, cik)
print(comp_df)
# 定義財報項目的分類
categories = {
    '資產負債表': ['Assets', 'Liabilities', 'Equity', 'CommonStockShares', 'ContractWithCustomerLiability_USD', 'ContractWithCustomerLiabilityCurrent_USD', 'DebtInstrument', 'Deferred', 'Unrecorded', 
                  'LongTermDebt', 'FinanceLease', 'AccountsPayable', 'AccountsReceivable', 'AvailableForSaleSecurities'],
    '綜合損益表': ['Revenues', 'Costs', 'Income', 'Expense', 'CommonStockDividends', 'ContractWithCustomerLiabilityRevenueRecognized_USD', 'Depreciation', 'Dividends_USD', 'EarningsPerShare', 'Unrecognized'],
    '現金流量表': ['Operating', 'Investing', 'Financing', 'PaymentsToAcquirePropertyPlantAndEquipment_USD', 'PaymentsForRepurchaseOfCommonStock_USD', 'ProceedsFrom'],
    '其他':[]
}

# 初始化分類結果
classified_columns = {category: [] for category in categories}

# 遍歷欄位名稱並分類
for col in comp_df.columns:
    found = False
    for category, keywords in categories.items():
        if category == '其他':
            continue
        if any(keyword in col for keyword in keywords):
            classified_columns[category].append(col)
            found = True
            break
    if not found:
        classified_columns['其他'].append(col)

# 印出分類結果
for category, columns in classified_columns.items():
    print(f"--------- {category} ---------")
    for col in columns:
        print(col)
    print()

fig, ax = plt.subplots(5, figsize=(12, 8))
ax[0].plot(comp_df.PaymentsToAcquirePropertyPlantAndEquipment_USD)      # 資本支出
ax[0].set_title("PaymentsToAcquirePropertyPlantAndEquipment_USD")
ax[1].plot(comp_df.ResearchAndDevelopmentExpense_USD)      
ax[1].set_title("ResearchAndDevelopmentExpense_USD")
ax[2].plot(comp_df.PaymentsForRepurchaseOfCommonStock_USD)      # 普通股回購
ax[2].set_title("PaymentsForRepurchaseOfCommonStock_USD")
ax[3].plot(comp_df.GrossProfit_USD)
ax[3].set_title("GrossProfit_USD")
ax[4].plot(comp_df.OperatingExpenses_USD)
ax[4].set_title("OperatingExpenses_USD")
fig.tight_layout()
plt.show()

