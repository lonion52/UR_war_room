import streamlit as st
import pandas as pd
import requests
import io

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
        
        /* 🍐 戰術同步按鈕專屬設計 */
        div[data-testid="stButton"] > button {
            background-color: #fcf8f2;
            color: #1f1a14;
            border: 1px solid #1f1a14;
            border-radius: 0px;
            box-shadow: 2px 2px 0px #1f1a14;
            font-family: monospace;
            font-weight: bold;
            font-size: 14px;
            padding: 4px 16px;
            transition: all 0.15s ease;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #f0e6d2;
            color: #1f1a14;
            border: 1px solid #1f1a14;
        }
        div[data-testid="stButton"] > button:active {
            background-color: #FF6B35;
            color: #1f1a14;
            box-shadow: 0px 0px 0px #1f1a14;
            transform: translate(2px, 2px);
        }
        div[data-testid="stButton"] > button:focus:not(:active) {
            border: 1px solid #1f1a14;
            color: #1f1a14;
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
@st.cache_data(ttl=60)
def load_data():
    try:
        # ⚠️ 請確保這裡是正確的 GAS Web App 網址
        gas_url = "https://script.google.com/macros/s/AKfycbxf0xiDNHzoJXBI5ZIoUfeijjPuTtpxh2BwG_NPYOqpTFrkD5_jAy72U9xeEHl5YH0U/exec"
        res_action = requests.get(f"{gas_url}?sheet=Action", allow_redirects=True)
        df_action = pd.read_csv(io.StringIO(res_action.text), dtype=str).fillna("") if res_action.status_code == 200 else pd.DataFrame()
        res_market = requests.get(f"{gas_url}?sheet=Quotes", allow_redirects=True)
        df_market = pd.read_csv(io.StringIO(res_market.text), dtype=str).fillna("") if res_market.status_code == 200 else pd.DataFrame()
        res_status = requests.get(f"{gas_url}?sheet=State", allow_redirects=True)
        df_status = pd.read_csv(io.StringIO(res_status.text), dtype=str, header=None).fillna("") if res_status.status_code == 200 else pd.DataFrame()
        return df_action, df_status, df_market
    except Exception as e:
        st.error(f"連線至 Google 試算表失敗: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_action, df_status, df_market = load_data()

status_dict = {}
if not df_status.empty and len(df_status.columns) >= 2:
    for k, v in zip(df_status.iloc[:, 0], df_status.iloc[:, 1]):
        clean_key = str(k).strip().replace("'", "")
        status_dict[clean_key] = v

price_dict = {}
prev_price_dict = {}
latest_market_date = "2026-07-28"  

if not df_market.empty:
    last_row = df_market.iloc[-1]
    latest_market_date = str(last_row.get('日期', last_row.iloc[0] if len(last_row) > 0 else "2026-07-28")).strip().replace("'", "")
    
    for _, row in df_market.iterrows():
        row_date = str(row.get('日期', row.iloc[0] if len(row) > 0 else "")).strip().replace("'", "")
        sym = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).strip().replace("'", "")
        prc = row.get('收盤價', row.iloc[3] if len(row) > 3 else 0)
        try:
            prc_float = float(str(prc).replace(',', ''))
            if row_date == latest_market_date: price_dict[sym] = prc_float
            else: prev_price_dict[sym] = prc_float
        except: pass

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

col_space, col_btn = st.columns([5, 2])
with col_btn:
    st.button("🍐 SYNC", on_click=load_data.clear, use_container_width=True)

tab_market, tab_status, tab_action = st.tabs(["Quotes", "Dashboard", "Action"])

with tab_market:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">MARKET DATA BASELINE</div>', unsafe_allow_html=True)
    if df_market.empty:
        st.markdown('<div class="swiss-card">尚無歷史報價資料。</div>', unsafe_allow_html=True)
    else:
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
                change_m = str(row.get('漲跌', str(row.get('漲跌幅', row.iloc[4] if len(row) > 4 else ""))))
                if change_m == "nan" or change_m == "休市" or change_m == "停牌/無資料": change_m = ""
                
                price_color = "#1f1a14" 
                try:
                    curr_prc = float(price_m.replace(',', ''))
                    if symbol_m in prev_price_dict:
                        prev_prc = prev_price_dict[symbol_m]
                        if curr_prc > prev_prc: price_color = "#FF6B35" 
                        elif curr_prc < prev_prc: price_color = "#7ba23f" 
                except: pass
                
                st.markdown(f"""
                    <div class="swiss-card" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px;">
                        <div>
                            <span style="font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">{date_m}</span>
                            <div style="font-weight: bold; font-size: 13px; font-family: monospace; color: #1f1a14;">{symbol_m} // {name_m}</div>
                        </div>
                        <div style="font-size: 16px; font-weight: bold; font-family: monospace; color: {price_color}; text-align: right;">
                            {price_m}<br><span style="font-size: 10px; opacity: 0.8;">{change_m}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tab_status:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">TACTICAL MONITOR & RISK</div>', unsafe_allow_html=True)
    
    ordered_symbols = ["^TWII", "0050", "00631L", "2330", "3711", "00981A"]
    for s in price_dict.keys():
        if s not in ordered_symbols: ordered_symbols.append(s)

    for sym in ordered_symbols:
        if sym not in price_dict: continue
        current_price = price_dict.get(sym, 0)
        
        name_val = ""
        for _, row in df_market.iterrows():
            row_sym = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).strip().replace("'", "")
            if row_sym == sym:
                name_val = str(row.get('股票名稱', row.iloc[2] if len(row) > 2 else ""))
                break
        
        peak_val_raw = current_price
        for k, v in status_dict.items():
            if sym in k and "最高價" in k:
                peak_val_raw = v
                break
                
        try: peak_price = float(str(peak_val_raw).replace(',', ''))
        except: peak_price = current_price
        if peak_price <= 0 and current_price > 0: peak_price = current_price
        drawdown_pct = ((current_price - peak_price) / peak_price) * 100 if peak_price > 0 else 0.0
        bar_width = max(0, min(100, 100 + drawdown_pct))

        if sym == "^TWII":
            st.markdown(f"""
                <div class="swiss-card" style="border: 2px solid #1f1a14; background-color: #f0e6d2;">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">大盤天氣預報 // {name_val}</div>
                    <div style="background-color: #fcf8f2; border: 1px solid #1f1a14; padding: 16px; text-align: center; font-family: monospace;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">CURRENT POINT</span><br><strong style="font-size: 26px; color: #1f1a14;">{current_price:,.2f}</strong></div>
                </div>
            """, unsafe_allow_html=True)

        elif sym == "0050":
            try: stage_0050 = int(float(str(status_dict.get('元大0050_回撤階段', '0'))))
            except: stage_0050 = 0
            
            p90 = peak_price * 0.9
            p80 = peak_price * 0.8
            p70 = peak_price * 0.7
            s90 = "已到達" if current_price <= p90 else "未到達"
            s80 = "已到達" if current_price <= p80 else "未到達"
            s70 = "已到達" if current_price <= p70 else "未到達"
            
            stage_color = "#FF6B35" if stage_0050 > 0 else "#7ba23f"
            
            st.markdown(f"""
                <div class="swiss-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f1a14; margin-bottom: 10px; padding-bottom: 4px;">
                        <div style="font-weight: bold; font-size: 14px; color: #1f1a14;">{sym} // {name_val} 回撤監控</div>
                        <div style="background-color: {stage_color}; color: #f0e6d2; font-size: 10px; padding: 2px 6px; font-weight: bold; font-family: monospace;">STAGE: {stage_0050}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; font-family: monospace;">
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">CURRENT PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{current_price}</strong></div>
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">PEAK PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{peak_price}</strong></div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px; font-family: monospace; text-align: center;">
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">最高價 × 0.9</span><br><strong style="font-size: 14px; color: #1f1a14;">{p90:.2f}</strong><br><span style="font-size: 12px; font-weight: bold; color: {'#FF6B35' if s90 == '已到達' else '#1f1a14'};">{s90}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">最高價 × 0.8</span><br><strong style="font-size: 14px; color: #1f1a14;">{p80:.2f}</strong><br><span style="font-size: 12px; font-weight: bold; color: {'#FF6B35' if s80 == '已到達' else '#1f1a14'};">{s80}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">最高價 × 0.7</span><br><strong style="font-size: 14px; color: #1f1a14;">{p70:.2f}</strong><br><span style="font-size: 12px; font-weight: bold; color: {'#FF6B35' if s70 == '已到達' else '#1f1a14'};">{s70}</span></div>
                    </div>
                    <div style="font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 4px; display: flex; justify-content: space-between;"><span>高點回撤幅度</span><span style="color: {'#FF6B35' if drawdown_pct < -5 else '#1f1a14'};">{drawdown_pct:.2f}%</span></div>
                    <div style="width: 100%; height: 8px; background-color: #e4dac6; border: 1px solid #1f1a14; overflow: hidden;"><div style="width: {bar_width}%; height: 100%; background-color: #1f1a14;"></div></div>
                </div>
            """, unsafe_allow_html=True)

        elif sym in ["2330", "3711"]:
            try: stage_sat = int(float(str(status_dict.get(f'{sym}_回撤階段', '0'))))
            except: stage_sat = 0
            
            p90 = peak_price * 0.90
            p85 = peak_price * 0.85
            s90 = "已到達" if current_price <= p90 else "未到達"
            s85 = "已到達" if current_price <= p85 else "未到達"
            
            stage_color = "#FF6B35" if stage_sat > 0 else "#7ba23f"

            st.markdown(f"""
                <div class="swiss-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f1a14; margin-bottom: 10px; padding-bottom: 4px;">
                        <div style="font-weight: bold; font-size: 14px; color: #1f1a14;">{sym} // {name_val} 衛星監控</div>
                        <div style="background-color: {stage_color}; color: #f0e6d2; font-size: 10px; padding: 2px 6px; font-weight: bold; font-family: monospace;">STAGE: {stage_sat}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; font-family: monospace;">
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">CURRENT PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{current_price}</strong></div>
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">PEAK PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{peak_price}</strong></div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; font-family: monospace; text-align: center;">
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">最高價 × 0.90 (-10%)</span><br><strong style="font-size: 14px; color: #1f1a14;">{p90:.2f}</strong><br><span style="font-size: 12px; font-weight: bold; color: {'#FF6B35' if s90 == '已到達' else '#1f1a14'};">{s90}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">最高價 × 0.85 (-15%)</span><br><strong style="font-size: 14px; color: #1f1a14;">{p85:.2f}</strong><br><span style="font-size: 12px; font-weight: bold; color: {'#FF6B35' if s85 == '已到達' else '#1f1a14'};">{s85}</span></div>
                    </div>
                    <div style="font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 4px; display: flex; justify-content: space-between;"><span>高點回撤幅度</span><span style="color: {'#FF6B35' if drawdown_pct < -5 else '#1f1a14'};">{drawdown_pct:.2f}%</span></div>
                    <div style="width: 100%; height: 8px; background-color: #e4dac6; border: 1px solid #1f1a14; overflow: hidden;"><div style="width: {bar_width}%; height: 100%; background-color: #1f1a14;"></div></div>
                </div>
            """, unsafe_allow_html=True)

        elif sym == "00631L":
            try: left_val = int(float(str(status_dict.get('00631L_左側階段', '0')).replace(',', '')))
            except: left_val = 0
            try: right_val = int(float(str(status_dict.get('00631L_右側階段', '0')).replace(',', '')))
            except: right_val = 0
            
            right_base = float(status_dict.get('00631L_右側基準價', peak_price))
            if right_base == 0: right_base = peak_price
            total_buys_631l = left_val + right_val
            
            inv_slots = []
            for _ in range(left_val): inv_slots.append("防禦 (回撤)")
            for _ in range(right_val): inv_slots.append("進攻 (動能)")
            while len(inv_slots) < 3: inv_slots.append("空缺")
            inv_slots = inv_slots[:3]
            
            inv_html = ""
            for s in inv_slots:
                bg_color = "#FF6B35" if s != "空缺" else "#e4dac6"
                text_color = "#1f1a14" if s != "空缺" else "#a09a8f"
                inv_html += f'<div style="background-color: {bg_color}; color: {text_color}; border: 1px solid #1f1a14; text-align: center; padding: 8px; font-weight: bold; font-size: 12px;">{s}</div>'

            L_85_price = peak_price * 0.85
            L_80_price = peak_price * 0.80
            L_70_price = peak_price * 0.70
            L_85 = "已到達" if current_price <= L_85_price else "未到達"
            L_80 = "已到達" if current_price <= L_80_price else "未到達"
            L_70 = "已到達" if current_price <= L_70_price else "未到達"
            
            R_10_price = right_base * 1.0
            R_11_price = right_base * 1.1
            R_12_price = right_base * 1.2
            R_10 = "已到達" if current_price >= R_10_price else "未到達"
            R_11 = "已到達" if current_price >= R_11_price else "未到達"
            R_12 = "已到達" if current_price >= R_12_price else "未到達"

            st.markdown(f"""
                <div class="swiss-card">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">00631L 戰術部署</div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; font-family: monospace;">
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">CURRENT PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{current_price}</strong></div>
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">PEAK PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{peak_price}</strong></div>
                    </div>

                    <div style="font-size: 11px; font-weight: bold; font-family: monospace; margin-bottom: 6px;">庫存狀態 (進度 {total_buys_631l}/3)</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; font-family: monospace;">{inv_html}</div>
                    
                    <div style="background-color: #1f1a14; color: #f0e6d2; text-align: center; padding: 6px; font-weight: bold; font-size: 12px; margin-bottom: 8px;">防禦 (左側回撤)</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; font-family: monospace; text-align: center;">
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">高點 × 0.85</span><br><strong style="font-size: 14px; color: #1f1a14;">{L_85_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if L_85 == '已到達' else '#1f1a14'};">{L_85}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">高點 × 0.80</span><br><strong style="font-size: 14px; color: #1f1a14;">{L_80_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if L_80 == '已到達' else '#1f1a14'};">{L_80}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">高點 × 0.70</span><br><strong style="font-size: 14px; color: #1f1a14;">{L_70_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if L_70 == '已到達' else '#1f1a14'};">{L_70}</span></div>
                    </div>
                    
                    <div style="background-color: #1f1a14; color: #f0e6d2; text-align: center; padding: 6px; font-weight: bold; font-size: 12px; margin-bottom: 8px;">進攻 (右側動能)</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px; font-family: monospace; text-align: center;">
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">基準點 × 1.0</span><br><strong style="font-size: 14px; color: #1f1a14;">{R_10_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if R_10 == '已到達' else '#1f1a14'};">{R_10}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">基準點 × 1.1</span><br><strong style="font-size: 14px; color: #1f1a14;">{R_11_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if R_11 == '已到達' else '#1f1a14'};">{R_11}</span></div>
                        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 11px; font-weight: bold; opacity: 0.7;">基準點 × 1.2</span><br><strong style="font-size: 14px; color: #1f1a14;">{R_12_price:.2f}</strong><br><span style="font-size: 11px; font-weight: bold; color: {'#FF6B35' if R_12 == '已到達' else '#1f1a14'};">{R_12}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        elif sym == "00981A":
            try: transfer_code = int(float(str(status_dict.get('00981A_轉倉狀態', 0)).replace(',', '')))
            except: transfer_code = 0
            status_text = "已觸發清空轉倉" if transfer_code == 1 else "常態佈局中"
            status_color = "#FF6B35" if transfer_code == 1 else "#7ba23f"
            st.markdown(f"""
                <div class="swiss-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 14px; color: #1f1a14;">00981A 轉倉狀態</span>
                        <span style="background-color: {status_color}; color: {'#1f1a14' if transfer_code == 1 else '#f0e6d2'}; padding: 4px 8px; font-size: 11px; font-family: monospace; font-weight: bold;">{status_text}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
                <div class="swiss-card">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">{sym} // {name_val} 回撤監控</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; font-family: monospace;">
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">CURRENT PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{current_price}</strong></div>
                        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 8px;"><span style="font-size: 9px; font-weight: bold; opacity: 0.7;">PEAK PRICE</span><br><strong style="font-size: 15px; color: #1f1a14;">{peak_price}</strong></div>
                    </div>
                    <div style="font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 4px; display: flex; justify-content: space-between;"><span>高點回撤幅度</span><span style="color: {'#FF6B35' if drawdown_pct < -5 else '#1f1a14'};">{drawdown_pct:.2f}%</span></div>
                    <div style="width: 100%; height: 8px; background-color: #e4dac6; border: 1px solid #1f1a14; overflow: hidden;"><div style="width: {bar_width}%; height: 100%; background-color: #1f1a14;"></div></div>
                </div>
            """, unsafe_allow_html=True)

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
            if symbol_val == "PORTFOLIO" or action_type == "CHECK":
                badge_color = "#4a69bd"
                symbol_val = "系統健診"
            st.markdown(f"""
                <div class="swiss-card" style="position: relative;">
                    <div style="position: absolute; top: 0; right: 0; background-color: {badge_color}; color: #1f1a14; font-size: 9px; font-family: monospace; padding: 2px 6px; font-weight: bold;">{category_val} // {action_type}</div>
                    <span style="font-size: 10px; font-family: monospace; font-weight: bold; color: #1f1a14;">TARGET: {symbol_val}</span>
                    <div style="font-size: 15px; font-weight: bold; margin: 4px 0 8px 0; color: #1f1a14;">{date_val} 執行指令</div>
                    <div style="background-color: #1f1a14; color: #f0e6d2; padding: 10px; font-family: monospace; font-size: 12px; margin-bottom: 8px; white-space: pre-line;">{message_val}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("""
    <div style="border-top: 1px solid #1f1a14; margin-top: 20px; padding-top: 10px; display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">
        <span>THEME: DUNE & SWISS</span>
        <span>PAGE 01/01</span>
    </div>
</div>
""", unsafe_allow_html=True)