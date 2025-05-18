import streamlit as st
import os

# 頁面標題
st.title("S&P500 策略展示")

# 策略說明字典
strategy_descriptions = {
    "Strategy 1": "上一季報酬表現最好的10檔，等權重持有。",
    "Strategy 2": "上一季報酬表現最差的10檔，等權重持有。",
    "Strategy 3": "上一季sharpe表現最好的20檔，再以極大化sharpe為目標自動分配權重。",
    "Strategy 4": "上一季報酬表現最好的20檔，從中再篩選波動率較小的10檔。"
}

# 回測數據字典
backtesting = {
    "Strategy 1": "Annual Return: 9.38%\nAnnual Volatility: 34.79%\nSharpe Ratio: 0.21\nMax Drawdown: -74.27%" ,
    "Strategy 2": "Annual Return: -8.75%\nAnnual Volatility: 49.01%\nSharpe Ratio: -0.22\nMax Drawdown: -97.08%",
    "Strategy 3": "Annual Return: 10.49%\nAnnual Volatility: 28.11%\nSharpe Ratio: 0.30\nMax Drawdown: -67.47%",
    "Strategy 4": "Annual Return: 2.70%\nAnnual Volatility: 32.09%\nSharpe Ratio: 0.02\nMax Drawdown: -93.90%"
}

# SPY buy and hold 回測數據
spy_backtesting = "Annual Return: 7.25%\nAnnual Volatility: 14.05%\nSharpe Ratio: 0.37\nMax Drawdown: -45.96%"

# 策略選項
strategy_options = ["Strategy 1", "Strategy 2", "Strategy 3", "Strategy 4"]
selected_strategy = st.selectbox("請選擇一個策略：", strategy_options)

# 顯示對應的圖片與說明
if selected_strategy:
    # 圖片檔案路徑
    image_path = f"S&P500/Strategy{strategy_options.index(selected_strategy) + 1}.jpg"
    
    try:
        st.write("**策略說明**：")
        st.write(strategy_descriptions[selected_strategy])
        
       # 左右切分區塊
        col1, col2 = st.columns(2)
        with col1:
            st.write("**策略回測數據**")
            st.text(backtesting[selected_strategy])
        with col2:
            st.write("**SPY Buy and Hold 回測數據**")
            st.text(spy_backtesting)
            
        st.image(image_path, caption=selected_strategy, use_container_width=True)
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: gray;'>由操盤人講堂第一組製作 2025.05</div>", unsafe_allow_html=True) 
    except FileNotFoundError:
        st.error(f"找不到圖片檔案：{image_path}。請確保圖片檔案存在於正確的目錄中。")

# streamlit run strategy_display.py
