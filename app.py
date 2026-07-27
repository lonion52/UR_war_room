import streamlit as st
import pandas as pd
import json

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
        
        df_action = pd.read_csv(f"{gas_url}?sheet=Action", dtype=str).fillna("")
        df_market = pd.read_csv(f"{gas_url}?sheet=Quotes", dtype=str).fillna("")
        df_status = pd.read_csv(f"{gas_url}?sheet=State", dtype=str, header=None).fillna("")
        
        return df_action, df_status, df_market
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_action, df_status, df_market = load_data()

# 整理狀態資料 
status_dict = {}
if not df_status.empty and len(df_status.columns) >= 2:
    for k, v in zip(df_status.iloc[:, 0], df_status.iloc[:, 1]):
        clean_key = str(k).strip().replace("'", "")
        status_dict[clean_key] = v

# 建立市場收盤價對應字典與前一次收盤價對應字典
price_dict = {}
prev_price_dict = {}
latest_market_date = "2026-07-27"  

if not df_market.empty:
    last_row = df_market.iloc[-1]
    latest_market_date = str(last_row.get('日期', last_row.iloc[0] if len(last_row) > 0 else "2026-07-27")).strip().replace("'", "")
    
    for _, row in df_market.iterrows():
        row_date = str(row.get('日期', row.iloc[0] if len(row) > 0 else "")).strip().replace("'", "")
        sym = str(row.get('股票代號', row.iloc[1] if len(row) > 1 else "")).strip().replace("'", "")
        prc = row.get('收盤價', row.iloc[3] if len(row) > 3 else 0)
        
        try:
            prc_float = float(str(prc).replace(',', ''))
            if row_date == latest_market_date:
                price_dict[sym] = prc_float
            else:
                prev_price_dict[sym] = prc_float
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

# ================= 修改點：調整頁籤順序 =================
tab_market, tab_status, tab_action = st.tabs(["Quotes", "Dashboard", "Action"])

# --- 頁籤一：報價紀錄 (Quotes) ---
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
                
                # 漲跌顏色判定
                price_color = "#1f1a14"
                try:
                    curr_prc = float(price_m.replace(',', ''))
                    if symbol_m in prev_price_dict:
                        prev_prc = prev_price_dict[symbol_m]
                        if curr_prc > prev_prc:
                            price_color = "#FF6B35" 
                        elif curr_prc < prev_prc:
                            price_color = "#7ba23f" 
                except:
                    pass
                
                # ================= 修改點：HTML 靠左對齊 =================
                st.markdown(f"""
<div class="swiss-card" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px;">
    <div>
        <span style="font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">{date_m}</span>
        <div style="font-weight: bold; font-size: 13px; font-family: monospace; color: #1f1a14;">{symbol_m} // {name_m}</div>
    </div>
    <div style="font-size: 16px; font-weight: bold; font-family: monospace; color: {price_color};">
        {price_m}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 頁籤二：狀態面板 (Dashboard) ---
with tab_status:
    st.markdown('<div style="font-size: 11px; font-family: monospace; border-left: 2px solid #1f1a14; padding-left: 8px; margin: 12px 0; font-weight: bold; color: #1f1a14;">TACTICAL MONITOR & RISK</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1, 1])

    # ======== 欄位一：0050 與 00631L ========
    with col1:
        # 1. 0050 核心部位 (2x3 Grid)
        sym_0050 = "0050"
        p_0050 = price_dict.get(sym_0050, 0)
        h_0050_raw = status_dict.get(f"{sym_0050}_最高價", p_0050)
        try: h_0050 = float(str(h_0050_raw).replace(',', ''))
        except: h_0050 = p_0050 if p_0050 > 0 else 200.0

        targets_50 = [h_0050 * 0.9, h_0050 * 0.8, h_0050 * 0.7]
        status_50 = []
        for t in targets_50:
            if p_0050 > 0 and p_0050 <= t:
                status_50.append(("#FF6B35", "#1f1a14", "✅ 已達標"))
            else:
                status_50.append(("#f0e6d2", "#1f1a14", "等待中"))

        st.markdown(f"""
<div class="swiss-card">
    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
        0050 核心部位
        <div style="font-size: 10px; font-family: monospace; margin-top: 2px; font-weight: normal;">現價 {p_0050} / 高點 {h_0050:.1f}</div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; font-family: monospace;">
        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 9px; opacity: 0.8; font-weight: bold;">高點 × 0.9</span><br>
            <strong style="font-size: 12px; color: #1f1a14;">{targets_50[0]:.1f}</strong>
        </div>
        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 9px; opacity: 0.8; font-weight: bold;">高點 × 0.8</span><br>
            <strong style="font-size: 12px; color: #1f1a14;">{targets_50[1]:.1f}</strong>
        </div>
        <div style="background-color: #e4dac6; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 9px; opacity: 0.8; font-weight: bold;">高點 × 0.7</span><br>
            <strong style="font-size: 12px; color: #1f1a14;">{targets_50[2]:.1f}</strong>
        </div>
        
        <div style="background-color: {status_50[0][0]}; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 10px; font-weight: bold; color: {status_50[0][1]};">{status_50[0][2]}</span>
        </div>
        <div style="background-color: {status_50[1][0]}; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 10px; font-weight: bold; color: {status_50[1][1]};">{status_50[1][2]}</span>
        </div>
        <div style="background-color: {status_50[2][0]}; border: 1px solid #1f1a14; padding: 4px; text-align: center;">
            <span style="font-size: 10px; font-weight: bold; color: {status_50[2][1]};">{status_50[2][2]}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # 2. 00631L 戰術部屬
        sym_631L = "00631L"
        p_631L = price_dict.get(sym_631L, 0)
        h_631L_raw = status_dict.get(f"{sym_631L}_歷史高點", p_631L)
        try: h_631L = float(str(h_631L_raw).replace(',', ''))
        except: h_631L = p_631L if p_631L > 0 else 250.0

        inv_str = status_dict.get(f"{sym_631L}_庫存陣列", "[]")
        try: inv_list = json.loads(inv_str)
        except: inv_list = []
        
        slots_html = ""
        for i in range(3):
            val = inv_list[i] if i < len(inv_list) else ""
            if "防禦" in val:
                slots_html += f'<div style="background-color: #FF6B35; color: #1f1a14; border: 1px solid #1f1a14; text-align: center; font-size: 11px; font-weight: bold; padding: 4px;">防禦</div>'
            elif "進攻" in val:
                slots_html += f'<div style="background-color: #FFD500; color: #1f1a14; border: 1px solid #1f1a14; text-align: center; font-size: 11px; font-weight: bold; padding: 4px;">進攻</div>'
            else:
                slots_html += f'<div style="background-color: #e4dac6; color: #1f1a14; border: 1px solid #1f1a14; text-align: center; font-size: 11px; font-weight: bold; padding: 4px; opacity: 0.5;">空置</div>'

        targets_L = [h_631L * 0.85, h_631L * 0.80, h_631L * 0.70]
        targets_R = [h_631L, h_631L * 1.1, h_631L * 1.2]

        def get_status_html(target, current, is_right_side=False):
            if current == 0:
                return f'<span style="font-size: 10px; font-weight: bold; color: #1f1a14;">等待中</span>'
            is_reached = (current >= target) if is_right_side else (current <= target)
            if is_reached:
                return f'<span style="font-size: 10px; font-weight: bold; color: #FF6B35;">✅ 已達標</span>'
            return f'<span style="font-size: 10px; font-weight: bold; color: #1f1a14;">等待中</span>'

        st.markdown(f"""
<div class="swiss-card">
    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
        00631L 戰術部署
        <div style="font-size: 10px; font-family: monospace; margin-top: 2px; font-weight: normal;">現價 {p_631L} / 高點 {h_631L:.1f}</div>
    </div>
    
    <div style="margin-bottom: 4px; font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">CURRENT INVENTORY (MAX 3)</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin-bottom: 12px; font-family: monospace;">
        {slots_html}
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 4px; font-family: monospace;">
        <div style="background-color: #1f1a14; color: #f0e6d2; text-align: center; font-size: 10px; font-weight: bold; padding: 4px;">🛡️ 防禦 (左側)</div>
        <div style="background-color: #1f1a14; color: #f0e6d2; text-align: center; font-size: 10px; font-weight: bold; padding: 4px;">⚔️ 進攻 (右側)</div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-family: monospace;">
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">高點×0.85</span><br><strong style="font-size: 11px;">{targets_L[0]:.1f}</strong></div>
            {get_status_html(targets_L[0], p_631L, False)}
        </div>
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">突破高點</span><br><strong style="font-size: 11px;">{targets_R[0]:.1f}</strong></div>
            {get_status_html(targets_R[0], p_631L, True)}
        </div>
        
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">高點×0.80</span><br><strong style="font-size: 11px;">{targets_L[1]:.1f}</strong></div>
            {get_status_html(targets_L[1], p_631L, False)}
        </div>
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">高點×1.1</span><br><strong style="font-size: 11px;">{targets_R[1]:.1f}</strong></div>
            {get_status_html(targets_R[1], p_631L, True)}
        </div>
        
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">高點×0.70</span><br><strong style="font-size: 11px;">{targets_L[2]:.1f}</strong></div>
            {get_status_html(targets_L[2], p_631L, False)}
        </div>
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 4px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.1;"><span style="font-size: 8px; font-weight: bold; opacity:0.6;">高點×1.2</span><br><strong style="font-size: 11px;">{targets_R[2]:.1f}</strong></div>
            {get_status_html(targets_R[2], p_631L, True)}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ======== 欄位二：2330 與 3711 (衛星) ========
    with col2:
        for sym, name in [("2330", "台積電"), ("3711", "日月光")]:
            p_sat = price_dict.get(sym, 0)
            h_sat_raw = status_dict.get(f"{sym}_最高價", p_sat)
            try: h_sat = float(str(h_sat_raw).replace(',', ''))
            except: h_sat = p_sat
            
            t_90 = h_sat * 0.90
            t_85 = h_sat * 0.85
            
            s_90 = "✅ 觸發" if (p_sat > 0 and p_sat <= t_90) else "等待"
            s_85 = "✅ 觸發" if (p_sat > 0 and p_sat <= t_85) else "等待"

            st.markdown(f"""
<div class="swiss-card">
    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
        {sym} {name}
        <div style="font-size: 10px; font-family: monospace; margin-top: 2px; font-weight: normal;">現價 {p_sat} / 高點 {h_sat:.1f}</div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr; gap: 4px; font-family: monospace;">
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 6px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.2;">
                <span style="font-size: 9px; font-weight: bold; opacity:0.7;">回檔 0.90 (買2萬)</span><br>
                <strong style="font-size: 13px;">{t_90:.1f}</strong>
            </div>
            <span style="font-size: 10px; font-weight: bold; color: {'#FF6B35' if '✅' in s_90 else '#1f1a14'};">{s_90}</span>
        </div>
        <div style="background-color: #f0e6d2; border: 1px solid #1f1a14; padding: 6px; display: flex; justify-content: space-between; align-items: center;">
            <div style="line-height: 1.2;">
                <span style="font-size: 9px; font-weight: bold; opacity:0.7;">修正 0.85 (買4萬)</span><br>
                <strong style="font-size: 13px;">{t_85:.1f}</strong>
            </div>
            <span style="font-size: 10px; font-weight: bold; color: {'#FF6B35' if '✅' in s_85 else '#1f1a14'};">{s_85}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ======== 欄位三：00981A 轉倉 ========
    with col3:
        transfer_status = status_dict.get('00981A_已換防', '0')
        try: transfer_code = int(float(str(transfer_status).replace(',', '')))
        except: transfer_code = 0
            
        status_text = "終極換防已觸發，部位轉倉" if transfer_code == 1 else "常態駐守中"
        status_color = "#FF6B35" if transfer_code == 1 else "#7ba23f"
        text_color = "#1f1a14" if transfer_code == 1 else "#f0e6d2"
        
        st.markdown(f"""
<div class="swiss-card">
    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
        00981A 轉倉狀態
    </div>
    <div style="background-color: {status_color}; color: {text_color}; padding: 12px; font-family: monospace; font-size: 12px; font-weight: bold; text-align: center; border: 1px solid #1f1a14;">
        {status_text}
    </div>
    <div style="font-size: 10px; font-family: monospace; color: #1f1a14; margin-top: 8px; opacity: 0.8;">
        *觸發條件：0050日收盤價自最高點回撤≥15%
    </div>
</div>

<div class="swiss-card">
    <div style="font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #1f1a14; border-bottom: 1px solid #1f1a14; padding-bottom: 4px;">
        下次排程檢查日
    </div>
    <ul style="font-size: 11px; font-family: monospace; color: #1f1a14; margin: 0; padding-left: 16px;">
        <li style="margin-bottom: 6px;"><strong>13週比例檢查：</strong>2026/08/14</li>
        <li><strong>四週加碼大軍：</strong>2026/08/17</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- 頁籤三：明日行動 (Action) ---
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

st.markdown("""
<div style="border-top: 1px solid #1f1a14; margin-top: 20px; padding-top: 10px; display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; font-weight: bold; color: #1f1a14;">
    <span>THEME: DUNE & SWISS</span>
    <span>PAGE 01/01</span>
</div>
</div>
""", unsafe_allow_html=True)