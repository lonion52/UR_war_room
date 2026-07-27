import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="鋼鐵柚子戰情室", layout="wide")

# ================= 參數與資料讀取 =================
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxf0xiDNHzoJXBI5ZIoUfeijjPuTtpxh2BwG_NPYOqpTFrkD5_jAy72U9xeEHl5YH0U/exec"

@st.cache_data(ttl=60)
def load_gas_data(sheet_name):
    try:
        url = f"{GAS_WEB_APP_URL}?sheet={sheet_name}"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        # 錯誤處理與測試用 Mock 資料，避免 API 未就緒時前端崩潰
        if sheet_name == "State":
            return pd.DataFrame({
                "Key": ["0050_最高價", "00631L_歷史高點", "00631L_庫存陣列", "00981A_已換防", "2330_最高價", "3711_最高價"],
                "Value": ["200", "250", '["防禦","防禦"]', "0", "1080", "170"]
            })
        return pd.DataFrame()

state_df = load_gas_data("State")
quotes_df = load_gas_data("Quotes") # 預期含有最新價格

# 解析 State
state = {}
if not state_df.empty and len(state_df.columns) >= 2:
    for idx, row in state_df.iterrows():
        state[str(row.iloc[0])] = row.iloc[1]

# 假設目前市價 (實務從 Quotes 取得最新一筆)
p_0050 = 175.0
p_00631L = 210.0
p_2330 = 950.0
p_3711 = 145.0

# ================= 頁面結構 =================
st.title("🛡️ 鋼鐵柚子戰情室")
tab_quotes, tab_dash, tab_action = st.tabs(["Quotes 報價", "Dashboard 儀表板", "Action 執行指令"])

with tab_dash:
    col1, col2, col3 = st.columns([1.2, 1, 1])

    # ---------------- 欄位一：0050 與 00631L ----------------
    with col1:
        # --- 0050 區塊 ---
        st.subheader("🎯 0050 核心部位")
        h_0050 = float(state.get("0050_最高價", 200.0))
        st.write(f"**最新現價**：{p_0050} / **歷史高點**：{h_0050}")
        
        # 0050 2x3 Grid
        st.markdown("##### 📉 高點回撤監控 (40萬計畫)")
        c1, c2, c3 = st.columns(3)
        
        def render_0050_cell(col, label, ratio):
            target = h_0050 * ratio
            is_reached = p_0050 <= target
            status = "✅ 已達到目標價" if is_reached else f"差距 {(p_0050 - target):.1f}"
            col.metric(label, f"{target:.1f}", status, delta_color="off" if is_reached else "normal")
            
        render_0050_cell(c1, "回撤 10% (x0.9)", 0.9)
        render_0050_cell(c2, "回撤 20% (x0.8)", 0.8)
        render_0050_cell(c3, "回撤 30% (x0.7)", 0.7)
        
        st.divider()

        # --- 00631L 區塊 ---
        st.subheader("00631L 🛡️戰術部屬⚔️")
        
        # 庫存顯示 (1x3)
        inv_str = state.get("00631L_庫存陣列", "[]")
        try:
            inv_list = json.loads(inv_str)
        except:
            inv_list = []
            
        slots = [inv_list[i] if i < len(inv_list) else "空" for i in range(3)]
        html_slots = "<div style='display:flex; gap:10px; margin-bottom:15px;'>"
        for s in slots:
            if s == "防禦":
                html_slots += f"<div style='background:#f59e0b; color:white; padding:8px 20px; border-radius:5px; font-weight:bold;'>🛡️ 防禦</div>"
            elif s == "進攻":
                html_slots += f"<div style='background:#ef4444; color:white; padding:8px 20px; border-radius:5px; font-weight:bold;'>⚔️ 進攻</div>"
            else:
                html_slots += f"<div style='background:#374151; color:white; padding:8px 20px; border-radius:5px; font-weight:bold;'>⬜ 空置</div>"
        html_slots += "</div>"
        st.markdown(html_slots, unsafe_allow_html=True)

        # 3x4 Grid (左防禦 / 右進攻)
        h_00631L = float(state.get("00631L_歷史高點", 250.0))
        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            st.markdown("#### 🛡️ 防禦 (左側)")
            def render_left(label, ratio):
                target = h_00631L * ratio
                status = "✅ 已達標" if p_00631L <= target else "等待中"
                st.info(f"**{label}**\n\n{target:.1f}  ➔  {status}")
            render_left("高點 × 0.85", 0.85)
            render_left("高點 × 0.80", 0.80)
            render_left("高點 × 0.70", 0.70)
            
        with d_col2:
            st.markdown("#### ⚔️ 進攻 (右側)")
            # 假設右側新高點同為歷史高點，實務上需依照 GAS 的 00631L_右側新高點 動態計算
            new_high = h_00631L 
            def render_right(label, target):
                status = "✅ 已達標" if p_00631L >= target else "等待中"
                st.error(f"**{label}**\n\n{target:.1f}  ➔  {status}")
            render_right("突破歷史高點", new_high)
            render_right("新高點 × 1.1", new_high * 1.1)
            render_right("新高點 × 1.2", new_high * 1.2)

    # ---------------- 欄位二：2330 與 3711 (衛星) ----------------
    with col2:
        st.subheader("🛰️ 衛星部位 (4倍投入中)")
        
        h_2330 = float(state.get("2330_最高價", 1080.0))
        st.markdown(f"### 2330 台積電\n**現價:** {p_2330} / **高點:** {h_2330}")
        st.metric("回檔 0.90 (買2萬)", f"{h_2330*0.9:.1f}", "✅ 觸發" if p_2330 <= h_2330*0.9 else "等待")
        st.metric("修正 0.85 (買4萬)", f"{h_2330*0.85:.1f}", "✅ 觸發" if p_2330 <= h_2330*0.85 else "等待")
        
        st.divider()
        
        h_3711 = float(state.get("3711_最高價", 170.0))
        st.markdown(f"### 3711 日月光\n**現價:** {p_3711} / **高點:** {h_3711}")
        st.metric("回檔 0.90 (買2萬)", f"{h_3711*0.9:.1f}", "✅ 觸發" if p_3711 <= h_3711*0.9 else "等待")
        st.metric("修正 0.85 (買4萬)", f"{h_3711*0.85:.1f}", "✅ 觸發" if p_3711 <= h_3711*0.85 else "等待")

    # ---------------- 欄位三：00981A ----------------
    with col3:
        st.subheader("🛡️ 00981A 轉倉狀態")
        is_switched = int(state.get("00981A_已換防", 0))
        
        if is_switched == 1:
            st.error("🚨 終極換防已觸發！\n00981A 已全數清空轉入 00631L。")
        else:
            st.success("✅ 駐守中\n尚未觸發 0050 回撤 15% 防線。")
        
        st.divider()
        st.markdown("### 📅 下次檢查日")
        st.write("- **13週比例檢查**：2026/08/14")
        st.write("- **四週加碼大軍**：2026/08/17")

# --- 其他分頁留供檢視原始資料 ---
with tab_quotes:
    st.write("市場報價紀錄 (Quotes)")
    st.dataframe(quotes_df)
    
with tab_action:
    action_df = load_gas_data("Action")
    st.write("交易指令紀錄 (Action)")
    st.dataframe(action_df)