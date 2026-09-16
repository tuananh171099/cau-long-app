import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="CLB Cầu Lông - Quản Lý Điểm", page_icon="🏸", layout="wide"
)

# --- ĐIỀN THÔNG TIN CỦA BẠN VÀO 2 DÒNG NÀY ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw7dy5f24HpFYqJDaEPH-4oxYrPKL8w8Blx7YgTbe9stUsNya6KiNMlsLWcJ1HvToIz/exec"


def get_sheet_csv_url(url, sheet_name="Sheet1"):
    if "/edit" in url:
        base = url.split("/edit")[0]
        return f"{base}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return url


@st.cache_data(ttl=2)
def load_all_data():
    try:
        url_players = get_sheet_csv_url(SHEET_URL)
        df_players = pd.read_csv(url_players)

        url_matches = get_sheet_csv_url(SHEET_URL, "Lịch Sử Trận Đấu")
        df_matches = pd.read_csv(url_matches)
        return df_players, df_matches
    except Exception:
        return pd.DataFrame(), pd.DataFrame()


df_players, df_matches = load_all_data()

st.title("🏸 Quản Lý & Tính Điểm Cầu Lông CLB")

# THỐNG KÊ NHANH CÁC CHỈ SỐ
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Tổng VĐV Tham Gia", len(df_players) if not df_players.empty else 0)
with col_b:
    st.metric(
        "Tổng Trận Đã Đấu", len(df_matches) if not df_matches.empty else 0
    )
with col_c:
    top_player = (
        df_players.sort_values(by="Điểm", ascending=False).iloc[0]["Tên VĐV"]
        if not df_players.empty and "Điểm" in df_players.columns
        else "Chưa có"
    )
    st.metric("VĐV Dẫn Đầu 🏆", top_player)

st.divider()

# TABS CHÍNH CỦA TRANG WEB
tab_leaderboard, tab_history, tab_action = st.tabs(
    ["🏆 Bảng Xếp Hạng", "📜 Lịch Sử Trận Đấu", "📝 Nhập & Cập Nhật Điểm"]
)

# 1. BẢNG XẾP HẠNG
with tab_leaderboard:
    st.subheader("📊 Bảng Xếp Hạng Chi Tiết")
    if not df_players.empty and "Điểm" in df_players.columns:
        # Tính tỷ lệ thắng %
        df_display = df_players.copy()
        df_display["Tỷ Lệ Thắng"] = (
            (df_display["Thắng"] / df_display["Số trận"] * 100)
            .fillna(0)
            .round(1)
            .astype(str)
            + "%"
        )
        df_sorted = df_display.sort_values(by="Điểm", ascending=False)
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu Bảng xếp hạng.")

# 2. LỊCH SỬ TRẬN ĐẤU
with tab_history:
    st.subheader("📜 Danh Sách Các Trận Đấu Đã Điễn Ra")
    if not df_matches.empty:
        st.dataframe(
            df_matches.iloc[::-1], use_container_width=True, hide_index=True
        )  # Mới nhất lên đầu
    else:
        st.info("Chưa có lịch sử trận đấu nào được ghi nhận.")

# 3. NHẬP VÀ CẬP NHẬT ĐIỂM
with tab_action:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⚔️ Cập Nhật Kết Quả Trận Đấu")
        if not df_players.empty and "Tên VĐV" in df_players.columns:
            player_list = df_players["Tên VĐV"].tolist()
            with st.form("form_match"):
                winner = st.selectbox(
                    "Người thắng (+3 điểm):", player_list, key="w"
                )
                loser = st.selectbox(
                    "Người thua (+1 điểm):",
                    [p for p in player_list if p != winner],
                    key="l",
                )
                btn_match = st.form_submit_button("Lưu Kết Quả Trận Đấu")

                if btn_match:
                    payload = {
                        "action": "update_match",
                        "winner": winner,
                        "loser": loser,
                    }
                    requests.post(SCRIPT_URL, json=payload)
                    st.success(f"Đã lưu: {winner} thắng {loser}!")
                    st.cache_data.clear()
                    st.rerun()

    with col_right:
        st.subheader("➕ Thêm VĐV Mới")
        with st.form("form_add_player"):
            new_name = st.text_input("Nhập tên VĐV mới:")
            btn_add = st.form_submit_button("Thêm VĐV")

            if btn_add and new_name:
                payload = {"action": "add_player", "name": new_name}
                requests.post(SCRIPT_URL, json=payload)
                st.success(f"Đã thêm VĐV {new_name}!")
                st.cache_data.clear()
                st.rerun()

    st.divider()
    with st.expander("⚙️ Quản Lý Nâng Cáo (Xóa/Reset dữ liệu)"):
        if st.button("🔴 Reset Toàn Bộ Điểm Số & Lịch Sử (Làm Mới Mùa Giải)"):
            payload = {"action": "reset_all"}
            requests.post(SCRIPT_URL, json=payload)
            st.warning("Đã reset toàn bộ dữ liệu!")
            st.cache_data.clear()
            st.rerun()
