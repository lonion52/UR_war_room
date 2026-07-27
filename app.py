import streamlit as st
import pandas as pd

# 1. 頁面基本設定
st.set_page_config(
    page_title="鋼鐵柚子戰情室",
    page_icon="🍐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 注入自定義 CSS 
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stApp {
            background-color: #1f1a14;
        }
        
        .fixed-header {
            background-color: #fcf8f2;
            color: #1f1a14;
            font-family: 'Space Grotesk', 'Noto Sans TC', sans-serif;
            max-width: 900px;
            margin: 0 auto 16px auto;
            border: 1px solid #1f1a14;
            padding: 16px;
            box-shadow: 2px 2px 0px #1f1a14;
        }

        .main-container {
            background-color: #f0e6d2;
            color: #1f1a14;
            font-family: 'Space Grotesk', 'Noto Sans TC', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            border: 1px solid #1f1a14;
            padding: 20px;
        }

        .swiss-card {
            background-color: #fcf8f2;
            border: 1px solid #1f1a14;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 2px 2px 0px #1f1a14;
            color: #1f1a14 !important;
        }

        .swiss-title {
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: -0.025em;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            background-color: #1f1a14;
            border: 1px solid #1f1a14;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f0e6d2;
            color: #1f1a14;
            font-family: monospace;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            border-radius: 0px;
            padding: 10px 0px;
            flex: 1;
            justify-content: center;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f1a14 !important;
            color: #f0e6d2 !important;
        }
    </style>

    <script>
        const removeBadges = () => {
            const doc = window.parent.document;
            const targetWidgets = doc.querySelectorAll('[data-testid="stStatusWidget"], .viewerBadge_container__1QSob, div[class*="viewerBadge"]');
            targetWidgets.forEach(el => el.remove());
        };
        setInterval(removeBadges, 500);
    </script>
""", unsafe_allow_html=True)

# 3. 讀取 Google 試算表資料的函數
@st.cache_data(ttl=600)
def load_data():
    try:
        gas_url = "https://script.google.com/macros/s/AKfycbxf0xiDNHzoJXBI5ZIoUfeijjPuTtpxh2BwG_NPYOqpTFrkD5_jAy72U9xeEHl5YH0U/exec"
        
        df_action = pd.read_csv(f"{gas_url}?sheet=Action")
        df_status = pd.read_csv(f"{gas_url}?sheet=State")
        df_market = pd.read_csv(f"{gas_url}?sheet=Quotes")
        
        return df_action, df_status, df_market
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_action, df_status, df_market = load_data()

# 整理狀態資料 (防呆：清除欄位名稱內的單引號與空白)
status_dict = {}
if not df_status.empty and len(df_status.columns) >= 2:
    for k, v in zip(df_status.iloc[:, 0], df_status.iloc[:, 1]):
        clean_key = str(k).strip().replace("'", "")
        status_dict[clean_key] = v

# 建立市場收盤價對應字典 (防呆：清除股票代號與日期的單引號)
price_dict = {}
latest_market_date = "2026-07-27"  

if not df_market.empty:
    last_row = df_market.iloc[-1]
    latest_market_date = str(last_row.get('日期', last_row.iloc[0] if len(last_row) > 0 else "2026-07-27")).strip().replace("'", "")
    
    for _, row in df_market.iterrows():
        sym = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).strip().replace("'", "")
        prc = row.get('收盤價', row.iloc[3] if len(row) > 3 else 0)
        try:
            price_dict[sym] = float(str(prc).replace(',', ''))
        except:
            pass

st.markdown(f"""
    <div class="fixed-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14; opacity: 0.7;">SYSTEM // DUNE EDITION</span>
                <div class="swiss-title" style="font-size: 18px; color: #1f1a14; margin-top: 2px;">鋼鐵柚子戰情室</div>
            </div>
            <div style="text-align: right;">
                <span style="display: inline-block; width: 8px; height: 8px; background-color: #556B2F; border-radius: 50%;"></span>
                <div style="font-size: 9px; font-family: monospace; color: #1f1a14; font-weight: bold; margin-top: 2px;">{latest_market_date}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

tab_action, tab_status, tab_market = st.tabs(["Action", "Dashboard", "Quotes"])

# --- 頁籤一：明日行動 (Action) ---
with tab_action:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">EXECUTIVE DIRECTIVE</div>', unsafe_allow_html=True)
    
    if df_action.empty:
        st.markdown('<div class="swiss-card">今日無待執行指令或尚無資料。</div>', unsafe_allow_html=True)
    else:
        for index, row in df_action.iterrows():
            date_val = str(row.get('日期', row.iloc[0] if len(row) > 0 else "")).replace("'", "")
            symbol_val = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).replace("'", "")
            category_val = row.get('類別', row.iloc[2] if len(row) > 2 else "")
            action_type = row.get('動作', row.iloc[3] if len(row) > 3 else "BUY")
            message_val = row.get('內容', row.iloc[4] if len(row) > 4 else "")
            
            badge_color = "#FF6B35" if "BUY" in str(action_type).upper() else "#FFD500" if "SELL" in str(action_type).upper() else "#7ba23f"
            
            st.markdown(f"""
                <div class="swiss-card" style="position: relative;">
                    <div style="position: absolute; top: 0; right: 0; background-color: {badge_color}; color: #1f1a14; font-size: 9px; font-family: monospace; padding: 2px 6px; font-weight: bold;">
                        {category_val} // {action_type}
                    </div>
                    <span style="font-size: 10px; font-family: monospace; font-weight: bold; color: #1f1a14;">TARGET: {symbol_val}</span>
                    <div style="font-size: 15px; font-weight: bold; margin: 4px 0 8px 0; color: #1f1a14;">{date_val} 執行指令</div>
                    <div style="background-color: #1f1a14; color: #f0e6d2; padding: 10px; font-family: monospace; font-size: 12px; margin-bottom: 8px;">
                        {message_val}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 頁籤二：狀態面板 (Dashboard) ---
with tab_status:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">TACTICAL MONITOR & RISK</div>', unsafe_allow_html=True)
    
    # 1. 00631L 專屬左右側部署情況 (含動態顏色標籤)
    stage_631l_left_raw = status_dict.get('00631L_左側階段', '0')
    stage_631l_right_raw = status_dict.get('00631L_右側階段', '0')
    
    try:
        left_val = int(float(str(stage_631l_left_raw).replace(',', '')))
    except:
        left_val = 0
        
    try:
        right_val = int(float(str(stage_631l_right_raw).replace(',', '')))
    except:
        right_val = 0

    # 狀態標籤邏輯判斷
    if left_val == 0 and right_val == 0:
        status_text_631l = "常態佈局中"
        status_color_631l = "#7ba23f"
        text_color_631l = "#f0e6d2"
    elif left_val > 0 and right_val == 0:
        status_text_631l = "觸發：回撤加碼"
        status_color_631l = "#FF6B35"
        text_color_631l = "#1f1a14"
    elif left_val == 0 and right_val > 0:
        status_text_631l = "觸發：動能追擊"
        status_color_631l = "#FF6B35"
        text_color_631l = "#1f1a14"
    else:
        status_text_631l = "雙向動態佈局中"
        status_color_631l = "#FF6B35"
        text_color_631l = "#1f1a14"

    st.markdown(f"""
        <div class="swiss-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold; font-size: 13px; color: #1f1a14;">00631L 戰術部署</span>
                <span style="background-color: {status_color_631l}; color: {text_color_631l}; padding: 4px 8px; font-size: 10px; font-family: monospace; font-weight: bold;">{status_text_631l}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family: monospace;">
                <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;">
                    <span style="font-size: 9px; font-weight: bold; opacity: 0.7;">左側階段 (回撤加碼)</span><br>
                    <strong style="font-size: 14px; color: #1f1a14;">Stage {left_val}</strong>
                </div>
                <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;">
                    <span style="font-size: 9px; font-weight: bold; opacity: 0.7;">右側階段 (動能追擊)</span><br>
                    <strong style="font-size: 14px; color: #1f1a14;">Stage {right_val}</strong>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 00981A 專屬轉倉狀態監控
    transfer_status_981a = status_dict.get('00981A_轉倉狀態', 0)
    try:
        transfer_code = int(float(str(transfer_status_981a).replace(',', '')))
    except:
        transfer_code = 0
        
    status_text = "已觸發清空轉倉" if transfer_code == 1 else "常態佈局中"
    status_color = "#FF6B35" if transfer_code == 1 else "#7ba23f"
    
    st.markdown(f"""
        <div class="swiss-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; font-size: 13px; color: #1f1a14;">00981A 轉倉狀態</span>
                <span style="background-color: {status_color}; color: {'#1f1a14' if transfer_code == 1 else '#f0e6d2'}; padding: 4px 8px; font-size: 10px; font-family: monospace; font-weight: bold;">{status_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. 標準回撤監控 (排除 00631L 與 00981A)
    target_symbols = [sym for sym in price_dict.keys() if sym not in ['00631L', '00981A']]
    
    for sym in target_symbols:
        name_val = ""
        for _, row in df_market.iterrows():
            row_sym = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).strip().replace("'", "")
            if row_sym == sym:
                name_val = str(row.get('股票名稱', row.iloc[2] if len(row) > 2 else ""))
                break
        
        current_price = price_dict.get(sym, 0)
        
        # 嚴謹過濾峰值價格
        peak_val_raw = status_dict.get(f'{sym}_最高價', current_price)
        try:
            peak_price = float(str(peak_val_raw).replace(',', ''))
        except:
            peak_price = current_price
            
        if peak_price <= 0 and current_price > 0:
            peak_price = current_price
            
        if peak_price > 0:
            drawdown_pct = ((current_price - peak_price) / peak_price) * 100
        else:
            drawdown_pct = 0.0
            
        bar_width = max(0, min(100, 100 + drawdown_pct))

        st.markdown(f"""
            <div class="swiss-card">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
                    {sym} // {name_val} 回撤監控
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; font-family: monospace;">
                    <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;">
                        <span style="font-size: 9px; font-weight: bold; opacity: 0.7;">CURRENT PRICE</span><br>
                        <strong style="font-size: 15px; color: #1f1a14;">{current_price}</strong>
                    </div>
                    <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;">
                        <span style="font-size: 9px; font-weight: bold; opacity: 0.7;">PEAK PRICE</span><br>
                        <strong style="font-size: 15px; color: #1f1a14;">{peak_price}</strong>
                    </div>
                </div>
                <div style="font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 4px; display: flex; justify-content: space-between;">
                    <span>高點回撤幅度</span>
                    <span style="color: {'#FF6B35' if drawdown_pct < -5 else '#1f1a14'};">{drawdown_pct:.2f}%</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #e4dac6; border: 1px solid #1f1a14; overflow: hidden;">
                    <div style="width: {bar_width}%; height: 100%; background-color: #1f1a14;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 頁籤三：報價紀錄 (Quotes) ---
with tab_market:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">MARKET DATA BASELINE</div>', unsafe_allow_html=True)
    
    if df_market.empty:
        st.markdown('<div class="swiss-card">尚無歷史報價資料。</div>', unsafe_allow_html=True)
    else:
        # 比對時強制清理 df_market 內的日期單引號
        df_market_clean_date = df_market.iloc[:, 0].astype(str).str.replace("'", "").str.strip()
        df_latest_market = df_market[df_market_clean_date == latest_market_date]
        
        if df_latest_market.empty:
            st.markdown('<div class="swiss-card">本日尚無報價資料。</div>', unsafe_allow_html=True)
        else:
            for index, row in df_latest_market.iterrows():
                date_m = str(row.get('日期', row.iloc[0] if len(row) > 0 else "")).replace("'", "")
                symbol_m = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).replace("'", "")
                name_m = str(row.get('股票名稱', row.iloc[2] if len(row) > 2 else ""))
                price_m = str(row.get('收盤價', row.iloc[3] if len(row) > 3 else ""))
                
                st.markdown(f"""
                    <div class="swiss-card" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px;">
                        <div>
                            <span style="font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">{date_m}</span>
                            <div style="font-weight: bold; font-size: 13px; font-family: monospace; color: #1f1a14;">{symbol_m} // {name_m}</div>
                        </div>
                        <div style="font-size: 16px; font-weight: bold; font-family: monospace; color: #1f1a14;">
                            {price_m}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("""
    <div style="border-top: 1px solid #1f1a14; margin-top: 20px; padding-top: 10px; display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">
        <span>THEME: DUNE & SWISS</span>
        <span>PAGE 01/01</span>
    </div>
</div>
""", unsafe_allow_html=True)