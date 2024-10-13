import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 讀取資料
file_path = 'TWII_30years.feather'
data = pd.read_feather(file_path)
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month

# 定義分析函數
def analyze_monthly_changes(year_data):
    monthly_changes = []

    # 取得每個月份的交易數據
    for month in range(1, 13):
        month_data = year_data[year_data['Month'] == month]

        if not month_data.empty:
            # 獲取月初和月末的交易日
            first_day = month_data.iloc[0]
            last_day = month_data.iloc[-1]

            # 計算漲跌幅
            pct_change = (last_day['Adj Close'] - first_day['Adj Close']) / first_day['Adj Close']
            monthly_changes.append({'Year': first_day['Year'], 'Month': month, 'Pct Change': pct_change})
    
    return monthly_changes
    
# 分析所有年份的資料
all_monthly_changes = []

for year, year_data in data.groupby('Year'):
    all_monthly_changes.extend(analyze_monthly_changes(year_data))

# 將結果轉成DataFrame
monthly_changes_df = pd.DataFrame(all_monthly_changes)

# 計算每個月份的漲的次數和平均漲幅
monthly_stats = monthly_changes_df.groupby('Month').agg(
    Total_Up_Count=('Pct Change', lambda x: (x > 0).sum()),
    Total_Down_Count=('Pct Change', lambda x: (x < 0).sum()),
    Avg_Up_Percent=('Pct Change', lambda x: x[x > 0].mean() * 100),  # 轉換成百分比
    Avg_Down_Percent=('Pct Change', lambda x: x[x < 0].mean() * 100)  # 轉換成百分比
).reset_index()

# 找出漲的次數最多的月份
max_up_month = monthly_stats.loc[monthly_stats['Total_Up_Count'].idxmax()]

print("Month with most increases:")
print(f"Month: {max_up_month['Month']} - Count: {max_up_month['Total_Up_Count']} - Avg Increase: {max_up_month['Avg_Up_Percent']:.2f}%")
print("\nMonthly Statistics:")
print(monthly_stats)

# 繪製圖形
plt.figure(figsize=(12, 6))

# 設置長條圖的寬度和位置
bar_width = 0.4
x = range(len(monthly_stats['Month']))

# 繪製漲和跌的次數
plt.bar([i - bar_width/2 for i in x], monthly_stats['Total_Up_Count'], width=bar_width, color='lightcoral', label='Number of Increases')
plt.bar([i + bar_width/2 for i in x], monthly_stats['Total_Down_Count'], width=bar_width, color='lightgreen', label='Number of Decreases')

plt.title('Monthly Increases and Decreases')
plt.xlabel('Month')
plt.ylabel('Count')
plt.xticks(ticks=x, labels=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
plt.grid(axis='y')
plt.legend()

# 顯示平均漲跌百分比
for index, row in monthly_stats.iterrows():
    if row['Avg_Up_Percent'] > 0:
        plt.text(index - 0.2, row['Total_Up_Count'] + 0.1, f"{row['Avg_Up_Percent']:.1f}%", color='black', ha='center', fontsize=9)
    if row['Avg_Down_Percent'] < 0:
        plt.text(index + 0.2, row['Total_Down_Count'] + 0.1, f"{row['Avg_Down_Percent']:.1f}%", color='black', ha='center', fontsize=9)

plt.tight_layout()
plt.show()
