import streamlit as st
import pandas as pd

st.set_page_config(page_title="CLB Cầu Lông", page_icon="🏸")
st.title("🏸 Quản Lý Điểm Cầu Lông CLB")

# --- KẾT NỐI GOOGLE SHEETS ---
# Thay đường link Google Sheets của bạn vào giữa 2 dấu ngoặc kép ở dòng dưới:
SHEET_URL = "THAY_LINK_GOOGLE_SHEET_CUA_BAN_VAO_DAY"

# Chuyển link Google Sheets sang dạng CSV đọc trực tiếp
def get_csv_url(url):
    if "/edit" in url:
        return url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
    return url

@st.cache_data(ttl=5) # Cập nhật dữ liệu mới mỗi 5 giây
def load_data():
    try:
        csv_url = get_csv_url(SHEET_URL)
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error("Chưa thể đọc dữ liệu. Vui lòng kiểm tra lại Link Google Sheets (Đã bật Chia sẻ cho mọi người xem chưa?)")
        return pd.DataFrame()

df = load_data()

# --- HIỂN THỊ BẢNG XẾP HẠNG ---
st.subheader("🏆 Bảng Xếp Hạng CLB")

if not df.empty:
    # Nếu có cột Điểm thì sắp xếp theo điểm giảm dần
    if "Điểm" in df.columns:
        df_sorted = df.sort_values(by="Điểm", ascending=False)
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có dữ liệu VĐV. Hãy điền danh sách vào file Google Sheets!")

if st.button("🔄 Cập nhật dữ liệu mới"):
    st.cache_data.clear()
    st.rerun()
