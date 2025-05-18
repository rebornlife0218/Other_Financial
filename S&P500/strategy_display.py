import streamlit as st
import os

# 頁面標題
st.title("S&P500 策略展示")

# 策略說明字典
strategy_descriptions = {
    "Strategy 1": "上一季報酬表現最好的10檔，等權重持有。",
    "Strategy 2": "上一季報酬表現最差的10檔，等權重持有。",
    "Strategy 3": "上一季表現最好的20檔，再以sharpe極大為目標分配權重。",
    "Strategy 4": "上一季表現最好的20檔，再篩選波動率前10小。"
}

# 回測數據字典
backtesting = {
    "Strategy 1": "Annual Return: 9.38%\nAnnual Volatility: 34.79%\nSharpe Ratio: 0.21\nMax Drawdown: -74.27%" ,
    "Strategy 2": "Annual Return: -8.75%\nAnnual Volatility: 49.01%\nSharpe Ratio: -0.22\nMax Drawdown: -97.08%",
    "Strategy 3": "Annual Return: 10.49%\nAnnual Volatility: 28.11%\nSharpe Ratio: 0.30\nMax Drawdown: -67.47%",
    "Strategy 4": "Annual Return: 2.70%\nAnnual Volatility: 32.09%\nSharpe Ratio: 0.02\nMax Drawdown: -93.90%"
}

# 策略選項
strategy_options = ["Strategy 1", "Strategy 2", "Strategy 3", "Strategy 4"]
selected_strategy = st.selectbox("請選擇一個策略：", strategy_options)

# 顯示對應的圖片與說明
if selected_strategy:
    # 圖片檔案路徑
    image_path = os.path.join(f"Strategy{strategy_options.index(selected_strategy) + 1}.jpg")
    
    try:
        st.write("**策略說明**：")
        st.write(strategy_descriptions[selected_strategy])
        st.write("**回測數據**：")
        st.text(backtesting[selected_strategy])
        with open(image_path, "rb") as img_file:
            st.image(img_file, caption=selected_strategy, use_container_width=True)
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: gray;'>由操盤人講堂第一組製作 2025.05</div>", unsafe_allow_html=True) 
    except FileNotFoundError:
        st.error(f"找不到圖片檔案：{image_path}。請確保圖片檔案存在於正確的目錄中。")

# streamlit run strategy_display.py
