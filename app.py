from datetime import date, datetime
import time
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="CLB Cầu Lông - HV BADMINTON",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS Tối ưu căn lề & Dùng Flexbox ép điểm số sát tên VĐV
st.markdown(
    """
    <style>
    /* Khóa tràn ngang toàn ứng dụng */
    html, body, [data-testid="stAppViewContainer"], .main {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    .main .block-container {
        padding: 0.5rem 0.2rem !important;
        max-width: 100% !important;
    }

    div[data-baseweb="select"] > div {
        min-height: 38px !important;
        font-size: 0.85rem !important;
        padding: 0 2px !important;
    }
    
    .stNumberInput input {
        height: 38px !important;
        font-size: 0.85rem !important;
        padding: 2px 4px !important;
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
    
    /* Layout sát lề ép tỉ số dính sát tên VĐV */
    .match-row-wrapper {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
        width: 100%;
    }

    .match-item-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 6px 8px;
        display: inline-flex;
        flex-direction: column;
        gap: 4px;
        max-width: fit-content;
    }

    .team-row-compact {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .team-name-compact {
        font-size: 0.85rem;
        font-weight: 600;
        color: #495057;
        white-space: nowrap;
        line-height: 1.2;
    }

    .winner-team .team-name-compact {
        color: #000000;
        font-weight: 800;
    }

    .score-box-compact {
        min-width: 26px;
        height: 22px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
        border-radius: 4px;
        padding: 0 4px;
        flex-shrink: 0;
    }

    .score-win {
        background-color: #212529;
        color: #ffffff;
    }

    .score-lose {
        background-color: #e9ecef;
        color: #495057;
    }

    .badge-win-tag {
        background-color: #2b8a3e;
        color: white;
        font-size: 0.6rem;
        font-weight: 700;
        padding: 1px 3px;
        border-radius: 3px;
        flex-shrink: 0;
    }

    .team-card-1 {
        background-color: #e7f5ff;
        border-left: 4px solid #1c7ed6;
        padding: 6px 10px;
        border-radius: 6px;
        font-weight: bold;
        color: #1c7ed6;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }
    .team-card-2 {
        background-color: #fff5f5;
        border-left: 4px solid #f03e3e;
        padding: 6px 10px;
        border-radius: 6px;
        font-weight: bold;
        color: #f03e3e;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }

    /* Animation Quả Cầu Lông Bay */
    @keyframes flyUp {
        0% {
            bottom: -50px;
            opacity: 1;
            transform: scale(0.8) rotate(0deg);
        }
        50% {
            transform: scale(1.2) rotate(15deg);
        }
        100% {
            bottom: 105vh;
            opacity: 0;
            transform: scale(1) rotate(-15deg);
        }
    }

    .shuttlecock-fly {
        position: fixed;
        z-index: 999999;
        font-size: 2.8rem;
        pointer-events: none;
        animation: flyUp 2.2s ease-out forwards;
    }
    </style>
""",
    unsafe_allow_html=True,
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZGD4GKHo9cjMhWyD0-RDq-c7DuWLWnGwBuI77NDCOmGh15fSIG5tX3o9pbl6zaKEhiQ/exec"


def trigger_shuttlecock_effect():
    st.markdown(
        """
        <div class="shuttlecock-fly" style="left: 15%; animation-delay: 0s;">🏸</div>
        <div class="shuttlecock-fly" style="left: 35%; animation-delay: 0.2s;">🏸</div>
        <div class="shuttlecock-fly" style="left: 55%; animation-delay: 0.1s;">🏸</div>
        <div class="shuttlecock-fly" style="left: 75%; animation-delay: 0.3s;">🏸</div>
        <div class="shuttlecock-fly" style="left: 88%; animation-delay: 0.05s;">🏸</div>
    """,
        unsafe_allow_html=True,
    )


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

    season_name = ""
    for s in seasons_info:
        if match_belong_to_season(dt_obj, s):
            season_name = s["name"]
            break
    if not season_name:
        season_name = seasons_info[0]["name"] if seasons_info else "Mùa 1 (2026)"

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


def render_match_html(m):
    team1_str = f"{m['p1_1']} / {m['p1_2']}"
    team2_str = f"{m['p2_1']} / {m['p2_2']}"
    is_team1_winner = (m['winner'] == "Đội 1") or (m['score1'] > m['score2'])

    t1_class = "winner-team" if is_team1_winner else ""
    t2_class = "" if is_team1_winner else "winner-team"

    s1_class = "score-win" if is_team1_winner else "score-lose"
    s2_class = "score-lose" if is_team1_winner else "score-win"

    b1 = '<span class="badge-win-tag">WIN</span>' if is_team1_winner else ""
    b2 = "" if is_team1_winner else '<span class="badge-win-tag">WIN</span>'

    return f"""<div class="match-item-container"><div class="team-row-compact {t1_class}">{b1}<div class="team-name-compact">{team1_str}</div><div class="score-box-compact {s1_class}">{m['score1']}</div></div><div class="team-row-compact {t2_class}">{b2}<div class="team-name-compact">{team2_str}</div><div class="score-box-compact {s2_class}">{m['score2']}</div></div></div>"""


# Header thương hiệu HV BADMINTON
st.markdown(
    """
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 1.5rem; margin-right: 6px;">🏸</span>
        <div>
            <h3 style="margin: 0; padding: 0; font-size: 1.1rem;">HV BADMINTON</h3>
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
                trigger_shuttlecock_effect()
                st.toast(f"Đã kết thúc {selected_season_name}!", icon="🏸")
                time.sleep(1.5)
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
                        trigger_shuttlecock_effect()
                        st.toast(f"Đã tạo {s_name_final} thành công!", icon="🏸")
                        time.sleep(1.5)
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
                    trigger_shuttlecock_effect()
                    st.toast("Đã chỉnh sửa mùa giải!", icon="🏸")
                    time.sleep(1.5)
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
        tab_day, tab_all, tab_month = st.tabs(
            ["📅 BXH Ngày", "🌟 BXH Cả Mùa", "📆 BXH Tháng"]
        )

        def calculate_leaderboard(df_filtered):
            stats = {
                m: {
                    "Thắng": 0,
                    "Thua": 0,
                    "Điểm": 0,
                    "Tổng Trận": 0,
                    "% Thắng": 0.0,
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
                        stats[w]["Thắng"] += 1
                        stats[w]["Tổng Trận"] += 1

                for l_player, l_bet in losers:
                    if l_player in stats:
                        stats[l_player]["Thua"] += 1
                        stats[l_player]["Tổng Trận"] += 1
                        stats[l_player]["Điểm"] += l_bet

            for m in stats:
                total = stats[m]["Tổng Trận"]
                if total > 0:
                    stats[m]["% Thắng"] = round((stats[m]["Thắng"] / total) * 100, 1)

            df_lb = pd.DataFrame.from_dict(stats, orient="index").reset_index()
            df_lb.rename(columns={"index": "Tên VĐV"}, inplace=True)
            df_lb.sort_values(by=["Thắng", "% Thắng"], ascending=[False, False], inplace=True)

            column_order = [
                "Tên VĐV",
                "Thắng",
                "Thua",
                "Điểm",
                "Tổng Trận",
                "% Thắng",
            ]

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

        column_configs = {
            "Tên VĐV": st.column_config.TextColumn("Tên VĐV", width=110),
            "Thắng": st.column_config.NumberColumn("Thắng", width=50),
            "Thua": st.column_config.NumberColumn("Thua", width=50),
            "Điểm": st.column_config.NumberColumn("Điểm", width=55),
            "Tổng Trận": st.column_config.NumberColumn("Tổng Trận", width=75),
            "% Thắng": st.column_config.ProgressColumn(
                "% Thắng", format="%.0f%%", min_value=0, max_value=100, width=90
            ),
        }

        # 1. Tab BXH Ngày
        with tab_day:
            selected_date = st.date_input("📅 Chọn ngày xem:", value=date.today(), format="DD/MM/YYYY")
            selected_date_str = format_date_vn(selected_date)

            df_day = df_season_matches[
                df_season_matches.apply(lambda r: parse_match_row(r)["date"] == selected_date_str, axis=1)
            ]

            if df_day.empty:
                st.info(f"💡 Không có trận nào ngày `{selected_date_str}`.")
            else:
                df_lb_day = calculate_leaderboard(df_day)
                total_fund_day = df_lb_day["Điểm"].sum()
                total_matches_day = len(df_day)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🎯 Điểm ({selected_date_str})</div>
                            <div class="metric-value" style="color: #2b8a3e;">{total_fund_day:,.0f}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🏸 Tổng Số Trận</div>
                            <div class="metric-value" style="color: #1c7ed6;">{total_matches_day} Trận</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.write("")
                calc_height = max(150, (len(df_lb_day) + 1) * 35 + 10)
                st.dataframe(
                    df_lb_day,
                    use_container_width=True,
                    height=calc_height,
                    column_config=column_configs,
                )

        # 2. Tab BXH Cả Mùa
        with tab_all:
            df_lb_all = calculate_leaderboard(df_season_matches)
            total_fund_all = df_lb_all["Điểm"].sum()
            total_matches_all = len(df_season_matches)

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🎯 ĐIỂM ({selected_season_name})</div>
                        <div class="metric-value" style="color: #2b8a3e;">{total_fund_all:,.0f}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">🏸 TỔNG SỐ TRẬN</div>
                        <div class="metric-value" style="color: #1c7ed6;">{total_matches_all} Trận</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.write("")
            calc_height_all = max(150, (len(df_lb_all) + 1) * 35 + 10)
            st.dataframe(
                df_lb_all,
                use_container_width=True,
                height=calc_height_all,
                column_config=column_configs,
            )

        # 3. Tab BXH Tháng
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

            if df_month.empty:
                st.info(f"💡 Không có trận nào trong tháng `{selected_month}/{selected_year}`.")
            else:
                df_lb_month = calculate_leaderboard(df_month)
                total_fund_month = df_lb_month["Điểm"].sum()
                total_matches_month = len(df_month)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">🎯 Điểm ({selected_month}/{selected_year})</div>
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
                calc_height_month = max(150, (len(df_lb_month) + 1) * 35 + 10)
                st.dataframe(
                    df_lb_month,
                    use_container_width=True,
                    height=calc_height_month,
                    column_config=column_configs,
                )


# ==========================================
# 2. CẬP NHẬT TRẬN ĐẤU
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

            # 🔵 ĐỘI 1
            st.markdown("<div class='team-card-1'>🔵 ĐỘI 1</div>", unsafe_allow_html=True)

            cp1_name, cp1_bet, cp1_team = st.columns([2.2, 1, 1.3])
            with cp1_name:
                p1 = st.selectbox("VĐV 1", members_list, index=None, placeholder="Chọn VĐV...", key="p1")
            with cp1_bet:
                k1_1 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k1_1")
            with cp1_team:
                score1 = st.number_input("Điểm Số Đội 1", min_value=0, max_value=30, value=21, key="s1")

            cp2_name, cp2_bet, _ = st.columns([2.2, 1, 1.3])
            with cp2_name:
                p2 = st.selectbox("VĐV 2", members_list, index=None, placeholder="Chọn VĐV...", key="p2")
            with cp2_bet:
                k1_2 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k1_2")

            st.write("")

            # 🔴 ĐỘI 2
            st.markdown("<div class='team-card-2'>🔴 ĐỘI 2</div>", unsafe_allow_html=True)

            cp3_name, cp3_bet, cp3_team = st.columns([2.2, 1, 1.3])
            with cp3_name:
                p3 = st.selectbox("VĐV 1", members_list, index=None, placeholder="Chọn VĐV...", key="p3")
            with cp3_bet:
                k2_1 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k2_1")
            with cp3_team:
                score2 = st.number_input("Điểm Số Đội 2", min_value=0, max_value=30, value=19, key="s2")

            cp4_name, cp4_bet, _ = st.columns([2.2, 1, 1.3])
            with cp4_name:
                p4 = st.selectbox("VĐV 2", members_list, index=None, placeholder="Chọn VĐV...", key="p4")
            with cp4_bet:
                k2_2 = st.number_input("Điểm", min_value=0, max_value=10, value=1, step=1, key="k2_2")

            video_input = st.text_input("🎥 Link Video YouTube (Tùy chọn):", placeholder="https://...")

            st.write("")
            submitted = st.form_submit_button("💾 LƯU TRẬN ĐẤU", use_container_width=True)

            if submitted:
                if not p1 or not p2 or not p3 or not p4:
                    st.error("❌ Vui lòng chọn đầy đủ 4 VĐV!")
                else:
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
                        
                        trigger_shuttlecock_effect()
                        st.toast("Đã lưu kết quả thành công!", icon="🏸")
                        time.sleep(1.8)
                        st.cache_data.clear()
                        st.rerun()


# ==========================================
# 3. LỊCH SỬ CÁC TRẬN ĐẤU (FİX TRIỆT ĐỂ BẢNG ĐIỂM + NÚT ⚙️ DÍNH SÁT)
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
                # Ép bảng điểm và Nút ⚙️ vào cùng 1 dòng dính sát lề trái
                st.markdown('<div class="match-row-wrapper">', unsafe_allow_html=True)
                st.markdown(render_match_html(m), unsafe_allow_html=True)

                # Nút Popover Cài Đặt
                with st.popover("⚙️"):
                    st.markdown(f"### ⚙️ Chỉnh Sửa Trận Đấu")
                    st.caption(f"🗓️ Ngày: `{m['date']}` | Mùa: `{m['season']}`")

                    with st.form(f"edit_match_form_{m['row_index']}"):
                        st.markdown("**🔵 Đội 1:**")
                        e_p1_1 = st.selectbox("VĐV 1:", members_list, index=members_list.index(m['p1_1']) if m['p1_1'] in members_list else 0, key=f"ep11_{m['row_index']}")
                        e_p1_2 = st.selectbox("VĐV 2:", members_list, index=members_list.index(m['p1_2']) if m['p1_2'] in members_list else 0, key=f"ep12_{m['row_index']}")
                        e_s1 = st.number_input("Tỉ số Đội 1:", min_value=0, max_value=30, value=m['score1'], key=f"es1_{m['row_index']}")

                        st.markdown("**🔴 Đội 2:**")
                        e_p2_1 = st.selectbox("VĐV 1:", members_list, index=members_list.index(m['p2_1']) if m['p2_1'] in members_list else 0, key=f"ep21_{m['row_index']}")
                        e_p2_2 = st.selectbox("VĐV 2:", members_list, index=members_list.index(m['p2_2']) if m['p2_2'] in members_list else 0, key=f"ep22_{m['row_index']}")
                        e_s2 = st.number_input("Tỉ số Đội 2:", min_value=0, max_value=30, value=m['score2'], key=f"es2_{m['row_index']}")

                        save_m_edit = st.form_submit_button("💾 Lưu Thay Đổi", use_container_width=True)

                        if save_m_edit:
                            e_players = [e_p1_1, e_p1_2, e_p2_1, e_p2_2]
                            if len(set(e_players)) < 4:
                                st.error("❌ Trùng tên VĐV!")
                            elif e_s1 == e_s2:
                                st.error("❌ Tỉ số hai đội không được bằng nhau!")
                            else:
                                e_winner = "Đội 1" if int(e_s1) > int(e_s2) else "Đội 2"
                                updated_match_data = {
                                    "Ngày": m["date"],
                                    "Đội 1 - VĐV 1": e_p1_1,
                                    "Kèo 1_1": m["k1_1"],
                                    "Đội 1 - VĐV 2": e_p1_2,
                                    "Kèo 1_2": m["k1_2"],
                                    "Điểm Đội 1": int(e_s1),
                                    "Đội 2 - VĐV 1": e_p2_1,
                                    "Kèo 2_1": m["k2_1"],
                                    "Đội 2 - VĐV 2": e_p2_2,
                                    "Kèo 2_2": m["k2_2"],
                                    "Điểm Đội 2": int(e_s2),
                                    "Đội Thắng": e_winner,
                                    "Video": m["video_url"],
                                    "Mùa Giải": m["season"]
                                }
                                requests.post(
                                    SCRIPT_URL,
                                    json={
                                        "action": "edit_match",
                                        "row_index": m["row_index"],
                                        "match": updated_match_data
                                    }
                                )
                                trigger_shuttlecock_effect()
                                st.toast("Đã cập nhật trận đấu!", icon="🏸")
                                time.sleep(1.5)
                                st.cache_data.clear()
                                st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Xóa trận đấu này", key=f"del_m_{m['row_index']}", use_container_width=True):
                        requests.post(
                            SCRIPT_URL,
                            json={"action": "delete_match", "row_index": m['row_index']},
                        )
                        st.toast("Đã xóa trận!", icon="🗑️")
                        st.cache_data.clear()
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

                # Link Video YouTube giữ nguyên tại vị trí Chi Tiết & Video như cũ
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
                            trigger_shuttlecock_effect()
                            st.toast("Đã lưu video thành công!", icon="🏸")
                            time.sleep(1.5)
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
                        Điểm: <b style="color:#f03e3e;">{fine_today}</b>
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
                        Điểm: <b style="color:#f03e3e;">{fine_month}</b>
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
                    st.markdown(render_match_html(m), unsafe_allow_html=True)
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
                trigger_shuttlecock_effect()
                st.toast(f"Đã thêm VĐV **{name_clean}** thành công!", icon="🏸")
                time.sleep(1.5)
                st.cache_data.clear()
                st.rerun()

    st.markdown("---")

    st.markdown("### 📋 Danh Sách VĐV")
    if not members_list:
        st.info("Chưa có VĐV nào.")
    else:
        for idx, member in enumerate(members_list):
            c_name, c_edit, c_del = st.columns([3, 1, 1])
            with c_name:
                st.write(f"**{idx + 1}. {member}**")
            
            with c_edit:
                with st.popover("✏️", use_container_width=True):
                    st.markdown(f"### ✏️ Sửa tên VĐV")
                    with st.form(f"edit_mem_form_{idx}"):
                        updated_name = st.text_input("Tên mới:", value=member, key=f"inp_edit_mem_{idx}")
                        submit_edit = st.form_submit_button("Lưu Tên Mới", use_container_width=True)
                        if submit_edit:
                            u_name_clean = updated_name.strip()
                            if not u_name_clean:
                                st.warning("Không được để trống tên!")
                            elif u_name_clean in members_list and u_name_clean != member:
                                st.error("Tên này đã tồn tại!")
                            else:
                                payload = {
                                    "action": "edit_member",
                                    "old_name": member,
                                    "new_name": u_name_clean
                                }
                                requests.post(SCRIPT_URL, json=payload)
                                trigger_shuttlecock_effect()
                                st.toast(f"Đã cập nhật tên thành **{u_name_clean}**!", icon="🏸")
                                time.sleep(1.5)
                                st.cache_data.clear()
                                st.rerun()

            with c_del:
                if st.button("🗑️", key=f"del_mem_{idx}", use_container_width=True):
                    payload = {"action": "delete_member", "name": member}
                    requests.post(SCRIPT_URL, json=payload)
                    st.toast(f"Đã xóa **{member}**!", icon="🗑️")
                    st.cache_data.clear()
                    st.rerun()
