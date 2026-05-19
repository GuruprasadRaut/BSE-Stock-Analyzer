import streamlit as st
import yfinance as yf
import requests
import json
import os
from datetime import datetime, timedelta

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Custom CSS for premium UI
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .stApp { background-color: #0a0a0a; }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 900;
        color: #00d4ff;
        margin: 0;
    }
    
    .metric-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }
    
    .price-display {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        border: 2px solid #00d4ff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        margin: 20px 0;
    }
    
    .company-name {
        font-size: 32px;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
    }
    
    .current-price {
        font-size: 64px;
        font-weight: 900;
        color: #00d4ff;
        margin: 10px 0;
    }
    
    .price-change-positive {
        font-size: 24px;
        font-weight: 700;
        color: #00ff88;
    }
    
    .price-change-negative {
        font-size: 24px;
        font-weight: 700;
        color: #ff4444;
    }
    
    .ai-section {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #gold;
        border-left: 4px solid #ffd700;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #ffd700;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")
        return info, hist
    except:
        return None, None

def get_ai_analysis(company_name, current_price, change_percent, market_cap, pe_ratio, week_high, week_low):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a senior equity analyst at a top investment bank. Analyze this BSE listed stock:
    
    Company: {company_name}
    Current Price: ₹{current_price}
    Today's Change: {change_percent}%
    Market Cap: ₹{market_cap}
    P/E Ratio: {pe_ratio}
    52-Week High: ₹{week_high}
    52-Week Low: ₹{week_low}
    
    Provide a concise analysis with:
    1. MARKET SENTIMENT (Bullish/Bearish/Neutral with reasoning)
    2. KEY OBSERVATIONS (3 bullet points about the stock's current position)
    3. RISK FACTORS (2 key risks)
    4. OPPORTUNITY (1 key opportunity)
    5. VERDICT (Buy/Hold/Sell with one sentence explanation)
    
    Keep it professional, concise and insightful. No financial advice disclaimer needed.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return "Unable to generate analysis at this time."

# Main App
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 48px; font-weight: 900; color: #00d4ff; margin: 0;'>📈 BSE Stock Analyzer</h1>
    <p style='color: #888; font-size: 16px; letter-spacing: 3px; text-transform: uppercase;'>AI-Powered Market Intelligence</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("", placeholder="Enter BSE Ticker (e.g. RELIANCE.NS, TCS.NS, INFY.NS)", label_visibility="collapsed")
with col2:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

st.markdown("""
<p style='color: #555; font-size: 12px;'>
💡 Add .NS for NSE/BSE stocks — e.g. RELIANCE.NS, TCS.NS, HDFCBANK.NS, WIPRO.NS, TATAMOTORS.NS
</p>
""", unsafe_allow_html=True)

if analyze_btn and ticker_input:
    with st.spinner("Fetching live market data... 📡"):
        info, hist = get_stock_data(ticker_input.upper())
    
    if info and hist is not None and not hist.empty:
        # Extract data
        company_name = info.get('longName', ticker_input)
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        prev_close = info.get('previousClose', 0)
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close else 0
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('trailingPE', 0)
        week_high = info.get('fiftyTwoWeekHigh', 0)
        week_low = info.get('fiftyTwoWeekLow', 0)
        volume = info.get('volume', 0)
        dividend_yield = info.get('dividendYield', 0)

        # Price Display
        change_class = "price-change-positive" if change >= 0 else "price-change-negative"
        change_symbol = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div class='price-display'>
            <p class='company-name'>{company_name}</p>
            <p class='current-price'>₹{current_price:,.2f}</p>
            <p class='{change_class}'>{change_symbol} ₹{abs(change):,.2f} ({change_percent:+.2f}%)</p>
            <p style='color: #555; font-size: 12px; margin: 5px 0;'>BSE • Live Data</p>
        </div>
        """, unsafe_allow_html=True)

        # Metrics Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>Market Cap</p>
                <p class='metric-value'>₹{market_cap/1e9:.1f}B</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>P/E Ratio</p>
                <p class='metric-value'>{pe_ratio:.1f}x</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>52W High</p>
                <p class='metric-value'>₹{week_high:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>52W Low</p>
                <p class='metric-value'>₹{week_low:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Price Chart
        st.markdown("<p class='section-title' style='color: #00d4ff;'>📊 30-DAY PRICE CHART</p>", unsafe_allow_html=True)
        st.line_chart(hist['Close'], use_container_width=True)

        # AI Analysis
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='section-title' style='color: #ffd700; font-size: 20px; font-weight: 800; letter-spacing: 3px;'>🤖 AI MARKET ANALYSIS</p>", unsafe_allow_html=True)
        
        with st.spinner("Generating AI insights... 🧠"):
            analysis = get_ai_analysis(
                company_name, current_price, change_percent,
                f"{market_cap/1e9:.1f}B", pe_ratio, week_high, week_low
            )
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border-left: 4px solid #ffd700; 
                    border-radius: 15px; 
                    padding: 25px; 
                    margin: 10px 0;
                    color: #ddd;
                    line-height: 1.8;'>
            {analysis.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ Stock not found! Please check the ticker symbol and try again.")

elif analyze_btn and not ticker_input:
    st.warning("⚠️ Please enter a stock ticker!")