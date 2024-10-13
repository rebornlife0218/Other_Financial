# 探討勞退基金和 0050ETF 報酬率之關係

import urllib.request as req
import bs4
import csv
from datetime import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


# 爬蟲抓取勞動部勞退基金績效
url = "https://www.blf.gov.tw/49200/49255/49261/49269/49279/73028/post"
request = req.Request(url,
    headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
) 
with req.urlopen(request) as response:
    data = response.read().decode("utf-8")

soup = bs4.BeautifulSoup(data, "html.parser")
rows = soup.find_all('tr')[5:-15]

with open('output.csv', 'w', newline ='', encoding ='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    for row in rows:
        row_data = []
        td_tags = row.find_all('td')
        
        # 刪除最後一欄的公布時間
        for i, td_tag in enumerate(td_tags):
            if i != len(td_tags) - 1:       # 檢查目前 <td> 標籤是否為最後一列數據，若不是，則將其內容新增至 row_data 清單中
                row_data.append(td_tag.text.strip())
        
       # 删除字串中的"年"和"月份"
        year_month = row_data[0].replace("年", "-").replace("月份", "")
        year, month = map(int, year_month.split('-'))
        year += 1911
        
        # 將年份和月份轉換為datetime格式
        date_obj = datetime(year, month, 1)                
        row_data[0] = date_obj.strftime("%Y-%m-%d") 
        
        csvwriter.writerow(row_data)

# 將日期列解析為時間索引
df = pd.read_csv('output.csv', parse_dates = [0], index_col=0, header=None)     # 沒有指定 header=None 參數，導致Pandas將第一行資料作為列名，而不是資料行。
df.to_csv('output.csv', encoding ='utf-8-sig')
df.index = df.index.strftime('%Y-%m')
df.set_axis(["0050_returns"], axis="columns", inplace=True)
df['0050_returns'] = df['0050_returns'].str.strip('%').astype(float)

# 下載0050數據
stock_data = yf.download('0050.TW', start ='2013-12-31', end = '2024-1-31')
stock_data = stock_data['Close']

monthly_returns = (stock_data.resample('BM').last().pct_change(1)* 100)    # 每月收盤價相對於前一月的變化百分比
monthly_returns.index = monthly_returns.index.strftime("%Y-%m")
monthly_returns = monthly_returns.dropna()      # 刪除2013-12的遺失值

# 合并DataFrame
merged_df = pd.concat([df, monthly_returns], axis=1, join='inner')
merged_df.set_axis(['LPF_returns', '0050_returns'], axis="columns", inplace=True)
merged_df = merged_df[::-1]     # 把順序倒過來

cumulative_returns = merged_df.cumsum()

# 繪製折線圖
plt.figure(figsize=(10, 6))
plt.plot(merged_df.index, merged_df['LPF_returns'], label='LPF Cumulative Returns')
plt.plot(cumulative_returns.index, cumulative_returns['0050_returns'], label='0050 Cumulative Returns')

# 添加圖例和標籤
plt.legend()
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_locator(plt.MultipleLocator(5))       # 避免標籤的字重疊
plt.ylabel('Cumulative Returns (%)')
plt.title('LPF and 0050 Cumulative Returns Comparison')
plt.grid(True)
plt.show()
