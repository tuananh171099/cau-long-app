import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="CLB Cầu Lông", page_icon="🏸")
st.title("🏸 Quản Lý & Tính Điểm Cầu Lông CLB")

# Dán đường link Google Sheets của bạn vào đây:
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(spreadsheet=SHEET_URL, ttl="0s")

df = get_data()

# --- KHU VỰC 1: BẢNG XẾP HẠNG ---
st.subheader("🏆 Bảng Xếp Hạng")
if not df.empty and "Điểm" in df.columns:
    df_sorted = df.sort_values(by="Điểm", ascending=False)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có dữ liệu VĐV nào.")

st.divider()

# --- KHU VỰC 2: NHẬP DỮ LIỆU TRỰC TIẾP TRÊN WEB ---
tab1, tab2 = st.tabs(["➕ Thêm VĐV Mới", "⚔️ Cập Nhật Kết Quả Trận Đấu"])

# 1. Tab Thêm VĐV
with tab1:
    with st.form("add_player_form"):
        new_name = st.text_input("Tên VĐV mới:")
        submit_add = st.form_submit_button("Thêm VĐV")
        
        if submit_add and new_name:
            if not df.empty and new_name in df["Tên VĐV"].values:
                st.warning("VĐV này đã có trong danh sách!")
            else:
                new_row = pd.DataFrame([{"Tên VĐV": new_name, "Số trận": 0, "Thắng": 0, "Điểm": 0}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"Đã thêm VĐV: {new_name}")
                st.rerun()

# 2. Tab Cập nhật kết quả
with tab2:
    if not df.empty and len(df) >= 2:
        with st.form("match_form"):
            col1, col2 = st.columns(2)
            with col1:
                winner = st.selectbox("Người thắng (Cộng 3 điểm):", df["Tên VĐV"].tolist())
            with col2:
                loser = st.selectbox("Người thua (Cộng 1 điểm):", df[df["Tên VĐV"] != winner]["Tên VĐV"].tolist())
            
            submit_match = st.form_submit_button("Lưu kết quả trận đấu")
            
            if submit_match:
                # Cập nhật người thắng (+1 trận, +1 thắng, +3 điểm)
                df.loc[df["Tên VĐV"] == winner, "Số trận"] += 1
                df.loc[df["Tên VĐV"] == winner, "Thắng"] += 1
                df.loc[df["Tên VĐV"] == winner, "Điểm"] += 3
                
                # Cập nhật người thua (+1 trận, +1 điểm tham gia)
                df.loc[df["Tên VĐV"] == loser, "Số trận"] += 1
                df.loc[df["Tên VĐV"] == loser, "Điểm"] += 1
                
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.success(f"Đã lưu kết quả: {winner} thắng {loser}!")
                st.rerun()
    else:
        st.info("Cần ít nhất 2 VĐV trong danh sách để cập nhật trận đấu.")
