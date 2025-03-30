import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Function to fetch stock data
def get_stock_data(symbol, period="3mo", interval="1d"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            raise ValueError("No data found for the given stock symbol.")
        hist['SMA_10'] = hist['Close'].rolling(window=10).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        return hist
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

# Function to plot stock data
def plot_stock_data(hist, symbol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Closing Price', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Open'], mode='lines', name='Opening Price', line=dict(color='#2ca02c', width=2)))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_10'], mode='lines', name='10-Day SMA', line=dict(color='#d62728', dash='dot', width=2)))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], mode='lines', name='50-Day SMA', line=dict(color='#ff7f0e', dash='dot', width=2)))
    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Candlestick'))
    fig.update_layout(title=f"📊 Stock Price of {symbol}", xaxis_title="📅 Date", yaxis_title="💰 Price (USD)", template="plotly_dark", font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)

# Function to display stock summary
def display_stock_summary(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        st.subheader("📌 Stock Summary")
        st.markdown(f"**🏢 Company Name:** {info.get('longName', 'N/A')}")
        st.markdown(f"**🏛 Sector:** {info.get('sector', 'N/A')}")
        st.markdown(f"**💰 Market Cap:** {info.get('marketCap', 'N/A'):,}")
        st.markdown(f"**📈 52-Week High:** {info.get('fiftyTwoWeekHigh', 'N/A')}")
        st.markdown(f"**📉 52-Week Low:** {info.get('fiftyTwoWeekLow', 'N/A')}")
    except Exception as e:
        st.error(f"Error fetching stock summary: {e}")

# Function to display latest news
def display_news(symbol):
    st.subheader("📰 Latest News")
    try:
        stock = yf.Ticker(symbol)
        if 'news' in stock.info:
            news = stock.news[:5]
            for article in news:
                st.markdown(f"🔗 [{article['title']}]({article['link']})")
        else:
            st.write("No news available.")
    except Exception as e:
        st.error(f"Error fetching news: {e}")

# Function for comparative stock performance
def compare_stocks(symbol1, symbol2, period="3mo", interval="1d"):
    st.subheader("📊 Compare Stock Performance")
    hist1 = get_stock_data(symbol1, period, interval)
    hist2 = get_stock_data(symbol2, period, interval)
    if hist1 is not None and hist2 is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist1.index, y=hist1['Close'], mode='lines', name=f'{symbol1} Close', line=dict(color='#1f77b4', width=2)))
        fig.add_trace(go.Scatter(x=hist2.index, y=hist2['Close'], mode='lines', name=f'{symbol2} Close', line=dict(color='#d62728', width=2)))
        fig.update_layout(title=f"⚖ {symbol1} vs {symbol2} Performance", xaxis_title="📅 Date", yaxis_title="💰 Price (USD)", template="plotly_dark", font=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)

# Streamlit UI
st.set_page_config(page_title="📈 Stock Market Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")
st.write("🔍 Enter a stock symbol (e.g., AAPL for Apple, TSLA for Tesla), select a time period and data interval, then click the button to fetch data.")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    symbol = st.text_input("📌 Stock Symbol", "AAPL").upper()
    compare_symbol = st.text_input("⚖ Compare With (Optional)", "").upper()
with col2:
    period = st.selectbox("📆 Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=1)
with col3:
    interval = st.selectbox("⏳ Select Data Interval", ["1d", "1wk", "1mo"], index=0)

fetch_data = st.button("🚀 Get Stock Data")

if fetch_data and symbol:
    hist = get_stock_data(symbol, period, interval)
    if hist is not None:
        col4, col5 = st.columns([2, 1])
        with col4:
            st.write(f"### 📊 {symbol} Stock Data ({period} Period, {interval} Interval)")
            st.dataframe(hist[['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_10', 'SMA_50']])
            plot_stock_data(hist, symbol)
        with col5:
            display_stock_summary(symbol)
            display_news(symbol)
    if compare_symbol:
        compare_stocks(symbol, compare_symbol, period, interval)

# Download Data Option
if fetch_data and hist is not None:
    csv = hist.to_csv().encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name=f"{symbol}_stock_data.csv", mime='text/csv')

