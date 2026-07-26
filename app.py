import streamlit as st
import pandas as pd

# 1. 頁面基本設定
st.set_page_config(
    page_title="鋼鐵柚子戰情室",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 注入自定義 CSS (修正文字顏色為深色，確保在沙丘色底清晰可見)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stApp {
            background-color: #1f1a14;
        }
        
        .main-container {
            background-color: #f0e6d2;
            color: #1f1a14;
            font-family: 'Space Grotesk', 'Noto Sans TC', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            border: 1px solid #1f1a14;
            padding: 24px;
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
""", unsafe_allow_html=True)

# 3. 讀取 Google 試算表資料的函數 (透過 GAS 網頁應用程式)
@st.cache_data(ttl=600)
def load_data():
    try:
        gas_url = "https://script.google.com/macros/s/AKfycbyZwj4KHu0BmmAfc3w8MOVxe3yh9rELyxUez_pWosUsMFM3IEqg9hK-F2p2BaHGJf5v/exec"
        
        df_action = pd.read_csv(f"{gas_url}?sheet=Action")
        df_status = pd.read_csv(f"{gas_url}?sheet=State")
        df_market = pd.read_csv(f"{gas_url}?sheet=Quotes")
        
        return df_action, df_status, df_market
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 載入資料
df_action, df_status, df_market = load_data()

# 將狀態面板轉換成字典
status_dict = {}
if not df_status.empty and len(df_status.columns) >= 2:
    status_dict = dict(zip(df_status.iloc[:, 0], df_status.iloc[:, 1]))

last_sync_time = status_dict.get('最後更新時間', '2026-07-27 17:05:00')

# 4. 前端排版主體
st.markdown('<div class="main-container">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<span style="font-size: 10px; font-family: monospace; opacity: 0.8;">SYSTEM // DUNE EDITION</span>', unsafe_allow_html=True)
    st.markdown('<h1 class="swiss-title" style="font-size: 20px; margin: 0; color: #1f1a14;">鋼鐵柚子戰情室</h1>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align: right;"><span style="display: inline-block; width: 8px; height: 8px; background-color: #556B2F; border-radius: 50%;"></span><br><span style="font-size: 9px; font-family: monospace; color: #1f1a14; font-weight: bold;">{str(last_sync_time).split(" ")[-1]}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #1f1a14; margin: 12px 0;'>", unsafe_allow_html=True)

tab_action, tab_status, tab_market = st.tabs(["Action", "Dashboard", "Quotes"])

# --- 頁籤一：明日行動 (Action) ---
with tab_action:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin-bottom: 12px; font-weight: bold;">EXECUTIVE DIRECTIVE</div>', unsafe_allow_html=True)
    
    if df_action.empty:
        st.markdown('<div class="swiss-card">今日無待執行指令或尚無資料。</div>', unsafe_allow_html=True)
    else:
        for index, row in df_action.iterrows():
            date_val = row.get('日期', row.iloc[0] if len(row) > 0 else "")
            symbol_val = row.get('股票代號', row.iloc[1] if len(row) > 1 else "")
            category_val = row.get('類別', row.iloc[2] if len(row) > 2 else "")
            action_type = row.get('動作', row.iloc[3] if len(row) > 3 else "BUY")
            message_val = row.get('內容', row.iloc[4] if len(row) > 4 else "")
            
            badge_color = "#FF6B35" if str(action_type).upper() == "BUY" else "#FFD500"
            
            st.markdown(f"""
                <div class="swiss-card" style="position: relative;">
                    <div style="position: absolute; top: 0; right: 0; background-color: {badge_color}; color: #1f1a14; font-size: 9px; font-family: monospace; padding: 2px 6px; font-weight: bold;">
                        {category_val} // {action_type}
                    </div>
                    <span style="font-size: 10px; font-family: monospace; font-weight: bold;">TARGET: {symbol_val}</span>
                    <div style="font-size: 15px; font-weight: bold; margin: 4px 0 8px 0; color: #1f1a14;">{date_val} 執行指令</div>
                    <div style="background-color: #1f1a14; color: #f0e6d2; padding: 10px; font-family: monospace; font-size: 12px; margin-bottom: 8px;">
                        {message_val}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 頁籤二：狀態面板 (Dashboard) ---
with tab_status:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin-bottom: 12px; font-weight: bold;">QUANTITATIVE STATE</div>', unsafe_allow_html=True)
    
    peak_0050 = status_dict.get('0050_最高價', 195.50)
    stage_0050 = status_dict.get('0050_回撤階段', 0)
    left_00631l = status_dict.get('00631L_左側階段', 2)
    
    st.markdown(f"""
        <div class="swiss-card">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                <span style="font-weight: bold; font-size: 13px; color: #1f1a14;">0050 高點回撤監控</span>
                <span style="background-color: #FFD500; padding: 2px 6px; font-size: 10px; font-family: monospace; font-weight: bold; color: #1f1a14;">STAGE {stage_0050}/3</span>
            </div>
            <div style="font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 8px; color: #1f1a14;">
                PEAK: {peak_0050}
            </div>
            <div style="width: 100%; height: 10px; background-color: #e4dac6; border: 1px solid #1f1a14; overflow: hidden;">
                <div style="width: 85%; height: 100%; background-color: #1f1a14;"></div>
            </div>
        </div>

        <div class="swiss-card">
            <div style="font-weight: bold; font-size: 13px; margin-bottom: 8px; color: #1f1a14;">00631L 戰術布署</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family: monospace; font-size: 11px;">
                <div style="background-color: #fcf8f2; border: 1px solid #1f1a14; padding: 8px;">
                    <span style="font-size: 9px; color: #1f1a14; font-weight: bold;">LEFT-SIDE</span><br>
                    <strong style="color: #FF6B35; font-size: 13px;">STAGE {left_00631l}</strong>
                </div>
                <div style="background-color: #fcf8f2; border: 1px solid #1f1a14; padding: 8px;">
                    <span style="font-size: 9px; color: #1f1a14; font-weight: bold;">RIGHT-SIDE</span><br>
                    <strong style="color: #1f1a14; font-size: 13px; opacity: 0.5;">INACTIVE</strong>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 頁籤三：報價紀錄 (Quotes) ---
with tab_market:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin-bottom: 12px; font-weight: bold;">MARKET DATA BASELINE</div>', unsafe_allow_html=True)
    
    if df_market.empty:
        st.markdown('<div class="swiss-card">尚無歷史報價資料。</div>', unsafe_allow_html=True)
    else:
        for index, row in df_market.iterrows():
            date_m = row.get('日期', row.iloc[0] if len(row) > 0 else "")
            symbol_m = row.get('股票代號', row.iloc[1] if len(row) > 1 else "")
            name_m = row.get('股票名稱', row.iloc[2] if len(row) > 2 else "")
            price_m = row.get('收盤價', row.iloc[3] if len(row) > 3 else "")
            
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
    <div style="border-top: 1px solid #1f1a14; margin-top: 20px; padding-top: 10px; display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; font-weight: bold;">
        <span>THEME: DUNE & SWISS</span>
        <span>PAGE 01/01</span>
    </div>
</div>
""", unsafe_allow_html=True)