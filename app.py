from datetime import date, datetime
import pandas as pd
import requests
import streamlit as st

# Cấu hình trang với Layout Rộng & Title
st.set_page_config(
    page_title="Badminton Club Manager",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện thêm hiện đại & chuyên nghiệp
st.markdown(
    """
    <style>
    /* Chỉnh font và padding tổng thể */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Style cho Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Thẻ Thống kê (Metric Cards Custom) */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #212529;
    }

    /* Đội 1 vs Đội 2 Card trong Cập nhật trận đấu */
    .team-card-1 {
        background-color: #e7f5ff;
        border-left: 5px solid #1c7ed6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .team-card-2 {
        background-color: #fff5f5;
        border-left: 5px solid #f03e3e;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* SCOREBOARD KHUNG TRẬN ĐẤU THEO KIỂU THỂ THAO */
    .scoreboard-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .scoreboard-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 12px;
        border-bottom: 1px solid #f0f0f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .scoreboard-row:last-child {
        border-bottom: none;
    }
    .team-name {
        font-size: 1rem;
        font-weight: 600;
        color: #495057;
        letter-spacing: 0.3px;
        flex-grow: 1;
    }
    .winner-row {
        background-color: #f8f9fa;
    }
    .winner-row .team-name {
        color: #000000;
        font-weight: 800;
    }
    .score-box {
        width: 42px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        font-weight: 800;
        border-radius: 4px;
        margin-left: 8px;
    }
    .score-winner {
        background-color: #212529;
        color: #ffffff;
    }
    .score-loser {
        background-color: #e9ecef;
        color: #495057;
    }
    .badge-win {
        background-color: #2b8a3e;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        margin-right: 8px;
        text-transform: uppercase;
    }
    </style>
""",
    unsafe_allow_html=True,
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw4QXiNzVXTDLd9ltpCiMElur1F29Wi_xV6w5jMx-ZFlQ25nkvOdUI5OvpJU7469UHnjw/exec"


def get_sheet_csv_url(url, sheet_name="Sheet1"):
    if "/edit" in url:
        base = url.split("/edit")[0]
        return f"{base}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return url


@st.cache_data(ttl=2)
def load_data():
    try:
        url_members = get_sheet_csv_url(SHEET_URL, "Members")
        df_m = pd.read_csv(url_members)
        members = df_m["Tên Thành Viên"].dropna().tolist()
    except Exception:
        members = ["Nguyễn Văn A", "Trần Văn B", "Lê Thị C", "Phạm Văn D"]

    try:
        url_matches = get_sheet_csv_url(SHEET_URL, "Matches")
        df_matches = pd.read_csv(url_matches)
    except Exception:
        df_matches = pd.DataFrame(
            columns=[
                "Ngày",
                "Đội 1 - VĐV 1",
                "Đội 1 - VĐV 2",
                "Điểm Đội 1",
                "Đội 2 - VĐV 1",
                "Đội 2 - VĐV 2",
                "Điểm Đội 2",
                "Đội Thắng",
            ]
        )

    return members, df_matches


members_list, matches_df = load_data()


# Hàm phụ trợ dựng khung Scoreboard chuẩn thể thao
def render_scoreboard_html(
    team1_str, score1, team2_str, score2, is_team1_winner
):
    row1_class = "winner-row" if is_team1_winner else ""
    row2_class = "" if is_team1_winner else "winner-row"

    score1_class = "score-winner" if is_team1_winner else "score-loser"
    score2_class = "score-loser" if is_team1_winner else "score-winner"

    badge1 = '<span class="badge-win">WIN</span>' if is_team1_winner else ""
    badge2 = "" if is_team1_winner else '<span class="badge-win">WIN</span>'

    html = f"""
    <div class="scoreboard-card">
        <div class="scoreboard-row {row1_class}">
            <div class="team-name">{badge1} {team1_str}</div>
            <div class="score-box {score1_class}">{score1}</div>
        </div>
        <div class="scoreboard-row {row2_class}">
            <div class="team-name">{badge2} {team2_str}</div>
            <div class="score-box {score2_class}">{score2}</div>
        </div>
    </div>
    """
    return html


# Header chính ứng dụng
st.markdown(
    """
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <span style="font-size: 2.5rem; margin-right: 15px;">🏸</span>
        <div>
            <h1 style="margin: 0; padding: 0; font-size: 2rem;">CLB Cầu Lông - Dashboard</h1>
            <p style="margin: 0; color: #6c757d;">Hệ thống theo dõi bảng xếp hạng, trận đấu và quỹ phạt</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Thanh Menu Sidebar
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2906/2906206.png", width=80
    )
    st.title("Menu Điều Hướng")
    menu = st.radio(
        "Chọn chức năng:",
        [
            "🏆 Leaderboard & Quỹ",
            "📝 Cập nhật trận đấu",
            "🛠️ Lịch sử & Quản lý trận",
            "🔍 Tìm kiếm thành viên",
            "⚙️ Quản lý thành viên",
        ],
    )
    st.markdown("---")
    st.caption("Developed with Streamlit & Google Sheets")


# ==========================================
# 1. LEADERBOARD & QUỸ
# ==========================================
if menu == "🏆 Leaderboard & Quỹ":
    st.subheader("🏆 Bảng Xếp Hạng & Quỹ Thua Trận")

    if matches_df.empty:
        st.info("💡 Chưa có dữ liệu trận đấu nào. Hãy vào phần 'Cập nhật trận đấu' để ghi nhận trận đầu tiên!")
    else:
        tab_day, tab_month, tab_all = st.tabs(
            ["📅 Xếp hạng Theo Ngày", "📆 Xếp hạng Theo Tháng", "🌟 Tổng Sắp Tất Cả"]
        )

        def calculate_leaderboard(df_filtered, show_points=False):
            stats = {
                m: {
                    "Điểm": 0,
                    "Thắng": 0,
                    "Thua": 0,
                    "Ủng Hộ Quỹ (k)": 0,
                    "Tổng Số Trận": 0,
                    "Tỷ Lệ Thắng (%)": 0.0,
                }
                for m in members_list
            }

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
                        stats[w]["Tổng Số Trận"] += 1

                for l in losers:
                    if l in stats:
                        stats[l]["Thua"] += 1
                        stats[l]["Tổng Số Trận"] += 1
                        stats[l]["Ủng Hộ Quỹ (k)"] += 10

            for m in stats:
                total = stats[m]["Tổng Số Trận"]
                if total > 0:
                    stats[m]["Tỷ Lệ Thắng (%)"] = round(
                        (stats[m]["Thắng"] / total) * 100, 1
                    )

            df_lb = pd.DataFrame.from_dict(stats, orient="index").reset_index()
            df_lb.rename(columns={"index": "Tên Thành Viên"}, inplace=True)
            df_lb.sort_values(
                by=["Thắng", "Tỷ Lệ Thắng (%)"],
                ascending=[False, False],
                inplace=True,
            )

            column_order = [
                "Tên Thành Viên",
                "Thắng",
                "Thua",
                "Ủng Hộ Quỹ (k)",
                "Tổng Số Trận",
                "Tỷ Lệ Thắng (%)",
            ]
            if show_points:
                column_order.insert(1, "Điểm")

            df_lb = df_lb[column_order]
            df_lb.reset_index(drop=True, inplace=True)

            def add_medal(index):
                if index == 0:
                    return "🥇 1"
                if index == 1:
                    return "🥈 2"
                if index == 2:
                    return "🥉 3"
                return f"  {index + 1}"

            df_lb.index = [add_medal(i) for i in range(len(df_lb))]
            return df_lb

        # --- Tab Theo Ngày (Có chọn ngày) ---
        with tab_day:
            c_date, _ = st.columns([1, 2])
            with c_date:
                selected_date = st.date_input(
                    "📅 Chọn ngày muốn xem xếp hạng:",
                    value=date.today(),
                )

            selected_date_str = selected_date.strftime("%Y-%m-%d")
            df_day = matches_df[matches_df["Ngày"] == selected_date_str]

            if df_day.empty:
                st.info(f"💡 Không có trận đấu nào diễn ra trong ngày `{selected_date_str}`.")
            else:
                df_lb_day = calculate_leaderboard(df_day, show_points=False)
                total_fund_day = df_lb_day["Ủng Hộ Quỹ (k)"].sum()
                total_matches_day = len(df_day)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">💰 Quỹ Thu Trong Ngày ({selected_date_str})</div>
                            <div class="metric-value" style="color: #2b8a3e;">{total_fund_day:,.0f}k VNĐ</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🏸 Tổng Trận Đã Đấu</div>
                            <div class="metric-value" style="color: #1c7ed6;">{total_matches_day} Trận</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.write("")
                st.dataframe(
                    df_lb_day,
                    use_container_width=True,
                    column_config={
                        "Tỷ Lệ Thắng (%)": st.column_config.ProgressColumn(
                            "Tỷ Lệ Thắng (%)", format="%.1f%%", min_value=0, max_value=100
                        ),
                        "Ủng Hộ Quỹ (k)": st.column_config.NumberColumn(
                            "Ủng Hộ Quỹ (k)", format="%d k"
                        ),
                    },
                )

        # --- Tab Theo Tháng ---
        with tab_month:
            c1, c2 = st.columns(2)
            with c1:
                selected_year = st.number_input(
                    "Chọn Năm",
                    min_value=2024,
                    max_value=2030,
                    value=datetime.now().year,
                )
            with c2:
                selected_month = st.number_input(
                    "Chọn Tháng",
                    min_value=1,
                    max_value=12,
                    value=datetime.now().month,
                )

            df_temp = matches_df.copy()
            df_temp["Ngày_dt"] = pd.to_datetime(df_temp["Ngày"])
            df_month = df_temp[
                (df_temp["Ngày_dt"].dt.month == selected_month)
                & (df_temp["Ngày_dt"].dt.year == selected_year)
            ]

            df_lb_month = calculate_leaderboard(df_month, show_points=False)
            total_fund_month = df_lb_month["Ủng Hộ Quỹ (k)"].sum()
            total_matches_month = len(df_month)

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">💰 Tổng Quỹ Thu Được (Tháng {selected_month})</div>
                        <div class="metric-value" style="color: #2b8a3e;">{total_fund_month:,.0f}k VNĐ</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🏸 Tổng Số Trận Đã Đấu</div>
                        <div class="metric-value" style="color: #1c7ed6;">{total_matches_month} Trận</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.write("")
            st.dataframe(
                df_lb_month,
                use_container_width=True,
                column_config={
                    "Tỷ Lệ Thắng (%)": st.column_config.ProgressColumn(
                        "Tỷ Lệ Thắng (%)", format="%.1f%%", min_value=0, max_value=100
                    ),
                    "Ủng Hộ Quỹ (k)": st.column_config.NumberColumn(
                        "Ủng Hộ Quỹ (k)", format="%d k"
                    ),
                },
            )

        # --- Tab Toàn Thời Gian ---
        with tab_all:
            st.write("**Bảng xếp hạng cộng dồn toàn thời gian**")
            st.dataframe(
                calculate_leaderboard(matches_df, show_points=True),
                use_container_width=True,
                column_config={
                    "Tỷ Lệ Thắng (%)": st.column_config.ProgressColumn(
                        "Tỷ Lệ Thắng (%)", format="%.1f%%", min_value=0, max_value=100
                    )
                },
            )


# ==========================================
# 2. CẬP NHẬT TRẬN ĐẤU
# ==========================================
elif menu == "📝 Cập nhật trận đấu":
    st.subheader("📝 Ghi Nhận Trận Đấu Mới (Đánh Đôi)")

    if len(members_list) < 4:
        st.warning("⚠️ Cần tối thiểu 4 thành viên trong danh sách để tổ chức trận đánh đôi!")
    else:
        with st.form("match_form", clear_on_submit=False):
            match_date = st.date_input("🗓️ Ngày Thi Đấu", value=date.today())

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    "<div class='team-card-1'><b>🔵 ĐỘI 1</b></div>",
                    unsafe_allow_html=True,
                )
                p1 = st.selectbox("Thành viên 1", members_list, index=0, key="p1")
                p2 = st.selectbox(
                    "Thành viên 2",
                    members_list,
                    index=min(1, len(members_list) - 1),
                    key="p2",
                )
                score1 = st.number_input(
                    "Điểm Số Đội 1", min_value=0, max_value=30, value=21
                )

            with col2:
                st.markdown(
                    "<div class='team-card-2'><b>🔴 ĐỘI 2</b></div>",
                    unsafe_allow_html=True,
                )
                p3 = st.selectbox(
                    "Thành viên 1",
                    members_list,
                    index=min(2, len(members_list) - 1),
                    key="p3",
                )
                p4 = st.selectbox(
                    "Thành viên 2",
                    members_list,
                    index=min(3, len(members_list) - 1),
                    key="p4",
                )
                score2 = st.number_input(
                    "Điểm Số Đội 2", min_value=0, max_value=30, value=19
                )

            st.write("")
            submitted = st.form_submit_button(
                "💾 LƯU KẾT QUẢ TRẬN ĐẤU", use_container_width=True
            )

            if submitted:
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error("❌ Lỗi: Có VĐV bị chọn trùng tên! Vui lòng chọn 4 người khác nhau.")
                elif score1 == score2:
                    st.error("❌ Lỗi: Điểm số hai đội không được bằng nhau (Không có tỉ số hòa).")
                else:
                    winner = "Đội 1" if score1 > score2 else "Đội 2"
                    new_match = {
                        "Ngày": match_date.strftime("%Y-%m-%d"),
                        "Đội 1 - VĐV 1": p1,
                        "Đội 1 - VĐV 2": p2,
                        "Điểm Đội 1": int(score1),
                        "Đội 2 - VĐV 1": p3,
                        "Đội 2 - VĐV 2": p4,
                        "Điểm Đội 2": int(score2),
                        "Đội Thắng": winner,
                    }
                    requests.post(
                        SCRIPT_URL,
                        json={"action": "add_match", "match": new_match},
                    )
                    st.success(f"🎉 Đã lưu thành công! **{winner}** chiến thắng ({score1} - {score2})")
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 3. LỊCH SỬ & QUẢN LÝ TRẬN
# ==========================================
elif menu == "🛠️ Lịch sử & Quản lý trận":
    st.subheader("🛠️ Lịch Sử & Quản Lý Trận Đấu")

    if matches_df.empty:
        st.info("Chưa có trận đấu nào trong hệ thống.")
    else:
        st.caption("Danh sách trận đấu được hiển thị theo giao diện Scoreboard thi đấu:")

        for idx, row in matches_df.iterrows():
            col_info, col_del = st.columns([6, 1])

            team1_str = f"{row['Đội 1 - VĐV 1']} / {row['Đội 1 - VĐV 2']}"
            team2_str = f"{row['Đội 2 - VĐV 1']} / {row['Đội 2 - VĐV 2']}"
            score1 = row["Điểm Đội 1"]
            score2 = row["Điểm Đội 2"]
            is_team1_winner = row["Đội Thắng"] == "Đội 1"

            with col_info:
                st.caption(f"📅 **Ngày:** `{row['Ngày']}`")
                st.markdown(
                    render_scoreboard_html(
                        team1_str, score1, team2_str, score2, is_team1_winner
                    ),
                    unsafe_allow_html=True,
                )

            with col_del:
                st.write("")
                st.write("")
                sheet_row = idx + 2
                if st.button("🗑️ Xóa", key=f"del_match_{idx}"):
                    requests.post(
                        SCRIPT_URL,
                        json={"action": "delete_match", "row_index": sheet_row},
                    )
                    st.toast("Đã xóa trận đấu thành công!", icon="✅")
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 4. TÌM KIẾM THÀNH VIÊN
# ==========================================
elif menu == "🔍 Tìm kiếm thành viên":
    st.subheader("🔍 Hồ Sơ & Lịch Sử Thi Đấu Thành Viên")

    if not members_list:
        st.warning("Chưa có thành viên nào!")
    else:
        selected_member = st.selectbox(
            "🔎 Chọn thành viên muốn tra cứu:", members_list
        )

        df_matches = matches_df.copy()

        filter_condition = (
            (df_matches["Đội 1 - VĐV 1"] == selected_member)
            | (df_matches["Đội 1 - VĐV 2"] == selected_member)
            | (df_matches["Đội 2 - VĐV 1"] == selected_member)
            | (df_matches["Đội 2 - VĐV 2"] == selected_member)
        ) if not df_matches.empty else pd.Series([], dtype=bool)

        user_matches = (
            df_matches[filter_condition].copy()
            if not df_matches.empty
            else pd.DataFrame()
        )

        today_str = date.today().strftime("%Y-%m-%d")
        now = datetime.now()

        win_today = lose_today = win_month = lose_month = 0

        if not user_matches.empty:
            user_matches["Ngày_dt"] = pd.to_datetime(user_matches["Ngày"])

            for _, row in user_matches.iterrows():
                is_team1 = selected_member in [
                    row["Đội 1 - VĐV 1"],
                    row["Đội 1 - VĐV 2"],
                ]
                is_winner = (is_team1 and row["Đội Thắng"] == "Đội 1") or (
                    not is_team1 and row["Đội Thắng"] == "Đội 2"
                )

                if row["Ngày"] == today_str:
                    if is_winner:
                        win_today += 1
                    else:
                        lose_today += 1

                if (
                    row["Ngày_dt"].month == now.month
                    and row["Ngày_dt"].year == now.year
                ):
                    if is_winner:
                        win_month += 1
                    else:
                        lose_month += 1

        fine_today = lose_today * 10
        fine_month = lose_month * 10

        st.write("")
        c_today, c_month = st.columns(2)

        with c_today:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">📊 Báo Cáo Hôm Nay ({today_str})</div>
                    <div style="font-size: 1.1rem; margin-top: 5px;">
                        • Thắng: <b>{win_today}</b> | Thua: <b>{lose_today}</b><br>
                        • Quỹ ủng hộ: <b style="color:#f03e3e;">{fine_today}k VNĐ</b>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with c_month:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">📈 Báo Cáo Tháng {now.month}/{now.year}</div>
                    <div style="font-size: 1.1rem; margin-top: 5px;">
                        • Thắng: <b>{win_month}</b> | Thua: <b>{lose_month}</b><br>
                        • Quỹ ủng hộ: <b style="color:#f03e3e;">{fine_month}k VNĐ</b>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.write("### 📜 Lịch Sử Trận Đấu Đã Tham Gia")

        if user_matches.empty:
            st.info("Thành viên này chưa tham gia trận đấu nào.")
        else:
            grouped = user_matches.groupby("Ngày", sort=False)

            for match_date, group in grouped:
                st.markdown(f"##### 🗓️ Ngày: `{match_date}`")

                for _, row in group.iterrows():
                    team1_str = (
                        f"{row['Đội 1 - VĐV 1']} / {row['Đội 1 - VĐV 2']}"
                    )
                    team2_str = (
                        f"{row['Đội 2 - VĐV 1']} / {row['Đội 2 - VĐV 2']}"
                    )
                    score1 = row["Điểm Đội 1"]
                    score2 = row["Điểm Đội 2"]
                    is_team1_winner = row["Đội Thắng"] == "Đội 1"

                    st.markdown(
                        render_scoreboard_html(
                            team1_str,
                            score1,
                            team2_str,
                            score2,
                            is_team1_winner,
                        ),
                        unsafe_allow_html=True,
                    )


# ==========================================
# 5. QUẢN LÝ THÀNH VIÊN
# ==========================================
elif menu == "⚙️ Quản lý thành viên":
    st.subheader("⚙️ Quản Lý Danh Sách Thành Viên")

    col_add, col_list = st.columns([1, 1])

    with col_add:
        st.write("### ➕ Thêm Thành Viên")
        with st.form("add_member_form", clear_on_submit=True):
            new_name = st.text_input("Họ và Tên thành viên:")
            add_btn = st.form_submit_button(
                "Thêm mới", use_container_width=True
            )

            if add_btn:
                name_clean = new_name.strip()
                if name_clean == "":
                    st.warning("Vui lòng nhập tên!")
                elif name_clean in members_list:
                    st.error("Thành viên này đã tồn tại!")
                else:
                    payload = {"action": "add_member", "name": name_clean}
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast(
                        f"Đã thêm thành viên **{name_clean}**!", icon="✅"
                    )
                    st.cache_data.clear()
                    st.rerun()

    with col_list:
        st.write("### 📋 Danh Sách Hiện Tại")
        if not members_list:
            st.info("Chưa có thành viên nào.")
        else:
            for idx, member in enumerate(members_list):
                c_name, c_btn = st.columns([3, 1])
                c_name.write(f"**{idx + 1}. {member}**")
                if c_btn.button("🗑️ Xóa", key=f"del_mem_{idx}"):
                    payload = {"action": "delete_member", "name": member}
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast(f"Đã xóa **{member}**!", icon="🗑️")
                    st.cache_data.clear()
                    st.rerun()
