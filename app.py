from datetime import date, datetime
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="CLB Cầu Lông - HVBADMINTON",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS Tối ưu căn chỉnh độ cao & phẳng lề triệt để
st.markdown(
    """
    <style>
    /* Khóa tràn ngang toàn ứng dụng */
    html, body, [data-testid="stAppViewContainer"], .main {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    .main .block-container {
        padding: 0.5rem 0.4rem !important;
        max-width: 100% !important;
    }

    /* Ép tất cả các hàng căn giữa tuyệt đối theo chiều dọc */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 6px !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    /* Tối ưu ô chọn & ô nhập số */
    div[data-baseweb="select"] > div {
        min-height: 40px !important;
        font-size: 0.8rem !important;
        padding: 0 2px !important;
    }
    
    .stNumberInput input {
        height: 40px !important;
        font-size: 0.9rem !important;
        padding: 2px 4px !important;
    }

    /* Bỏ khoảng trống thừa của ô NumberInput khi ẩn label */
    div[data-testid="stNumberInput"] {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    div[data-testid="stNumberInput"] > label {
        display: none !important;
    }

    .stPopover button {
        padding: 2px 2px !important;
        font-size: 0.72rem !important;
        height: 38px !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 8px 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .metric-title {
        font-size: 0.68rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 2px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #212529;
    }
    
    /* Scoreboard */
    .scoreboard-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 4px;
    }
    .scoreboard-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        border-bottom: 1px solid #f0f0f0;
    }
    .scoreboard-row:last-child {
        border-bottom: none;
    }
    .team-name {
        font-size: 0.85rem;
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
        width: 34px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        font-weight: 800;
        border-radius: 4px;
        margin-left: 6px;
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
        font-size: 0.65rem;
        font-weight: 700;
        padding: 1px 4px;
        border-radius: 3px;
        margin-right: 4px;
    }

    /* Thẻ tiêu đề Đội bằng chính xác độ cao 40px với ô điểm */
    .team-card-1 {
        background-color: #e7f5ff;
        border-left: 4px solid #1c7ed6;
        padding: 0 10px;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        border-radius: 6px;
        font-weight: bold;
        color: #1c7ed6;
        font-size: 0.9rem;
        box-sizing: border-box;
    }
    .team-card-2 {
        background-color: #fff5f5;
        border-left: 4px solid #f03e3e;
        padding: 0 10px;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        border-radius: 6px;
        font-weight: bold;
        color: #f03e3e;
        font-size: 0.9rem;
        box-sizing: border-box;
    }
    </style>
""",
    unsafe_allow_html=True,
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZGD4GKHo9cjMhWyD0-RDq-c7DuWLWnGwBuI77NDCOmGh15fSIG5tX3o9pbl6zaKEhiQ/exec"


def format_date_vn(dt_val):
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


def parse_seasons_dict(df_s):
    seasons_data = []
    if not df_s.empty:
        for _, r in df_s.iterrows():
            name = str(get_val(r, "Tên Mùa", 0, "")).strip()
            start_str = format_date_vn(get_val(r, "Ngày Bắt Đầu", 1, ""))
            end_str = format_date_vn(get_val(r, "Ngày Kết Thúc", 2, ""))
            status = str(get_val(r, "Trạng Thái", 3, "")).strip()

            if name:
                seasons_data.append({
                    "name": name,
                    "start_str": start_str,
                    "start_obj": parse_date_obj(start_str),
                    "end_str": end_str,
                    "end_obj": parse_date_obj(end_str) if end_str else datetime.max,
                    "status": status
                })
    if not seasons_data:
        seasons_data = [{
            "name": "Mùa 1 (2026)",
            "start_str": "01/01/2026",
            "start_obj": parse_date_obj("01/01/2026"),
            "end_str": "",
            "end_obj": datetime.max,
            "status": "Đang Khởi Tranh"
        }]
    return seasons_data


seasons_info = parse_seasons_dict(seasons_df)


def match_belong_to_season(match_dt_obj, season_item):
    return season_item["start_obj"] <= match_dt_obj <= season_item["end_obj"]


def parse_match_row(row):
    raw_date = get_val(row, "Ngày", 0, "")
    match_date = format_date_vn(raw_date)
    dt_obj = parse_date_obj(raw_date)

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

    if not season_name:
        for s in seasons_info:
            if match_belong_to_season(dt_obj, s):
                season_name = s["name"]
                break
        if not season_name:
            season_name = seasons_info[-1]["name"]

    if not winner:
        winner = "Đội 1" if score1 > score2 else "Đội 2"

    return {
        "date": match_date,
        "date_obj": dt_obj,
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
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 1.5rem; margin-right: 6px;">🏸</span>
        <div>
            <h3 style="margin: 0; padding: 0; font-size: 1.1rem;">HVBADMINTON</h3>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906206.png", width=60)
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

    seasons_list = [s["name"] for s in seasons_info]
    
    col_s, col_e, col_p = st.columns([2.2, 1.4, 1.4])

    with col_s:
        selected_season_name = st.selectbox(
            "Mùa Giải:", 
            seasons_list, 
            index=len(seasons_list) - 1 if seasons_list else 0, 
            label_visibility="collapsed"
        )

    curr_s_item = next((s for s in seasons_info if s["name"] == selected_season_name), seasons_info[-1])

    with col_e:
        with st.popover(f"🛑 Kết thúc {selected_season_name}", use_container_width=True):
            st.markdown(f"### 🛑 Kết Thúc\n**{selected_season_name}**")
            end_s_date = st.date_input("🗓️ Chọn Ngày Kết Thúc:", value=date.today(), format="DD/MM/YYYY")
            confirm_end = st.button("Đồng ý kết thúc mùa", use_container_width=True)

            if confirm_end:
                requests.post(
                    SCRIPT_URL,
                    json={
                        "action": "end_season",
                        "season_name": selected_season_name,
                        "end_date": format_date_vn(end_s_date)
                    }
                )
                st.toast(f"Đã kết thúc {selected_season_name}!", icon="✅")
                st.cache_data.clear()
                st.rerun()

    with col_p:
        with st.popover("⚙️ Tùy Chỉnh Mùa", use_container_width=True):
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
            st.markdown(f"### ✏️ Chỉnh Sửa Mùa")
            with st.form("edit_season_form"):
                edit_name = st.text_input("Tên Mùa:", value=curr_s_item["name"])
                edit_start = st.date_input("🗓️ Ngày Bắt Đầu:", value=curr_s_item["start_obj"].date() if curr_s_item["start_obj"] != datetime.min else date.today(), format="DD/MM/YYYY")

                is_ended = curr_s_item["status"] == "Đã Kết Thúc" or curr_s_item["end_str"] != ""
                if is_ended:
                    edit_end = st.date_input("🗓️ Ngày Kết Thúc:", value=curr_s_item["end_obj"].date() if curr_s_item["end_obj"] != datetime.max else date.today(), format="DD/MM/YYYY")
                else:
                    st.caption(" Mùa này đang diễn ra.")
                    edit_end = None

                save_edit = st.form_submit_button("Lưu Thay Đổi", use_container_width=True)
                if save_edit:
                    payload = {
                        "action": "edit_season",
                        "old_name": selected_season_name,
                        "new_name": edit_name.strip(),
                        "start_date": format_date_vn(edit_start),
                        "end_date": format_date_vn(edit_end) if edit_end else ""
                    }
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast("Đã chỉnh sửa mùa giải!", icon="✅")
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("---")
            st.markdown(f"### 🗑️ Xóa Mùa")
            if st.button("Xóa Mùa Này", use_container_width=True):
                requests.post(
                    SCRIPT_URL,
                    json={
                        "action": "delete_season",
                        "season_name": selected_season_name
                    }
                )
                st.toast(f"Đã xóa {selected_season_name}!", icon="🗑️")
                st.cache_data.clear()
                st.rerun()

    df_season_matches = pd.DataFrame()
    if not matches_df.empty:
        df_season_matches = matches_df[
            matches_df.apply(lambda r: match_belong_to_season(parse_match_row(r)["date_obj"], curr_s_item), axis=1)
        ]

    if df_season_matches.empty:
        st.info(f"💡 Chưa có trận đấu nào trong `{selected_season_name}`.")
    else:
        tab_day, tab_month, tab_all = st.tabs(
            ["📅 Ngày", "📆 Tháng", "🌟 Tất Cả"]
        )

        def calculate_leaderboard(df_filtered, show_points=False):
            stats = {
                m: {
                    "Điểm": 0,
                    "Thắng": 0,
                    "Thua": 0,
                    "Điểm thành viên": 0,
                    "Tổng Trận": 0,
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
                        stats[w]["Tổng Trận"] += 1

                for l_player, l_bet in losers:
                    if l_player in stats:
                        stats[l_player]["Thua"] += 1
                        stats[l_player]["Tổng Trận"] += 1
                        stats[l_player]["Điểm thành viên"] += l_bet

            for m in stats:
                total = stats[m]["Tổng Trận"]
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
                "Tổng Trận",
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
            selected_date = st.date_input("📅 Chọn ngày xem:", value=date.today(), format="DD/MM/YYYY")
            selected_date_str = format_date_vn(selected_date)

            df_day = df_season_matches[
                df_season_matches.apply(lambda r: parse_match_row(r)["date"] == selected_date_str, axis=1)
            ]

            if df_day.empty:
                st.info(f"💡 Không có trận nào ngày `{selected_date_str}`.")
            else:
                df_lb_day = calculate_leaderboard(df_day, show_points=False)
                total_fund_day = df_lb_day["Điểm thành viên"].sum()
                total_matches_day = len(df_day)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🎯 Điểm Thua</div>
                            <div class="metric-value" style="color: #2b8a3e;">{total_fund_day:,.0f}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🏸 Tổng Trận</div>
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
                        )
                    },
                )

        # Tab Tháng
        with tab_month:
            c1, c2 = st.columns(2)
            with c1:
                selected_year = st.number_input("Năm", min_value=2024, max_value=2030, value=datetime.now().year)
            with c2:
                selected_month = st.number_input("Tháng", min_value=1, max_value=12, value=datetime.now().month)

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
                        <div class="metric-title">🎯 Điểm Thua ({selected_month}/{selected_year})</div>
                        <div class="metric-value" style="color: #2b8a3e;">{total_fund_month:,.0f}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🏸 Tổng Số Trận</div>
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
                    )
                },
            )

        # Tab All
        with tab_all:
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
# 2. CẬP NHẬT TRẬN ĐẤU (ĐÃ FIX CHUẨN THẲNG HÀNG 100% & ĐỔI TÊN ĐIỂM)
# ==========================================
elif menu == "📝 Cập nhật trận đấu":
    st.subheader("📝 Ghi Nhận Trận Đấu Mới")

    current_season_name = seasons_info[-1]["name"] if seasons_info else "Mùa 1 (2026)"

    if len(members_list) < 4:
        st.warning("⚠️ Cần tối thiểu 4 VĐV để tổ chức trận đấu!")
    else:
        st.caption(f"🏆 Mùa hiện tại: **{current_season_name}**")
        with st.form("match_form", clear_on_submit=False):
            match_date = st.date_input("🗓️ Ngày Thi Đấu", value=date.today(), format="DD/MM/YYYY")

            # 🔵 ĐỘI 1: Căn chuẩn ngang hàng tuyệt đối
            col_t1_title, col_t1_score = st.columns([2.5, 1])
            with col_t1_title:
                st.markdown("<div class='team-card-1'>🔵 ĐỘI 1</div>", unsafe_allow_html=True)
            with col_t1_score:
                score1 = st.number_input("Điểm Đội 1", min_value=0, max_value=30, value=21, label_visibility="collapsed")

            cp1_name, cp1_bet = st.columns([2.5, 1])
            with cp1_name:
                p1 = st.selectbox("VĐV 1", members_list, index=0, key="p1")
            with cp1_bet:
                k1_1 = st.number_input("Điểm 1", min_value=0, max_value=10, value=1, step=1, key="k1_1")

            cp2_name, cp2_bet = st.columns([2.5, 1])
            with cp2_name:
                p2 = st.selectbox("VĐV 2", members_list, index=min(1, len(members_list) - 1), key="p2")
            with cp2_bet:
                k1_2 = st.number_input("Điểm 2", min_value=0, max_value=10, value=1, step=1, key="k1_2")

            st.write("")

            # 🔴 ĐỘI 2: Căn chuẩn ngang hàng tuyệt đối
            col_t2_title, col_t2_score = st.columns([2.5, 1])
            with col_t2_title:
                st.markdown("<div class='team-card-2'>🔴 ĐỘI 2</div>", unsafe_allow_html=True)
            with col_t2_score:
                score2 = st.number_input("Điểm Đội 2", min_value=0, max_value=30, value=19, label_visibility="collapsed")

            cp3_name, cp3_bet = st.columns([2.5, 1])
            with cp3_name:
                p3 = st.selectbox("VĐV 1", members_list, index=min(2, len(members_list) - 1), key="p3")
            with cp3_bet:
                k2_1 = st.number_input("Điểm 1", min_value=0, max_value=10, value=1, step=1, key="k2_1")

            cp4_name, cp4_bet = st.columns([2.5, 1])
            with cp4_name:
                p4 = st.selectbox("VĐV 2", members_list, index=min(3, len(members_list) - 1), key="p4")
            with cp4_bet:
                k2_2 = st.number_input("Điểm 2", min_value=0, max_value=10, value=1, step=1, key="k2_2")

            video_input = st.text_input("🎥 Link Video YouTube (Tùy chọn):", placeholder="https://...")

            st.write("")
            submitted = st.form_submit_button("💾 LƯU TRẬN ĐẤU", use_container_width=True)

            if submitted:
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error("❌ Trùng tên VĐV!")
                elif score1 == score2:
                    st.error("❌ Điểm hai đội không được bằng nhau!")
                else:
                    winner = "Đội 1" if int(score1) > int(score2) else "Đội 2"
                    m_date_vn = format_date_vn(match_date)
                    m_dt_obj = parse_date_obj(m_date_vn)

                    assigned_season = current_season_name
                    for s in seasons_info:
                        if match_belong_to_season(m_dt_obj, s):
                            assigned_season = s["name"]
                            break

                    new_match = {
                        "Ngày": m_date_vn,
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
                        "Mùa Giải": assigned_season
                    }
                    requests.post(SCRIPT_URL, json={"action": "add_match", "match": new_match})
                    
                    st.toast("✅ Đã lưu kết quả thành công!", icon="🎉")
                    time.sleep(1.5)
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 3. LỊCH SỬ CÁC TRẬN ĐẤU
# ==========================================
elif menu == "🛠️ Lịch sử các trận đấu":
    st.subheader("🛠️ Lịch Sử Các Trận Đấu")

    if matches_df.empty:
        st.info("Chưa có trận đấu nào.")
    else:
        matches_parsed = []
        for idx, row in matches_df.iterrows():
            m = parse_match_row(row)
            m["row_index"] = idx + 2
            matches_parsed.append(m)

        df_p = pd.DataFrame(matches_parsed)
        
        unique_dates = sorted(df_p["date_obj"].unique(), reverse=True)
        date_options = ["Tất cả các ngày"] + [d.strftime("%d/%m/%Y") for d in unique_dates]

        selected_history_date = st.selectbox("📅 Lọc xem theo ngày:", date_options)

        if selected_history_date != "Tất cả các ngày":
            df_filtered = df_p[df_p["date"] == selected_history_date]
        else:
            df_filtered = df_p

        df_filtered = df_filtered.sort_values(by=["date_obj", "row_index"], ascending=[False, False])
        grouped_dates = df_filtered["date"].unique()

        for match_date in grouped_dates:
            group = df_filtered[df_filtered["date"] == match_date]
            st.markdown(f"#### 🗓️ `{match_date}`")

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

                with st.expander("🔍 Chi tiết & Video"):
                    st.write(
                        f"• **Mùa:** `{m['season']}`\n"
                        f"• **Đội 1:** {m['p1_1']} (`điểm {m['k1_1']}`) | {m['p1_2']} (`điểm {m['k1_2']}`)\n"
                        f"• **Đội 2:** {m['p2_1']} (`điểm {m['k2_1']}`) | {m['p2_2']} (`điểm {m['k2_2']}`)"
                    )

                    if m["video_url"]:
                        try:
                            st.video(m["video_url"])
                        except Exception:
                            st.warning("🔗 Link video lỗi.")

                    with st.form(f"form_vid_{m['row_index']}"):
                        v_link = st.text_input("🔗 Link YouTube:", value=m["video_url"], key=f"v_in_{m['row_index']}")
                        save_v_btn = st.form_submit_button("💾 Lưu Video", use_container_width=True)
                        if save_v_btn:
                            requests.post(
                                SCRIPT_URL,
                                json={
                                    "action": "update_video",
                                    "row_index": m["row_index"],
                                    "video_url": v_link.strip()
                                }
                            )
                            st.toast("Đã lưu video!", icon="✅")
                            st.cache_data.clear()
                            st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Xóa trận đấu này", key=f"del_match_{m['row_index']}", use_container_width=True):
                        requests.post(
                            SCRIPT_URL,
                            json={"action": "delete_match", "row_index": m['row_index']},
                        )
                        st.toast("Đã xóa trận!", icon="✅")
                        st.cache_data.clear()
                        st.rerun()


# ==========================================
# 4. TÌM KIẾM THÀNH VIÊN
# ==========================================
elif menu == "🔍 Tìm kiếm thành viên":
    st.subheader("🔍 Hồ Sơ VĐV")

    if not members_list:
        st.warning("Chưa có VĐV nào!")
    else:
        selected_member = st.selectbox("🔎 Chọn VĐV:", members_list)

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
                    <div class="metric-title">📊 Hôm Nay</div>
                    <div style="font-size: 0.9rem; margin-top: 3px;">
                        Thắng: <b>{win_today}</b> | Thua: <b>{lose_today}</b><br>
                        Điểm thua: <b style="color:#f03e3e;">{fine_today}</b>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with c_month:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">📈 Tháng {now.month}/{now.year}</div>
                    <div style="font-size: 0.9rem; margin-top: 3px;">
                        Thắng: <b>{win_month}</b> | Thua: <b>{lose_month}</b><br>
                        Điểm thua: <b style="color:#f03e3e;">{fine_month}</b>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.write("### 📜 Lịch Sử Đã Tham Gia")

        if not user_matches:
            st.info("Chưa có trận đấu nào.")
        else:
            df_um = pd.DataFrame(user_matches)
            df_um = df_um.sort_values(by=["date_obj"], ascending=False)
            grouped_dates = df_um["date"].unique()

            for match_date in grouped_dates:
                group = df_um[df_um["date"] == match_date]
                st.markdown(f"##### 🗓️ `{match_date}`")

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
                    with st.expander("🔍 Chi tiết trận đấu"):
                        st.write(
                            f"• **Mùa:** `{m['season']}`\n"
                            f"• **Đội 1:** {m['p1_1']} (`{m['k1_1']}`) | {m['p1_2']} (`{m['k1_2']}`)\n"
                            f"• **Đội 2:** {m['p2_1']} (`{m['k2_1']}`) | {m['p2_2']} (`{m['k2_2']}`)"
                        )
                        if m["video_url"]:
                            try:
                                st.video(m["video_url"])
                            except Exception:
                                st.warning("🔗 Link video lỗi.")


# ==========================================
# 5. QUẢN LÝ THÀNH VIÊN
# ==========================================
elif menu == "⚙️ Quản lý thành viên":
    st.subheader("⚙️ Quản Lý VĐV")

    st.markdown("### ➕ Thêm VĐV Mới")
    with st.form("add_member_form", clear_on_submit=True):
        new_name = st.text_input("Họ và Tên VĐV:")
        add_btn = st.form_submit_button("Thêm VĐV Mới", use_container_width=True)

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

    st.markdown("---")

    st.markdown("### 📋 Danh Sách VĐV")
    if not members_list:
        st.info("Chưa có VĐV nào.")
    else:
        for idx, member in enumerate(members_list):
            c_name, c_btn = st.columns([3, 1])
            with c_name:
                st.write(f"**{idx + 1}. {member}**")
            with c_btn:
                if st.button("🗑️", key=f"del_mem_{idx}", use_container_width=True):
                    payload = {"action": "delete_member", "name": member}
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast(f"Đã xóa **{member}**!", icon="🗑️")
                    st.cache_data.clear()
                    st.rerun()
