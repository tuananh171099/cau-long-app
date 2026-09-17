from datetime import date, datetime
import re
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="CLB Cầu Lông - HVBADMINTON",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #212529;
    }
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
    .scoreboard-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 6px;
    }
    .scoreboard-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 14px;
        border-bottom: 1px solid #f0f0f0;
    }
    .scoreboard-row:last-child {
        border-bottom: none;
    }
    .team-name {
        font-size: 1rem;
        font-weight: 600;
        color: #495057;
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
    }
    </style>
""",
    unsafe_allow_html=True,
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx56axOdpQ-pRGzV1UWbaE3t88ATfMdWeVY_VZCJ6WKv_mtM_7DOJYZ0jMlyctJ-cGqPg/exec"


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
        members = (
            df_m["Tên Thành Viên"].dropna().astype(str).str.strip().tolist()
        )
    except Exception:
        members = ["Nguyễn Văn A", "Trần Văn B", "Lê Thị C", "Phạm Văn D"]

    try:
        url_matches = get_sheet_csv_url(SHEET_URL, "Matches")
        df_matches = pd.read_csv(url_matches)
    except Exception:
        df_matches = pd.DataFrame()

    return members, df_matches


members_list, matches_df = load_data()


def to_int(val, default=0):
    try:
        if pd.notna(val):
            return int(float(val))
    except Exception:
        pass
    return default


def get_val(row, key, col_idx, default=""):
    if key in row and pd.notna(row[key]):
        return row[key]
    if len(row) > col_idx and pd.notna(row.iloc[col_idx]):
        return row.iloc[col_idx]
    return default


def parse_match_row(row):
    match_date = str(get_val(row, "Ngày", 0, "")).strip()
    p1_1 = str(get_val(row, "Đội 1 - VĐV 1", 1, "")).strip()
    k1_1 = to_int(get_val(row, "Kèo 1_1", 2, 1), 1)
    p1_2 = str(get_val(row, "Đội 1 - VĐV 2", 3, "")).strip()
    k1_2 = to_int(get_val(row, "Kèo 1_2", 4, 1), 1)
    score1 = to_int(get_val(row, "Điểm Đội 1", 5, 0), 0)

    p2_1 = str(get_val(row, "Đội 2 - VĐV 1", 6, "")).strip()
    k2_1 = to_int(get_val(row, "Kèo 2_1", 7, 1), 1)
    p2_2 = str(get_val(row, "Đội 2 - VĐV 2", 8, "")).strip()
    k2_2 = to_int(get_val(row, "Kèo 2_2", 9, 1), 1)
    score2 = to_int(get_val(row, "Điểm Đội 2", 10, 0), 0)

    winner = str(get_val(row, "Đội Thắng", 11, "")).strip()
    video_url = str(get_val(row, "Video", 12, "")).strip()

    if not winner:
        winner = "Đội 1" if score1 > score2 else "Đội 2"

    return {
        "date": match_date,
        "p1_1": p1_1,
        "k1_1": k1_1,
        "p1_2": p1_2,
        "k1_2": k1_2,
        "score1": score1,
        "p2_1": p2_1,
        "k2_1": k2_1,
        "p2_2": p2_2,
        "k2_2": k2_2,
        "score2": score2,
        "winner": winner,
        "video_url": video_url,
    }


def render_scoreboard_html(
    team1_str, score1, team2_str, score2, is_team1_winner
):
    row1_class = "winner-row" if is_team1_winner else ""
    row2_class = "" if is_team1_winner else "winner-row"

    score1_class = "score-winner" if is_team1_winner else "score-loser"
    score2_class = "score-loser" if is_team1_winner else "score-winner"

    badge1 = '<span class="badge-win">WIN</span>' if is_team1_winner else ""
    badge2 = "" if is_team1_winner else '<span class="badge-win">WIN</span>'

    return f"""
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


# Hàm phát video YouTube chuẩn mượt không bị vướng controls
def render_youtube_player(url):
    video_id = None
    # Trích xuất Video ID từ link YouTube
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            video_id = match.group(1)
            break

    if video_id:
        embed_html = f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; margin-top: 10px; margin-bottom: 10px;">
            <iframe src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
        """
        st.markdown(embed_html, unsafe_allow_html=True)
    else:
        st.video(url)


# Header
st.markdown(
    """
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <span style="font-size: 2.5rem; margin-right: 15px;">🏸</span>
        <div>
            <h1 style="margin: 0; padding: 0; font-size: 2rem;">CLB Cầu Lông - HVBADMINTON</h1>
            <p style="margin: 0; color: #6c757d;">Hệ thống theo dõi bảng xếp hạng và trận đấu</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2906/2906206.png", width=80
    )
    st.title("Menu")
    menu = st.radio(
        "Chọn chức năng:",
        [
            "🏆 Bảng Xếp Hạng",
            "📝 Cập nhật trận đấu",
            "🛠️ Lịch sử các trận đấu",
            "🔍 Tìm kiếm thành viên",
            "⚙️ Quản lý thành viên",
        ],
    )
    st.markdown("---")
    st.caption("✨ **Created by NTA**")


# ==========================================
# 1. BẢNG XẾP HẠNG
# ==========================================
if menu == "🏆 Bảng Xếp Hạng":
    st.subheader("🏆 Bảng Xếp Hạng")

    if matches_df.empty:
        st.info(
            "💡 Chưa có dữ liệu trận đấu nào. Hãy vào phần 'Cập nhật trận đấu' để"
            " ghi nhận trận đầu tiên!"
        )
    else:
        tab_day, tab_month, tab_all = st.tabs(
            [
                "📅 Xếp hạng Theo Ngày",
                "📆 Xếp hạng Theo Tháng",
                "🌟 Tổng Sắp Tất Cả",
            ]
        )

        def calculate_leaderboard(df_filtered, show_points=False):
            stats = {
                m: {
                    "Điểm": 0,
                    "Thắng": 0,
                    "Thua": 0,
                    "Điểm thành viên": 0,
                    "Tổng Số Trận": 0,
                    "Tỷ Lệ Thắng (%)": 0.0,
                }
                for m in members_list
            }

            for _, row in df_filtered.iterrows():
                m_info = parse_match_row(row)

                is_team1_win = (m_info["winner"] == "Đội 1") or (
                    m_info["score1"] > m_info["score2"]
                )

                if is_team1_win:
                    winners = [m_info["p1_1"], m_info["p1_2"]]
                    losers = [
                        (m_info["p2_1"], m_info["k2_1"]),
                        (m_info["p2_2"], m_info["k2_2"]),
                    ]
                else:
                    winners = [m_info["p2_1"], m_info["p2_2"]]
                    losers = [
                        (m_info["p1_1"], m_info["k1_1"]),
                        (m_info["p1_2"], m_info["k1_2"]),
                    ]

                for w in winners:
                    if w in stats:
                        stats[w]["Điểm"] += 3
                        stats[w]["Thắng"] += 1
                        stats[w]["Tổng Số Trận"] += 1

                for l_player, l_bet in losers:
                    if l_player in stats:
                        stats[l_player]["Thua"] += 1
                        stats[l_player]["Tổng Số Trận"] += 1
                        stats[l_player]["Điểm thành viên"] += l_bet

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
                "Điểm thành viên",
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

        # Tab Ngày
        with tab_day:
            c_date, _ = st.columns([1, 2])
            with c_date:
                selected_date = st.date_input(
                    "📅 Chọn ngày muốn xem xếp hạng:", value=date.today()
                )

            selected_date_str = selected_date.strftime("%Y-%m-%d")

            df_day = pd.DataFrame()
            if not matches_df.empty:
                df_day = matches_df[
                    matches_df.apply(
                        lambda r: parse_match_row(r)["date"]
                        == selected_date_str,
                        axis=1,
                    )
                ]

            if df_day.empty:
                st.info(
                    "💡 Không có trận đấu nào diễn ra trong ngày"
                    f" `{selected_date_str}`."
                )
            else:
                df_lb_day = calculate_leaderboard(df_day, show_points=False)
                total_fund_day = df_lb_day["Điểm thành viên"].sum()
                total_matches_day = len(df_day)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🎯 Tổng Điểm ({selected_date_str})</div>
                            <div class="metric-value" style="color: #2b8a3e;">{total_fund_day:,.0f}</div>
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
                            "Tỷ Lệ Thắng (%)",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "Điểm thành viên": st.column_config.NumberColumn(
                            "Điểm thành viên", format="%d"
                        ),
                    },
                )

        # Tab Tháng
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

            df_month = pd.DataFrame()
            if not matches_df.empty:

                def is_in_month(row):
                    d_str = parse_match_row(row)["date"]
                    try:
                        dt = datetime.strptime(d_str, "%Y-%m-%d")
                        return (
                            dt.month == selected_month
                            and dt.year == selected_year
                        )
                    except Exception:
                        return False

                df_month = matches_df[matches_df.apply(is_in_month, axis=1)]

            df_lb_month = calculate_leaderboard(df_month, show_points=False)
            total_fund_month = df_lb_month["Điểm thành viên"].sum()
            total_matches_month = len(df_month)

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🎯 Tổng Điểm (Tháng {selected_month})</div>
                        <div class="metric-value" style="color: #2b8a3e;">{total_fund_month:,.0f}</div>
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
                    "Điểm thành viên": st.column_config.NumberColumn(
                        "Điểm thành viên", format="%d"
                    ),
                },
            )

        # Tab All
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
        st.warning(
            "⚠️ Cần tối thiểu 4 VĐV trong danh sách để tổ chức trận đánh đôi!"
        )
    else:
        with st.form("match_form", clear_on_submit=False):
            match_date = st.date_input("🗓️ Ngày Thi Đấu", value=date.today())

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    "<div class='team-card-1'><b>🔵 ĐỘI 1</b></div>",
                    unsafe_allow_html=True,
                )
                cp1_name, cp1_bet = st.columns([2.5, 1])
                with cp1_name:
                    p1 = st.selectbox("VĐV 1", members_list, index=0, key="p1")
                with cp1_bet:
                    k1_1 = st.number_input(
                        "Điểm",
                        min_value=0,
                        max_value=10,
                        value=1,
                        step=1,
                        key="k1_1",
                    )

                cp2_name, cp2_bet = st.columns([2.5, 1])
                with cp2_name:
                    p2 = st.selectbox(
                        "VĐV 2",
                        members_list,
                        index=min(1, len(members_list) - 1),
                        key="p2",
                    )
                with cp2_bet:
                    k1_2 = st.number_input(
                        "Điểm",
                        min_value=0,
                        max_value=10,
                        value=1,
                        step=1,
                        key="k1_2",
                    )

                score1 = st.number_input(
                    "Điểm Số Đội 1", min_value=0, max_value=30, value=21
                )

            with col2:
                st.markdown(
                    "<div class='team-card-2'><b>🔴 ĐỘI 2</b></div>",
                    unsafe_allow_html=True,
                )
                cp3_name, cp3_bet = st.columns([2.5, 1])
                with cp3_name:
                    p3 = st.selectbox(
                        "VĐV 1",
                        members_list,
                        index=min(2, len(members_list) - 1),
                        key="p3",
                    )
                with cp3_bet:
                    k2_1 = st.number_input(
                        "Điểm",
                        min_value=0,
                        max_value=10,
                        value=1,
                        step=1,
                        key="k2_1",
                    )

                cp4_name, cp4_bet = st.columns([2.5, 1])
                with cp4_name:
                    p4 = st.selectbox(
                        "VĐV 2",
                        members_list,
                        index=min(3, len(members_list) - 1),
                        key="p4",
                    )
                with cp4_bet:
                    k2_2 = st.number_input(
                        "Điểm",
                        min_value=0,
                        max_value=10,
                        value=1,
                        step=1,
                        key="k2_2",
                    )

                score2 = st.number_input(
                    "Điểm Số Đội 2", min_value=0, max_value=30, value=19
                )

            video_input = st.text_input(
                "🎥 Link Video YouTube Trận Đấu (Không bắt buộc):",
                placeholder="https://www.youtube.com/watch?v=...",
            )

            st.write("")
            submitted = st.form_submit_button(
                "💾 LƯU KẾT QUẢ TRẬN ĐẤU", use_container_width=True
            )

            if submitted:
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error(
                        "❌ Lỗi: Có VĐV bị chọn trùng tên! Vui lòng chọn 4 VĐV"
                        " khác nhau."
                    )
                elif score1 == score2:
                    st.error(
                        "❌ Lỗi: Điểm số hai đội không được bằng nhau (Không"
                        " có tỉ số hòa)."
                    )
                else:
                    winner = "Đội 1" if int(score1) > int(score2) else "Đội 2"
                    new_match = {
                        "Ngày": match_date.strftime("%Y-%m-%d"),
                        "Đội 1 - VĐV 1": p1,
                        "Kèo 1_1": int(k1_1),
                        "Đội 1 - VĐV 2": p2,
                        "Kèo 1_2": int(k1_2),
                        "Điểm Đội 1": int(score1),
                        "Đội 2 - VĐV 1": p3,
                        "Kèo 2_1": int(k2_1),
                        "Đội 2 - VĐV 2": p4,
                        "Kèo 2_2": int(k2_2),
                        "Điểm Đội 2": int(score2),
                        "Đội Thắng": winner,
                        "Video": video_input.strip(),
                    }
                    requests.post(
                        SCRIPT_URL,
                        json={"action": "add_match", "match": new_match},
                    )

                    st.balloons()
                    st.success(
                        "✅ **ĐÃ LƯU TRẬN ĐẤU THÀNH CÔNG!**\n\n🏆 **Đội"
                        f" thắng:** {winner} ({score1} - {score2})"
                    )
                    time.sleep(2.5)
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 3. LỊCH SỬ CÁC TRẬN ĐẤU
# ==========================================
elif menu == "🛠️ Lịch sử các trận đấu":
    st.subheader("🛠️ Lịch Sử Các Trận Đấu")

    if matches_df.empty:
        st.info("Chưa có trận đấu nào trong hệ thống.")
    else:
        matches_parsed = []
        for idx, row in matches_df.iterrows():
            m = parse_match_row(row)
            m["row_index"] = idx + 2
            matches_parsed.append(m)

        df_p = pd.DataFrame(matches_parsed)
        grouped = df_p.groupby("date", sort=False)

        for match_date, group in grouped:
            st.markdown(f"#### 🗓️ Ngày: `{match_date}`")

            for _, m in group.iterrows():
                team1_str = f"{m['p1_1']} / {m['p1_2']}"
                team2_str = f"{m['p2_1']} / {m['p2_2']}"

                is_team1_winner = (m["winner"] == "Đội 1") or (
                    m["score1"] > m["score2"]
                )

                col_info, col_del = st.columns([6, 1])

                with col_info:
                    st.markdown(
                        render_scoreboard_html(
                            team1_str,
                            m["score1"],
                            team2_str,
                            m["score2"],
                            is_team1_winner,
                        ),
                        unsafe_allow_html=True,
                    )
                    with st.expander("🔍 Chi tiết trận đấu & Video YouTube"):
                        st.write(
                            f"• **Đội 1:** {m['p1_1']} (`{m['k1_1']} điểm`)"
                            f" | {m['p1_2']} (`{m['k1_2']} điểm`)\n• **Đội"
                            f" 2:** {m['p2_1']} (`{m['k2_1']} điểm`) |"
                            f" {m['p2_2']} (`{m['k2_2']} điểm`)"
                        )

                        # Hiển thị Video phát chuẩn YouTube
                        if m["video_url"]:
                            st.write("🎬 **Video trận đấu:**")
                            render_youtube_player(m["video_url"])

                        # Form chỉnh sửa link video
                        with st.form(f"form_vid_{m['row_index']}"):
                            v_link = st.text_input(
                                "🔗 Chỉnh sửa / Điền link YouTube:",
                                value=m["video_url"],
                                key=f"v_in_{m['row_index']}",
                            )
                            save_v_btn = st.form_submit_button(
                                "💾 Lưu Video Trận Đấu"
                            )
                            if save_v_btn:
                                requests.post(
                                    SCRIPT_URL,
                                    json={
                                        "action": "update_video",
                                        "row_index": m["row_index"],
                                        "video_url": v_link.strip(),
                                    },
                                )
                                st.toast(
                                    "Đã lưu link Video thành công!", icon="✅"
                                )
                                st.cache_data.clear()
                                st.rerun()

                with col_del:
                    if st.button("🗑️ Xóa", key=f"del_match_{m['row_index']}"):
                        requests.post(
                            SCRIPT_URL,
                            json={
                                "action": "delete_match",
                                "row_index": m["row_index"],
                            },
                        )
                        st.toast("Đã xóa trận đấu thành công!", icon="✅")
                        st.cache_data.clear()
                        st.rerun()


# ==========================================
# 4. TÌM KIẾM THÀNH VIÊN
# ==========================================
elif menu == "🔍 Tìm kiếm thành viên":
    st.subheader("🔍 Hồ Sơ & Lịch Sử Thi Đấu VĐV")

    if not members_list:
        st.warning("Chưa có VĐV nào!")
    else:
        selected_member = st.selectbox(
            "🔎 Chọn VĐV muốn tra cứu:", members_list
        )

        user_matches = []
        if not matches_df.empty:
            for idx, row in matches_df.iterrows():
                m = parse_match_row(row)
                if selected_member in [
                    m["p1_1"],
                    m["p1_2"],
                    m["p2_1"],
                    m["p2_2"],
                ]:
                    user_matches.append(m)

        today_str = date.today().strftime("%Y-%m-%d")
        now = datetime.now()

        win_today = lose_today = fine_today = 0
        win_month = lose_month = fine_month = 0

        for m in user_matches:
            is_team1 = selected_member in [m["p1_1"], m["p1_2"]]
            is_winner = (
                is_team1 and (m["winner"] == "Đội 1" or m["score1"] > m["score2"])
            ) or (
                not is_team1
                and (m["winner"] == "Đội 2" or m["score2"] > m["score1"])
            )

            bet_amount = 1
            if selected_member == m["p1_1"]:
                bet_amount = m["k1_1"]
            elif selected_member == m["p1_2"]:
                bet_amount = m["k1_2"]
            elif selected_member == m["p2_1"]:
                bet_amount = m["k2_1"]
            elif selected_member == m["p2_2"]:
                bet_amount = m["k2_2"]

            if m["date"] == today_str:
                if is_winner:
                    win_today += 1
                else:
                    lose_today += 1
                    fine_today += bet_amount

            try:
                dt = datetime.strptime(m["date"], "%Y-%m-%d")
                if dt.month == now.month and dt.year == now.year:
                    if is_winner:
                        win_month += 1
                    else:
                        lose_month += 1
                        fine_month += bet_amount
            except Exception:
                pass

        st.write("")
        c_today, c_month = st.columns(2)

        with c_today:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">📊 Báo Cáo Hôm Nay ({today_str})</div>
                    <div style="font-size: 1.1rem; margin-top: 5px;">
                        • Thắng: <b>{win_today}</b> | Thua: <b>{lose_today}</b><br>
                        • Điểm tích lũy thua: <b style="color:#f03e3e;">{fine_today}</b>
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
                        • Điểm tích lũy thua: <b style="color:#f03e3e;">{fine_month}</b>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.write("### 📜 Lịch Sử Trận Đấu Đã Tham Gia")

        if not user_matches:
            st.info("VĐV này chưa tham gia trận đấu nào.")
        else:
            df_um = pd.DataFrame(user_matches)
            grouped = df_um.groupby("date", sort=False)

            for match_date, group in grouped:
                st.markdown(f"##### 🗓️ Ngày: `{match_date}`")

                for _, m in group.iterrows():
                    team1_str = f"{m['p1_1']} / {m['p1_2']}"
                    team2_str = f"{m['p2_1']} / {m['p2_2']}"

                    is_team1_winner = (m["winner"] == "Đội 1") or (
                        m["score1"] > m["score2"]
                    )

                    st.markdown(
                        render_scoreboard_html(
                            team1_str,
                            m["score1"],
                            team2_str,
                            m["score2"],
                            is_team1_winner,
                        ),
                        unsafe_allow_html=True,
                    )
                    with st.expander("🔍 Chi tiết trận đấu & Video"):
                        st.write(
                            f"• **Đội 1:** {m['p1_1']} (`{m['k1_1']} điểm`)"
                            f" | {m['p1_2']} (`{m['k1_2']} điểm`)\n• **Đội"
                            f" 2:** {m['p2_1']} (`{m['k2_1']} điểm`) |"
                            f" {m['p2_2']} (`{m['k2_2']} điểm`)"
                        )
                        if m["video_url"]:
                            st.write("🎬 **Video trận đấu:**")
                            render_youtube_player(m["video_url"])


# ==========================================
# 5. QUẢN LÝ THÀNH VIÊN
# ==========================================
elif menu == "⚙️ Quản lý thành viên":
    st.subheader("⚙️ Quản Lý Danh Sách VĐV")

    col_add, col_list = st.columns([1, 1])

    with col_add:
        st.write("### ➕ Thêm VĐV Mới")
        with st.form("add_member_form", clear_on_submit=True):
            new_name = st.text_input("Họ và Tên VĐV:")
            add_btn = st.form_submit_button(
                "Thêm mới", use_container_width=True
            )

            if add_btn:
                name_clean = new_name.strip()
                if name_clean == "":
                    st.warning("Vui lòng nhập tên!")
                elif name_clean in members_list:
                    st.error("VĐV này đã tồn tại!")
                else:
                    payload = {"action": "add_member", "name": name_clean}
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast(f"Đã thêm VĐV **{name_clean}**!", icon="✅")
                    st.cache_data.clear()
                    st.rerun()

    with col_list:
        st.write("### 📋 Danh Sách Hiện Tại")
        if not members_list:
            st.info("Chưa có VĐV nào.")
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
