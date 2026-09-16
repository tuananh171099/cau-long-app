import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="CLB Cầu Lông", page_icon="🏸")
st.title("🏸 Quản Lý Điểm Cầu Lông CLB")

# --- ĐIỀN THÔNG TIN CỦA BẠN VÀO 2 DÒNG NÀY ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
# Bạn tạo 1 Web App URL từ Google Sheet (xem hướng dẫn nhanh bên dưới)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw7dy5f24HpFYqJDaEPH-4oxYrPKL8w8Blx7YgTbe9stUsNya6KiNMlsLWcJ1HvToIz/exec"


def get_csv_url(url):
    if "/edit" in url:
        return url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
    return url


@st.cache_data(ttl=2)
def load_data():
    try:
        csv_url = get_csv_url(SHEET_URL)
        df = pd.read_csv(csv_url)
        return df
    except Exception:
        return pd.DataFrame()


df = load_data()

# --- KHU VỰC 1: BẢNG XẾP HẠNG ---
st.subheader("🏆 BẢNG XẾP HẠNG CLB")
if not df.empty and "Điểm" in df.columns:
    df_sorted = df.sort_values(by="Điểm", ascending=False)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)
else:
    st.warning(
        "Chưa đọc được dữ liệu. Bạn nhớ thay Link Google Sheet và bật quyền chia sẻ công khai nhé!"
    )

st.divider()

# --- KHU VỰC 2: Ô NHẬP ĐIỂM TRỰC TIẾP TRÊN WEB ---
st.subheader("📝 Cập Nhật Trực Tiếp Trên Web")
tab1, tab2 = st.tabs(["➕ Thêm VĐV Mới", "⚔️ Cập Nhật Trận Đấu"])

with tab1:
    with st.form("add_player"):
        new_name = st.text_input("Nhập tên VĐV mới:")
        btn_add = st.form_submit_button("Lưu VĐV")

        if btn_add and new_name:
            payload = {"action": "add_player", "name": new_name}
            res = requests.post(SCRIPT_URL, json=payload)
            st.success(f"Đã thêm VĐV {new_name} thành công!")
            st.cache_data.clear()
            st.rerun()

with tab2:
    if not df.empty and "Tên VĐV" in df.columns:
        player_list = df["Tên VĐV"].tolist()
        with st.form("add_match"):
            col1, col2 = st.columns(2)
            with col1:
                winner = st.selectbox("Người thắng (+3 điểm):", player_list)
            with col2:
                loser = st.selectbox(
                    "Người thua (+1 điểm):",
                    [p for p in player_list if p != winner],
                )

            btn_match = st.form_submit_button("Lưu Kết Quả Trận Đấu")

            if btn_match:
                payload = {
                    "action": "update_match",
                    "winner": winner,
                    "loser": loser,
                }
                res = requests.post(SCRIPT_URL, json=payload)
                st.success(f"Đã lưu: {winner} thắng {loser}!")
                st.cache_data.clear()
                st.rerun()
