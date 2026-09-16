from datetime import date, datetime
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Quản Lý CLB Cầu Lông", layout="wide")

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

st.title("🏸 Quản Lý Điểm & Quỹ CLB Cầu Lông")

menu = st.sidebar.radio(
    "Điều hướng",
    [
        "Leaderboard & Quỹ",
        "Cập nhật trận đấu",
        "Lịch sử & Quản lý trận",
        "Tìm kiếm thành viên",
        "Quản lý thành viên",
    ],
)


# ==========================================
# 1. LEADERBOARD & QUỸ
# ==========================================
if menu == "Leaderboard & Quỹ":
    st.header("🏆 Bảng Xếp Hạng & Quỹ Thua Trận")

    if matches_df.empty:
        st.info("Chưa có dữ liệu trận đấu nào được ghi nhận.")
    else:
        tab_today, tab_month, tab_all = st.tabs(
            ["Xếp hạng Hôm Nay", "Xếp hạng Theo Tháng", "Tổng Sắp Tất Cả"]
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
            df_lb.index += 1
            return df_lb

        with tab_today:
            today_str = date.today().strftime("%Y-%m-%d")
            df_today = matches_df[matches_df["Ngày"] == today_str]
            st.subheader(f"Bảng xếp hạng ngày {today_str}")
            st.dataframe(
                calculate_leaderboard(df_today, show_points=False),
                use_container_width=True,
            )

        with tab_month:
            col1, col2 = st.columns(2)
            with col1:
                selected_year = st.number_input(
                    "Năm",
                    min_value=2024,
                    max_value=2030,
                    value=datetime.now().year,
                )
            with col2:
                selected_month = st.number_input(
                    "Tháng",
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

            st.markdown("---")
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    "💰 Tổng Quỹ Tháng", f"{total_fund_month:.0f}k VNĐ"
                )
            with metric_col2:
                st.metric("🏸 Tổng Số Trận Trong Tháng", total_matches_month)

            st.subheader(
                f"Bảng xếp hạng Tháng {selected_month}/{selected_year}"
            )
            st.dataframe(df_lb_month, use_container_width=True)

        with tab_all:
            st.subheader("Bảng xếp hạng Toàn thời gian")
            st.dataframe(
                calculate_leaderboard(matches_df, show_points=True),
                use_container_width=True,
            )


# ==========================================
# 2. CẬP NHẬT TRẬN ĐẤU
# ==========================================
elif menu == "Cập nhật trận đấu":
    st.header("📝 Ghi Nhận Kết Quả Trận Đấu (Đánh Đôi)")

    if len(members_list) < 4:
        st.warning("Cần tối thiểu 4 thành viên để tổ chức trận đánh đôi!")
    else:
        with st.form("match_form"):
            match_date = st.date_input("Ngày thi đấu", value=date.today())
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔵 Đội 1")
                p1 = st.selectbox("VĐV A", members_list, index=0)
                p2 = st.selectbox(
                    "VĐV B",
                    members_list,
                    index=min(1, len(members_list) - 1),
                )
                score1 = st.number_input(
                    "Điểm Đội 1", min_value=0, max_value=30, value=21
                )

            with col2:
                st.subheader("🔴 Đội 2")
                p3 = st.selectbox(
                    "VĐV C",
                    members_list,
                    index=min(2, len(members_list) - 1),
                )
                p4 = st.selectbox(
                    "VĐV D",
                    members_list,
                    index=min(3, len(members_list) - 1),
                )
                score2 = st.number_input(
                    "Điểm Đội 2", min_value=0, max_value=30, value=19
                )

            submitted = st.form_submit_button("Lưu kết quả trận đấu")

            if submitted:
                players = [p1, p2, p3, p4]
                if len(set(players)) < 4:
                    st.error("Lỗi: Các VĐV không được trùng nhau!")
                elif score1 == score2:
                    st.error("Lỗi: Kết quả không được hòa!")
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
                    st.success("Đã lưu trận đấu thành công! 🎉")
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 3. LỊCH SỬ & QUẢN LÝ TRẬN
# ==========================================
elif menu == "Lịch sử & Quản lý trận":
    st.header("🛠️ Quản Lý Tất Cả Trận Đấu")

    if matches_df.empty:
        st.info("Chưa có trận đấu nào trong hệ thống.")
    else:
        st.write("Danh sách các trận đấu đã ghi nhận (bạn có thể xóa trận bị nhập sai):")
        for idx, row in matches_df.iterrows():
            col_info, col_del = st.columns([5, 1])

            team1_str = f"{row['Đội 1 - VĐV 1']}/{row['Đội 1 - VĐV 2']}"
            team2_str = f"{row['Đội 2 - VĐV 1']}/{row['Đội 2 - VĐV 2']}"
            score1 = row["Điểm Đội 1"]
            score2 = row["Điểm Đội 2"]

            # In đậm đội thắng theo định dạng A/B Score1 - Score2 C/D
            if row["Đội Thắng"] == "Đội 1":
                match_display = f"**{team1_str} {score1}** - {score2} {team2_str}"
            else:
                match_display = f"{team1_str} {score1} - **{score2} {team2_str}**"

            with col_info:
                st.info(f"🗓️ **{row['Ngày']}** &nbsp;|&nbsp; {match_display}")

            with col_del:
                sheet_row = idx + 2  # Bỏ qua dòng tiêu đề Google Sheet
                if st.button("🗑️ Xóa", key=f"del_match_{idx}"):
                    requests.post(
                        SCRIPT_URL,
                        json={"action": "delete_match", "row_index": sheet_row},
                    )
                    st.success("Đã xóa trận đấu thành công!")
                    st.cache_data.clear()
                    st.rerun()


# ==========================================
# 4. TÌM KIẾM THÀNH VIÊN
# ==========================================
elif menu == "Tìm kiếm thành viên":
    st.header("🔍 Lịch Sử Thi Đấu Của Thành Viên")

    if not members_list:
        st.warning("Chưa có thành viên nào trong danh sách!")
    else:
        selected_member = st.selectbox(
            "Chọn thành viên cần xem:", members_list
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

        win_today = lose_today = 0
        win_month = lose_month = 0

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

        st.subheader(f"📊 Báo cáo thành tích: **{selected_member}**")
        col_t, col_m = st.columns(2)

        with col_t:
            st.info(
                f"**Hôm nay ({today_str}):**\n- Thắng: **{win_today}** trận |"
                f" Thua: **{lose_today}** trận\n- Ủng hộ quỹ:"
                f" **{fine_today}k VNĐ**"
            )

        with col_m:
            st.success(
                f"**Tháng này ({now.month}/{now.year}):**\n- Thắng:"
                f" **{win_month}** trận | Thua: **{lose_month}** trận\n- Ủng"
                f" hộ quỹ: **{fine_month}k VNĐ**"
            )

        st.markdown("---")
        st.subheader("📜 Danh sách các trận đấu đã tham gia")

        if user_matches.empty:
            st.write("Chưa tham gia trận đấu nào.")
        else:
            grouped = user_matches.groupby("Ngày", sort=False)

            for match_date, group in grouped:
                st.markdown(f"#### 🗓️ Ngày: {match_date}")

                for _, row in group.iterrows():
                    team1_str = (
                        f"{row['Đội 1 - VĐV 1']} / {row['Đội 1 - VĐV 2']}"
                    )
                    team2_str = (
                        f"{row['Đội 2 - VĐV 1']} / {row['Đội 2 - VĐV 2']}"
                    )
                    score_str = (
                        f"{row['Điểm Đội 1']} - {row['Điểm Đội 2']}"
                    )

                    if row["Đội Thắng"] == "Đội 1":
                        match_text = f"**{team1_str}** &nbsp; ` {score_str} ` &nbsp; {team2_str}"
                    else:
                        match_text = f"{team1_str} &nbsp; ` {score_str} ` &nbsp; **{team2_str}**"

                    st.info(f"🏸 {match_text}")


# ==========================================
# 5. QUẢN LÝ THÀNH VIÊN
# ==========================================
elif menu == "Quản lý thành viên":
    st.header("⚙️ Quản Lý Danh Sách Thành Viên")

    with st.form("add_member_form", clear_on_submit=True):
        new_name = st.text_input("Nhập họ và tên thành viên mới:")
        add_btn = st.form_submit_button("➕ Thêm thành viên")

        if add_btn:
            name_clean = new_name.strip()
            if name_clean == "":
                st.warning("Vui lòng nhập tên thành viên!")
            elif name_clean in members_list:
                st.error("Thành viên này đã có trong danh sách!")
            else:
                payload = {"action": "add_member", "name": name_clean}
                requests.post(SCRIPT_URL, json=payload)
                st.success(f"Đã thêm thành viên **{name_clean}** thành công!")
                st.cache_data.clear()
                st.rerun()

    st.subheader("📋 Danh sách thành viên hiện tại")

    if not members_list:
        st.info("Danh sách thành viên đang trống.")
    else:
        for idx, member in enumerate(members_list):
            col_name, col_del = st.columns([4, 1])
            col_name.write(f"**{idx + 1}. {member}**")

            if col_del.button("🗑️ Xóa", key=f"del_{idx}"):
                payload = {"action": "delete_member", "name": member}
                requests.post(SCRIPT_URL, json=payload)
                st.success(f"Đã xóa thành viên **{member}**!")
                st.cache_data.clear()
                st.rerun()
