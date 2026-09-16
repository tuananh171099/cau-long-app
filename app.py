import streamlit as st
import pandas as pd
from datetime import datetime, date

# Cấu hình trang
st.set_page_config(page_title="Quản Lý CLB Cầu Lông", layout="wide")

# Khởi tạo dữ liệu mẫu trong Session State
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
menu = st.sidebar.radio("Điều hướng", ["Leaderboard & Quỹ", "Cập nhật trận đấu", "Tìm kiếm thành viên", "Quản lý thành viên"])

# ==========================================
# 1. BẢNG XẾP HẠNG & QUỸ
# ==========================================
if menu == "Leaderboard & Quỹ":
    st.header("🏆 Bảng Xếp Hạng & Quỹ Thua Trận")
    
    if st.session_state.matches.empty:
        st.info("Chưa có dữ liệu trận đấu nào được ghi nhận.")
    else:
        df_matches = st.session_state.matches.copy()
        
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
                
                for w in winners:
                    if w in stats:
                        stats[w]["Điểm"] += 3
                        stats[w]["Thắng"] += 1
                
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
# 2. CẬP NHẬT TRẬN ĐẤU (ĐÁNH ĐÔI)
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
# 3. TÌM KIẾM THÀNH VIÊN
# ==========================================
elif menu == "Tìm kiếm thành viên":
    st.header("🔍 Lịch Sử Thi Đấu Của Thành Viên")
    
    if not st.session_state.members:
        st.warning("Chưa có thành viên nào trong danh sách!")
    else:
        selected_member = st.selectbox("Chọn thành viên cần xem:", st.session_state.members)
        
        df_matches = st.session_state.matches.copy()
        
        # Lọc trận đấu của VĐV
        filter_condition = (
            (df_matches["Đội 1 - VĐV 1"] == selected_member) |
            (df_matches["Đội 1 - VĐV 2"] == selected_member) |
            (df_matches["Đội 2 - VĐV 1"] == selected_member) |
            (df_matches["Đội 2 - VĐV 2"] == selected_member)
        ) if not df_matches.empty else pd.Series([], dtype=bool)
        
        user_matches = df_matches[filter_condition].copy() if not df_matches.empty else pd.DataFrame()
        
        # 1. Tính toán chỉ số thống kê
        today_str = date.today().strftime("%Y-%m-%d")
        now = datetime.now()
        
        win_today = lose_today = 0
        win_month = lose_month = 0
        
        if not user_matches.empty:
            user_matches["Ngày_dt"] = pd.to_datetime(user_matches["Ngày"])
            
            for _, row in user_matches.iterrows():
                is_team1 = selected_member in [row["Đội 1 - VĐV 1"], row["Đội 1 - VĐV 2"]]
                is_winner = (is_team1 and row["Đội Thắng"] == "Đội 1") or (not is_team1 and row["Đội Thắng"] == "Đội 2")
                
                # Check hôm nay
                if row["Ngày"] == today_str:
                    if is_winner:
                        win_today += 1
                    else:
                        lose_today += 1
                
                # Check tháng này
                if row["Ngày_dt"].month == now.month and row["Ngày_dt"].year == now.year:
                    if is_winner:
                        win_month += 1
                    else:
                        lose_month += 1

        fine_today = lose_today * 10
        fine_month = lose_month * 10

        # Hiển thị thống kê
        st.subheader(f"📊 Báo cáo thành tích: **{selected_member}**")
        col_t, col_m = st.columns(2)
        
        with col_t:
            st.info(f"**Hôm nay ({today_str}):**\n- Thắng: **{win_today}** trận | Thua: **{lose_today}** trận\n- Thua tổng tiền: **{fine_today}k VNĐ**")
            
        with col_m:
            st.success(f"**Tháng này ({now.month}/{now.year}):**\n- Thắng: **{win_month}** trận | Thua: **{lose_month}** trận\n- Thua tổng tiền: **{fine_month}k VNĐ**")

        st.markdown("---")
        st.subheader("📜 Danh sách các trận đấu đã tham gia")
        
        if user_matches.empty:
            st.write("Chưa tham gia trận đấu nào.")
        else:
            # Nhóm theo ngày và hiển thị dạng thẻ khung
            grouped = user_matches.groupby("Ngày", sort=False)
            
            for match_date, group in grouped:
                st.markdown(f"#### 🗓️ Ngày: {match_date}")
                
                for _, row in group.iterrows():
                    team1_str = f"{row['Đội 1 - VĐV 1']} / {row['Đội 1 - VĐV 2']}"
                    team2_str = f"{row['Đội 2 - VĐV 1']} / {row['Đội 2 - VĐV 2']}"
                    score_str = f"{row['Điểm Đội 1']} - {row['Điểm Đội 2']}"
                    
                    # Highlight nếu là đội chiến thắng
                    if row["Đội Thắng"] == "Đội 1":
                        match_text = f"**{team1_str}** &nbsp; ` {score_str} ` &nbsp; {team2_str}"
                    else:
                        match_text = f"{team1_str} &nbsp; ` {score_str} ` &nbsp; **{team2_str}**"
                    
                    st.info(f"🏸 {match_text}")

# ==========================================
# 4. QUẢN LÝ THÀNH VIÊN (THÊM / XÓA)
# ==========================================
elif menu == "Quản lý thành viên":
    st.header("⚙️ Quản Lý Danh Sách Thành Viên")
    
    # Form thêm thành viên mới
    with st.form("add_member_form", clear_on_submit=True):
        new_name = st.text_input("Nhập họ và tên thành viên mới:")
        add_btn = st.form_submit_button("➕ Thêm thành viên")
        
        if add_btn:
            name_clean = new_name.strip()
            if name_clean == "":
                st.warning("Vui lòng nhập tên thành viên!")
            elif name_clean in st.session_state.members:
                st.error("Thành viên này đã có trong danh sách!")
            else:
                st.session_state.members.append(name_clean)
                st.success(f"Đã thêm thành viên **{name_clean}** thành công!")
                st.rerun()

    st.subheader("📋 Danh sách thành viên hiện tại")
    
    if not st.session_state.members:
        st.info("Danh sách thành viên đang trống.")
    else:
        # Hiển thị từng dòng kèm nút Xóa
        for idx, member in enumerate(st.session_state.members):
            col_name, col_del = st.columns([4, 1])
            col_name.write(f"**{idx + 1}. {member}**")
            
            if col_del.button("🗑️ Xóa", key=f"del_{idx}"):
                st.session_state.members.pop(idx)
                st.success(f"Đã xóa thành viên **{member}**!")
                st.rerun()
import streamlit as st
import pandas as pd

st.set_page_config(page_title="CLB Cầu Lông", page_icon="🏸")
st.title("🏸 Quản Lý Điểm Cầu Lông CLB")

# --- KẾT NỐI GOOGLE SHEETS ---
# Thay liên kết Google Sheets của bạn vào dòng dưới đây
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing/export?format=csv"

@st.cache_data(ttl=5) # Tự động cập nhật dữ liệu mới mỗi 5 giây
def load_data():
    try:
        # Đọc dữ liệu trực tiếp từ Google Sheets
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error("Không thể kết nối đến Google Sheets. Vui lòng kiểm tra lại link chia sẻ!")
        return pd.DataFrame()

# Tải dữ liệu
df = load_data()

st.subheader("🏆 Bảng Xếp Hạng (Dữ liệu vĩnh viễn từ Google Sheets)")

if not df.empty:
    # Sắp xếp theo điểm giảm dần
    df_sorted = df.sort_values(by="Điểm", ascending=False)
    st.dataframe(df_sorted, use_container_width=True)
else:
    st.info("Chưa có dữ liệu hoặc đường link Google Sheets chưa đúng.")

if st.button("🔄 Cập nhật dữ liệu mới"):
    st.cache_data.clear()
    st.rerun()
