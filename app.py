import streamlit as st
import requests
import json
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
    }
    .metric-value { font-size: 28px; font-weight: 900; color: #00d4ff; margin: 0; }
    .metric-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 2px; margin: 0; }
    .price-display {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        border: 2px solid #00d4ff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_stock_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1mo"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        result = data["chart"]["result"][0]
        meta = result["meta"]
        closes = result["indicators"]["quote"][0]["close"]
        timestamps = result["timestamp"]
        
        current_price = meta.get("regularMarketPrice", 0)
        prev_close = meta.get("chartPreviousClose", 0)
        week_high = meta.get("fiftyTwoWeekHigh", 0)
        week_low = meta.get("fiftyTwoWeekLow", 0)
        company_name = meta.get("longName", meta.get("shortName", ticker))
        
        return {
            "name": company_name,
            "price": current_price,
            "prev_close": prev_close,
            "week_high": week_high,
            "week_low": week_low,
            "closes": closes,
        }
    except Exception as e:
        return None

def get_ai_analysis(company_name, current_price, change_percent, week_high, week_low):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a senior equity analyst. Analyze this stock:
    
    Company: {company_name}
    Current Price: ₹{current_price}
    Today's Change: {change_percent:.2f}%
    52-Week High: ₹{week_high}
    52-Week Low: ₹{week_low}
    
    Provide:
    1. MARKET SENTIMENT (Bullish/Bearish/Neutral with reasoning)
    2. KEY OBSERVATIONS (3 bullet points)
    3. RISK FACTORS (2 key risks)
    4. OPPORTUNITY (1 key opportunity)
    5. VERDICT (Buy/Hold/Sell with one sentence explanation)
    
    Be concise and professional.
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
    return "Unable to generate analysis."

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
    ticker_input = st.text_input("", placeholder="Enter ticker e.g. TCS.NS, RELIANCE.NS, INFY.NS", label_visibility="collapsed")
with col2:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

st.markdown("<p style='color: #555; font-size: 12px;'>💡 Use .NS suffix — e.g. TCS.NS, HDFCBANK.NS, WIPRO.NS, TATAMOTORS.NS</p>", unsafe_allow_html=True)

if analyze_btn and ticker_input:
    with st.spinner("Fetching live market data... 📡"):
        stock = get_stock_data(ticker_input.upper())
    
    if stock:
        current_price = stock["price"]
        prev_close = stock["prev_close"]
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close else 0
        change_symbol = "▲" if change >= 0 else "▼"
        change_color = "#00ff88" if change >= 0 else "#ff4444"

        st.markdown(f"""
        <div class='price-display'>
            <p style='font-size: 32px; font-weight: 900; color: #ffffff; margin: 0;'>{stock["name"]}</p>
            <p style='font-size: 64px; font-weight: 900; color: #00d4ff; margin: 10px 0;'>₹{current_price:,.2f}</p>
            <p style='font-size: 24px; font-weight: 700; color: {change_color};'>{change_symbol} ₹{abs(change):,.2f} ({change_percent:+.2f}%)</p>
            <p style='color: #555; font-size: 12px; margin: 5px 0;'>NSE/BSE • Live Data</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>52W High</p>
                <p class='metric-value'>₹{stock["week_high"]:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-label'>52W Low</p>
                <p class='metric-value'>₹{stock["week_low"]:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: #00d4ff; font-size: 18px; font-weight: 800; letter-spacing: 3px;'>📊 30-DAY PRICE CHART</p>", unsafe_allow_html=True)
        
        closes = [c for c in stock["closes"] if c is not None]
        st.line_chart(closes)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: #ffd700; font-size: 18px; font-weight: 800; letter-spacing: 3px;'>🤖 AI MARKET ANALYSIS</p>", unsafe_allow_html=True)
        
        with st.spinner("Generating AI insights... 🧠"):
            analysis = get_ai_analysis(
                stock["name"], current_price, change_percent,
                stock["week_high"], stock["week_low"]
            )
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                    border-left: 4px solid #ffd700; 
                    border-radius: 15px; 
                    padding: 25px; 
                    color: #ddd;
                    line-height: 1.8;'>
            {analysis.replace(chr(10), "<br>")}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ Stock not found! Please check the ticker and try again.")

elif analyze_btn:
    st.warning("⚠️ Please enter a stock ticker!")