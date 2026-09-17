from datetime import date, datetime
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
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxbn2We-c4JNS7WFe3aJeHZP5pzohHugzFvKlnmy9jT2vmMy1nfwuqtOhrMx_n69KvP0g/exec"


def format_date_vn(dt_val):
    """Chuyển đổi các định dạng ngày về chuẩn dd/mm/yyyy"""
    if not dt_val:
        return ""
    if isinstance(dt_val, (date, datetime)):
        return dt_val.strftime("%d/%m/%Y")
    
    val_str = str(dt_val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(val_str, fmt).strftime("%d/%m/%Y")
        except Exception:
            pass
    return val_str


def parse_date_obj(dt_val):
    """Parse ngày về datetime object để sắp xếp"""
    if isinstance(dt_val, (date, datetime)):
        return datetime.combine(dt_val, datetime.min.time())
    val_str = str(dt_val).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(val_str, fmt)
        except Exception:
            pass
    return datetime.min


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
        members = df_m["Tên Thành Viên"].dropna().astype(str).str.strip().tolist()
    except Exception:
        members = ["Nguyễn Văn A", "Trần Văn B", "Lê Thị C", "Phạm Văn D"]

    try:
        url_matches = get_sheet_csv_url(SHEET_URL, "Matches")
        df_matches = pd.read_csv(url_matches)
    except Exception:
        df_matches = pd.DataFrame()

    try:
        url_seasons = get_sheet_csv_url(SHEET_URL, "Seasons")
        df_seasons = pd.read_csv(url_seasons)
    except Exception:
        df_seasons = pd.DataFrame(columns=["Tên Mùa", "Ngày Bắt Đầu", "Ngày Kết Thúc", "Trạng Thái"])

    return members, df_matches, df_seasons


members_list, matches_df, seasons_df = load_data()


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
    raw_date = get_val(row, "Ngày", 0, "")
    match_date = format_date_vn(raw_date)
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
    season_name = str(get_val(row, "Mùa Giải", 13, "")).strip()

    if not winner:
        winner = "Đội 1" if score1 > score2 else "Đội 2"

    return {
        "date": match_date,
        "date_obj": parse_date_obj(raw_date),
        "p1_1": p1_1, "k1_1": k1_1,
        "p1_2": p1_2, "k1_2": k1_2,
        "score1": score1,
        "p2_1": p2_1, "k2_1": k2_1,
        "p2_2": p2_2, "k2_2": k2_2,
        "score2": score2,
        "winner": winner,
        "video_url": video_url,
        "season": season_name
    }


def render_scoreboard_html(team1_str, score1, team2_str, score2, is_team1_winner):
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
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906206.png", width=80)
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

    seasons_list = seasons_df["Tên Mùa"].dropna().tolist() if not seasons_df.empty else ["Mùa 1 (2026)"]

    c_season, c_end, c_pop = st.columns([2.5, 1.2, 1])

    with c_season:
        selected_season = st.selectbox("Mùa Giải:", seasons_list, index=len(seasons_list) - 1 if seasons_list else 0)

    with c_end:
        st.write("")
        st.write("")
        if st.button(f"🛑 Kết thúc {selected_season}", use_container_width=True):
            requests.post(
                SCRIPT_URL,
                json={
                    "action": "end_season",
                    "season_name": selected_season,
                    "end_date": format_date_vn(date.today())
                }
            )
            st.toast(f"Đã kết thúc {selected_season}!", icon="✅")
            st.cache_data.clear()
            st.rerun()

    with c_pop:
        st.write("")
        st.write("")
        with st.popover("⚙️ Tùy Chỉnh Mùa"):
            st.markdown("### ➕ Thêm Mùa Mới")
            with st.form("add_season_form", clear_on_submit=True):
                new_s_name = st.text_input("Tên Mùa Giải Mới:", placeholder=f"Mùa {len(seasons_list)+1} (2026)")
                s_start_date = st.date_input("🗓️ Ngày Bắt Đầu Mùa", value=date.today(), format="DD/MM/YYYY")
                create_s_btn = st.form_submit_button("Thêm Mùa Mới", use_container_width=True)

                if create_s_btn:
                    s_name_final = new_s_name.strip() if new_s_name.strip() else f"Mùa {len(seasons_list)+1} (2026)"
                    if s_name_final in seasons_list:
                        st.error("❌ Tên mùa giải đã tồn tại!")
                    else:
                        requests.post(
                            SCRIPT_URL,
                            json={
                                "action": "add_season",
                                "season_name": s_name_final,
                                "start_date": format_date_vn(s_start_date)
                            }
                        )
                        st.toast(f"Đã tạo {s_name_final}!", icon="🎉")
                        st.cache_data.clear()
                        st.rerun()

            st.markdown("---")
            st.markdown(f"### ✏️ Sửa Tên {selected_season}")
            with st.form("edit_season_form"):
                rename_val = st.text_input("Tên Mới:", value=selected_season)
                save_rename = st.form_submit_button("Lưu Tên Mới", use_container_width=True)
                if save_rename:
                    if rename_val.strip() and rename_val.strip() != selected_season:
                        requests.post(
                            SCRIPT_URL,
                            json={
                                "action": "edit_season",
                                "old_name": selected_season,
                                "new_name": rename_val.strip()
                            }
                        )
                        st.toast("Đã đổi tên mùa thành công!", icon="✅")
                        st.cache_data.clear()
                        st.rerun()

            st.markdown("---")
            st.markdown(f"### 🗑️ Xóa {selected_season}")
            if st.button("Xóa Mùa Này", use_container_width=True):
                requests.post(
                    SCRIPT_URL,
                    json={
                        "action": "delete_season",
                        "season_name": selected_season
                    }
                )
                st.toast(f"Đã xóa {selected_season}!", icon="🗑️")
                st.cache_data.clear()
                st.rerun()

    df_season_matches = pd.DataFrame()
    if not matches_df.empty:
        df_season_matches = matches_df[
            matches_df.apply(lambda r: parse_match_row(r)["season"] == selected_season, axis=1)
        ]

    if df_season_matches.empty:
        st.info(f"💡 Chưa có dữ liệu trận đấu nào trong `{selected_season}`.")
    else:
        tab_day, tab_month, tab_all = st.tabs(
            ["📅 Xếp hạng Theo Ngày", "📆 Xếp hạng Theo Tháng", "🌟 Bảng Xếp Hạng Mùa"]
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
                is_team1_win = (m_info["winner"] == "Đội 1") or (m_info["score1"] > m_info["score2"])

                if is_team1_win:
                    winners = [m_info["p1_1"], m_info["p1_2"]]
                    losers = [(m_info["p2_1"], m_info["k2_1"]), (m_info["p2_2"], m_info["k2_2"])]
                else:
                    winners = [m_info["p2_1"], m_info["p2_2"]]
                    losers = [(m_info["p1_1"], m_info["k1_1"]), (m_info["p1_2"], m_info["k1_2"])]

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
                    stats[m]["Tỷ Lệ Thắng (%)"] = round((stats[m]["Thắng"] / total) * 100, 1)

            df_lb = pd.DataFrame.from_dict(stats, orient="index").reset_index()
            df_lb.rename(columns={"index": "Tên Thành Viên"}, inplace=True)
            df_lb.sort_values(by=["Thắng", "Tỷ Lệ Thắng (%)"], ascending=[False, False], inplace=True)

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
                selected_date = st.date_input("📅 Chọn ngày muốn xem xếp hạng:", value=date.today(), format="DD/MM/YYYY")

            selected_date_str = format_date_vn(selected_date)

            df_day = df_season_matches[
                df_season_matches.apply(lambda r: parse_match_row(r)["date"] == selected_date_str, axis=1)
            ]

            if df_day.empty:
                st.info(f"💡 Không có trận đấu nào trong ngày `{selected_date_str}` của mùa `{selected_season}`.")
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
                            "Tỷ Lệ Thắng (%)", format="%.1f%%", min_value=0, max_value=100
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
                selected_year = st.number_input("Chọn Năm", min_value=2024, max_value=2030, value=datetime.now().year)
            with c2:
                selected_month = st.number_input("Chọn Tháng", min_value=1, max_value=12, value=datetime.now().month)

            def is_in_month(row):
                m_info = parse_match_row(row)
                dt = m_info["date_obj"]
                return dt.month == selected_month and dt.year == selected_year

            df_month = df_season_matches[df_season_matches.apply(is_in_month, axis=1)]

            df_lb_month = calculate_leaderboard(df_month, show_points=False)
            total_fund_month = df_lb_month["Điểm thành viên"].sum()
            total_matches_month = len(df_month)

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🎯 Tổng Điểm (Tháng {selected_month}/{selected_year})</div>
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

        # Tab Toàn mùa
        with tab_all:
            st.write(f"**Bảng xếp hạng tổng quát của `{selected_season}`**")
            st.dataframe(
                calculate_leaderboard(df_season_matches, show_points=True),
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

    seasons_list = seasons_df["Tên Mùa"].dropna().tolist() if not seasons_df.empty else ["Mùa 1 (2026)"]
    current_season = seasons_list[-1] if seasons_list else "Mùa 1 (2026)"

    if len(members_list) < 4:
        st.warning("⚠️ Cần tối thiểu 4 VĐV trong danh sách để tổ chức trận đánh đôi!")
    else:
        st.info(f"🏆 Trận đấu này sẽ được tính vào: **{current_season}**")
        with st.form("match_form", clear_on_submit=False):
            match_date = st.date_input("🗓️ Ngày Thi Đấu", value=date.today(), format="DD/MM/YYYY")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<div class='team-card-1'><b>🔵 ĐỘI 1</b></div>", unsafe_allow_html=True)
                cp1_name, cp1_bet = st.columns([2.5, 1])
                with cp1_name:
                    p1 = st.selectbox("VĐV 1", members_list, index=0, key="p1")
                with cp1_bet:
                    k1_1 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k1_1")

                cp2_name, cp2_bet = st.columns([2.5, 1])
                with cp2_name:
                    p2 = st.selectbox("VĐV 2", members_list, index=min(1, len(members_list) - 1), key="p2")
                with cp2_bet:
                    k1_2 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k1_2")

                score1 = st.number_input("Điểm Số Đội 1", min_value=0, max_value=30, value=21)

            with col2:
                st.markdown("<div class='team-card-2'><b>🔴 ĐỘI 2</b></div>", unsafe_allow_html=True)
                cp3_name, cp3_bet = st.columns([2.5, 1])
                with cp3_name:
                    p3 = st.selectbox("VĐV 1", members_list, index=min(2, len(members_list) - 1), key="p3")
                with cp3_bet:
                    k2_1 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k2_1")

                cp4_name, cp4_bet = st.columns([2.5, 1])
                with cp4_name:
                    p4 = st.selectbox("VĐV 2", members_list, index=min(3, len(members_list) - 1), key="p4")
                with cp4_bet:
                    k2_2 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k2_2")

                score2 = st.number_input("Điểm Số Đội 2", min_value=0, max_value=30, value=19)

            video_input = st.text_input("🎥 Link Video YouTube Trận Đấu (Không bắt buộc):", placeholder="https://www.youtube.com/watch?v=...")

            st.write("")
            submitted = st.form_submit_button("💾 LƯU KẾT QUẢ TRẬN ĐẤU", use_container_width=True)

            if submitted:
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error("❌ Lỗi: Có VĐV bị chọn trùng tên! Vui lòng chọn 4 VĐV khác nhau.")
                elif score1 == score2:
                    st.error("❌ Lỗi: Điểm số hai đội không được bằng nhau (Không có tỉ số hòa).")
                else:
                    winner = "Đội 1" if int(score1) > int(score2) else "Đội 2"
                    new_match = {
                        "Ngày": format_date_vn(match_date),
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
                        "Mùa Giải": current_season
                    }
                    requests.post(SCRIPT_URL, json={"action": "add_match", "match": new_match})
                    
                    st.balloons()
                    st.success(
                        f"✅ **ĐÃ LƯU TRẬN ĐẤU THÀNH CÔNG!**\n\n"
                        f"🏆 **Đội thắng:** {winner} ({score1} - {score2})"
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
        
        # Lấy danh sách ngày có trận đấu để làm lựa chọn (sắp xếp giảm dần)
        unique_dates = sorted(df_p["date_obj"].unique(), reverse=True)
        date_options = ["Tất cả các ngày"] + [d.strftime("%d/%m/%Y") for d in unique_dates]

        c_filter, _ = st.columns([1.5, 2])
        with c_filter:
            selected_history_date = st.selectbox("📅 Lọc xem theo ngày:", date_options)

        # Lọc theo ngày được chọn
        if selected_history_date != "Tất cả các ngày":
            df_filtered = df_p[df_p["date"] == selected_history_date]
        else:
            df_filtered = df_p

        # Sắp xếp mặc định: Trận mới nhất/Ngày gần nhất lên trên cùng
        df_filtered = df_filtered.sort_values(by=["date_obj", "row_index"], ascending=[False, False])

        # Gom nhóm theo Ngày để hiển thị
        grouped_dates = df_filtered["date"].unique()

        for match_date in grouped_dates:
            group = df_filtered[df_filtered["date"] == match_date]
            st.markdown(f"#### 🗓️ Ngày: `{match_date}`")

            for _, m in group.iterrows():
                team1_str = f"{m['p1_1']} / {m['p1_2']}"
                team2_str = f"{m['p2_1']} / {m['p2_2']}"

                is_team1_winner = (m['winner'] == "Đội 1") or (m['score1'] > m['score2'])

                col_info, col_del = st.columns([6, 1])

                with col_info:
                    st.markdown(
                        render_scoreboard_html(
                            team1_str, m['score1'], team2_str, m['score2'], is_team1_winner
                        ),
                        unsafe_allow_html=True,
                    )
                    with st.expander("🔍 Chi tiết trận đấu & Video YouTube"):
                        st.write(
                            f"• **Mùa giải:** `{m['season']}`\n"
                            f"• **Đội 1:** {m['p1_1']} (`{m['k1_1']} điểm`) | {m['p1_2']} (`{m['k1_2']} điểm`)\n"
                            f"• **Đội 2:** {m['p2_1']} (`{m['k2_1']} điểm`) | {m['p2_2']} (`{m['k2_2']} điểm`)"
                        )

                        if m["video_url"]:
                            st.write("🎬 **Video trận đấu:**")
                            try:
                                st.video(m["video_url"])
                            except Exception:
                                st.warning("🔗 Link video không khả thi.")

                        with st.form(f"form_vid_{m['row_index']}"):
                            v_link = st.text_input("🔗 Chỉnh sửa / Điền link YouTube:", value=m["video_url"], key=f"v_in_{m['row_index']}")
                            save_v_btn = st.form_submit_button("💾 Lưu Video Trận Đấu")
                            if save_v_btn:
                                requests.post(
                                    SCRIPT_URL,
                                    json={
                                        "action": "update_video",
                                        "row_index": m["row_index"],
                                        "video_url": v_link.strip()
                                    }
                                )
                                st.toast("Đã lưu link Video thành công!", icon="✅")
                                st.cache_data.clear()
                                st.rerun()

                with col_del:
                    if st.button("🗑️ Xóa", key=f"del_match_{m['row_index']}"):
                        requests.post(
                            SCRIPT_URL,
                            json={"action": "delete_match", "row_index": m['row_index']},
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
        selected_member = st.selectbox("🔎 Chọn VĐV muốn tra cứu:", members_list)

        user_matches = []
        if not matches_df.empty:
            for idx, row in matches_df.iterrows():
                m = parse_match_row(row)
                if selected_member in [m["p1_1"], m["p1_2"], m["p2_1"], m["p2_2"]]:
                    user_matches.append(m)

        today_str = format_date_vn(date.today())
        now = datetime.now()

        win_today = lose_today = fine_today = 0
        win_month = lose_month = fine_month = 0

        for m in user_matches:
            is_team1 = selected_member in [m["p1_1"], m["p1_2"]]
            is_winner = (is_team1 and (m["winner"] == "Đội 1" or m["score1"] > m["score2"])) or (
                not is_team1 and (m["winner"] == "Đội 2" or m["score2"] > m["score1"])
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

            dt = m["date_obj"]
            if dt.month == now.month and dt.year == now.year:
                if is_winner:
                    win_month += 1
                else:
                    lose_month += 1
                    fine_month += bet_amount

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
            df_um = df_um.sort_values(by=["date_obj"], ascending=False)
            grouped_dates = df_um["date"].unique()

            for match_date in grouped_dates:
                group = df_um[df_um["date"] == match_date]
                st.markdown(f"##### 🗓️ Ngày: `{match_date}`")

                for _, m in group.iterrows():
                    team1_str = f"{m['p1_1']} / {m['p1_2']}"
                    team2_str = f"{m['p2_1']} / {m['p2_2']}"

                    is_team1_winner = (m['winner'] == "Đội 1") or (m['score1'] > m['score2'])

                    st.markdown(
                        render_scoreboard_html(
                            team1_str, m['score1'], team2_str, m['score2'], is_team1_winner
                        ),
                        unsafe_allow_html=True,
                    )
                    with st.expander("🔍 Chi tiết trận đấu & Video"):
                        st.write(
                            f"• **Mùa giải:** `{m['season']}`\n"
                            f"• **Đội 1:** {m['p1_1']} (`{m['k1_1']} điểm`) | {m['p1_2']} (`{m['k1_2']} điểm`)\n"
                            f"• **Đội 2:** {m['p2_1']} (`{m['k2_1']} điểm`) | {m['p2_2']} (`{m['k2_2']} điểm`)"
                        )
                        if m["video_url"]:
                            st.write("🎬 **Video trận đấu:**")
                            try:
                                st.video(m["video_url"])
                            except Exception:
                                st.warning("🔗 Link video không khả thi.")


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
            add_btn = st.form_submit_button("Thêm mới", use_container_width=True)

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
