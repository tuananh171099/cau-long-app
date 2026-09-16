import streamlit as st
import pandas as pd
from datetime import datetime, date

# Thiết lập cấu hình trang
st.set_page_config(page_title="Quản lý CLB Cầu Lông", layout="wide")

# 1. Khởi tạo dữ liệu lưu trữ trong Session State (Nên chuyển sang SQLite/CSV khi triển khai thực tế)
if "members" not in st.session_state:
    st.session_state.members = ["Nguyễn Văn A", "Trần Văn B", "Lê Thị C", "Phạm Văn D"]

if "matches" not in st.session_state:
    st.session_state.matches = pd.DataFrame(
        columns=[
            "Ngày",
            "Đội 1 - VĐV 1", "Đội 1 - VĐV 2", "Điểm Đội 1",
            "Đội 2 - VĐV 1", "Đội 2 - VĐV 2", "Điểm Đội 2",
            "Đội Thắng"
        ]
    )

st.title("🏸 Quản Lý Điểm & Quỹ CLB Cầu Lông")

# Thanh điều hướng (Sidebar)
menu = st.sidebar.radio("Điều hướng", ["Leaderboard & Quỹ", "Cập nhật trận đấu", "Tìm kiếm thành viên", "Thêm thành viên mới"])

# ==========================================
# CỨU NĂNG 1: BẢNG XẾP HẠNG & QUỸ
# ==========================================
if menu == "Leaderboard & Quỹ":
    st.header("🏆 Bảng Xếp Hạng & Quỹ Thua Trận")
    
    if st.session_state.matches.empty:
        st.info("Chưa có dữ liệu trận đấu nào được ghi nhận.")
    else:
        df_matches = st.session_state.matches.copy()
        
        # Lựa chọn thời gian xem Leaderboard
        tab_today, tab_month, tab_all = st.tabs(["Xếp hạng Hôm Nay", "Xếp hạng Theo Tháng", "Tổng Sắp Tất Cả"])

        def calculate_leaderboard(df_filtered):
            stats = {m: {"Điểm": 0, "Thắng": 0, "Thua": 0, "Tiền Phạt (k)": 0} for m in st.session_state.members}
            
            for _, row in df_filtered.iterrows():
                team1 = [row["Đội 1 - VĐV 1"], row["Đội 1 - VĐV 2"]]
                team2 = [row["Đội 2 - VĐV 1"], row["Đội 2 - VĐV 2"]]
                
                if row["Đội Thắng"] == "Đội 1":
                    winners, losers = team1, team2
                else:
                    winners, losers = team2, team1
                
                # Cộng điểm người thắng (+3 điểm)
                for w in winners:
                    if w in stats:
                        stats[w]["Điểm"] += 3
                        stats[w]["Thắng"] += 1
                
                # Tính tiền phạt người thua (10k/trận)
                for l in losers:
                    if l in stats:
                        stats[l]["Thua"] += 1
                        stats[l]["Tiền Phạt (k)"] += 10

            df_lb = pd.DataFrame.from_dict(stats, orient="index").reset_index()
            df_lb.rename(columns={"index": "Tên Thành Viên"}, inplace=True)
            df_lb.sort_values(by=["Điểm", "Thắng"], ascending=[False, False], inplace=True)
            df_lb.reset_index(drop=True, inplace=True)
            df_lb.index += 1
            return df_lb

        # Xếp hạng Hôm nay
        with tab_today:
            today_str = date.today().strftime("%Y-%m-%d")
            df_today = df_matches[df_matches["Ngày"] == today_str]
            st.subheader(f"Bảng xếp hạng ngày {today_str}")
            st.dataframe(calculate_leaderboard(df_today), use_container_width=True)

        # Xếp hạng Theo Tháng
        with tab_month:
            col1, col2 = st.columns(2)
            with col1:
                selected_year = st.number_input("Năm", min_value=2024, max_value=2030, value=datetime.now().year)
            with col2:
                selected_month = st.number_input("Tháng", min_value=1, max_value=12, value=datetime.now().month)
            
            df_matches["Ngày_dt"] = pd.to_datetime(df_matches["Ngày"])
            df_month = df_matches[(df_matches["Ngày_dt"].dt.month == selected_month) & (df_matches["Ngày_dt"].dt.year == selected_year)]
            
            st.subheader(f"Bảng xếp hạng Tháng {selected_month}/{selected_year}")
            st.dataframe(calculate_leaderboard(df_month), use_container_width=True)

        # Xếp hạng Tất cả
        with tab_all:
            st.subheader("Bảng xếp hạng Toàn thời gian")
            st.dataframe(calculate_leaderboard(df_matches), use_container_width=True)

# ==========================================
# TÍNH NĂNG 2: CẬP NHẬT TRẬN ĐẤU (ĐÁNH ĐÔI)
# ==========================================
elif menu == "Cập nhật trận đấu":
    st.header("📝 Ghi Nhận Kết Quả Trận Đấu (Đánh Đôi)")
    
    if len(st.session_state.members) < 4:
        st.warning("Cần tối thiểu 4 thành viên để tổ chức trận đánh đôi!")
    else:
        with st.form("match_form"):
            match_date = st.date_input("Ngày thi đấu", value=date.today())
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔵 Đội 1")
                p1 = st.selectbox("VĐV A", st.session_state.members, index=0)
                p2 = st.selectbox("VĐV B", st.session_state.members, index=min(1, len(st.session_state.members)-1))
                score1 = st.number_input("Điểm Đội 1", min_value=0, max_value=30, value=21)
                
            with col2:
                st.subheader("🔴 Đội 2")
                p3 = st.selectbox("VĐV C", st.session_state.members, index=min(2, len(st.session_state.members)-1))
                p4 = st.selectbox("VĐV D", st.session_state.members, index=min(3, len(st.session_state.members)-1))
                score2 = st.number_input("Điểm Đội 2", min_value=0, max_value=30, value=19)

            submitted = st.form_submit_button("Lưu kết quả trận đấu")

            if submitted:
                # Kiểm tra trùng lặp VĐV
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error("Lỗi: Các VĐV trong trận đấu không được trùng nhau!")
                elif score1 == score2:
                    st.error("Lỗi: Kết quả trận đấu cầu lông không được hòa!")
                else:
                    winner = "Đội 1" if score1 > score2 else "Đội 2"
                    new_match = {
                        "Ngày": match_date.strftime("%Y-%m-%d"),
                        "Đội 1 - VĐV 1": p1, "Đội 1 - VĐV 2": p2, "Điểm Đội 1": score1,
                        "Đội 2 - VĐV 1": p3, "Đội 2 - VĐV 2": p4, "Điểm Đội 2": score2,
                        "Đội Thắng": winner
                    }
                    st.session_state.matches = pd.concat([st.session_state.matches, pd.DataFrame([new_match])], ignore_index=True)
                    st.success(f"Đã lưu trận đấu thành công! {winner} chiến thắng 🎉")

# ==========================================
# TÍNH NĂNG 3: TÌM KIẾM LỊCH SỬ THÀNH VIÊN
# ==========================================
elif menu == "Tìm kiếm thành viên":
    st.header("🔍 Lịch Sử Thi Đấu Của Thành Viên")
    
    selected_member = st.selectbox("Chọn thành viên cần xem:", st.session_state.members)
    
    if st.session_state.matches.empty:
        st.info("Chưa có dữ liệu trận đấu.")
    else:
        df_matches = st.session_state.matches
        # Lọc các trận đấu có sự tham gia của thành viên được chọn
        filter_condition = (
            (df_matches["Đội 1 - VĐV 1"] == selected_member) |
            (df_matches["Đội 1 - VĐV 2"] == selected_member) |
            (df_matches["Đội 2 - VĐV 1"] == selected_member) |
            (df_matches["Đội 2 - VĐV 2"] == selected_member)
        )
        user_matches = df_matches[filter_condition].copy()
        
        if user_matches.empty:
            st.write(f"Thành viên **{selected_member}** chưa tham gia trận đấu nào.")
        else:
            st.write(f"Tìm thấy **{len(user_matches)}** trận đấu của **{selected_member}**:")
            st.dataframe(user_matches, use_container_width=True)

# ==========================================
# TÍNH NĂNG 4: THÊM THÀNH VIÊN MỚI
# ==========================================
elif menu == "Thêm thành viên mới":
    st.header("➕ Thêm Thành Viên Mới")
    
    new_name = st.text_input("Nhập họ và tên thành viên:")
    if st.button("Thêm vào CLB"):
        if new_name.strip() == "":
            st.warning("Tên thành viên không được để trống!")
        elif new_name.strip() in st.session_state.members:
            st.error("Thành viên này đã tồn tại trong danh sách!")
        else:
            st.session_state.members.append(new_name.strip())
            st.success(f"Đã thêm **{new_name.strip()}** vào danh sách thành viên!")

    st.subheader("📋 Danh sách thành viên hiện tại")
    st.write(", ".join(st.session_state.members))