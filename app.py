from datetime import date, datetime
from io import StringIO
import html
import threading
import time

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.set_page_config(
    page_title="HV BADMINTON",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CẤU HÌNH DỮ LIỆU
# Giữ nguyên 2 URL thật của web cũ tại đây khi thay file.
# =========================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KV81efOTe8CbiS7ZKO1H6jWBeDRJIFySmdiA9Ig3xfQ/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZGD4GKHo9cjMhWyD0-RDq-c7DuWLWnGwBuI77NDCOmGh15fSIG5tX3o9pbl6zaKEhiQ/exec"

DATA_CACHE_TTL = 15
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 15

# =========================================================
# GIAO DIỆN - PHONG CÁCH WEB APP, TỐI ƯU DESKTOP + MOBILE
# =========================================================
st.markdown(
    r"""
<style>
:root{
  --navy:#1f4375;
  --navy-dark:#17355f;
  --green:#076b55;
  --green-dark:#05543f;
  --green-soft:#e9f4f0;
  --ink:#111827;
  --muted:#7b8798;
  --line:#dce3ea;
  --soft:#f5f7f9;
  --gold:#e8aa22;
  --silver:#aeb9c7;
  --bronze:#c87535;
}

html,body,[data-testid="stAppViewContainer"],.main{
  max-width:100vw!important;
  overflow-x:hidden!important;
  background:#fff!important;
}

/* Ẩn chrome Streamlit để nhìn giống website riêng hơn */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important;}
[data-testid="stHeader"]{height:0!important;background:transparent!important;}
[data-testid="stSidebar"]{display:none!important;}

.main .block-container{
  max-width:1120px!important;
  padding:1rem 1.15rem 4.5rem!important;
  margin:0 auto!important;
}

/* Header web */
.hvb-nav-wrap{
  position:sticky;
  top:0;
  z-index:99990;
  width:100%;
  background:var(--navy);
  box-shadow:0 1px 0 rgba(255,255,255,.08);
  margin:-1rem calc(50% - 50vw) 1.6rem;
  padding-left:calc(50vw - 50%);
  padding-right:calc(50vw - 50%);
}
.hvb-nav{
  max-width:1120px;
  min-height:58px;
  margin:0 auto;
  padding:0 1.15rem;
  display:flex;
  align-items:center;
  gap:22px;
}
.hvb-brand{display:flex;align-items:center;gap:11px;text-decoration:none!important;color:#fff!important;font-weight:800;white-space:nowrap;}
.hvb-logo{width:34px;height:34px;border-radius:7px;background:#fff;color:var(--navy);display:flex;align-items:center;justify-content:center;font-size:.73rem;font-weight:900;letter-spacing:.02em;}
.hvb-brand-name{font-size:.98rem;}
.hvb-links{display:flex;align-items:center;justify-content:center;gap:28px;flex:1;}
.hvb-link{color:#eef4fb!important;text-decoration:none!important;font-size:.88rem;padding:18px 0 14px;border-bottom:3px solid transparent;white-space:nowrap;}
.hvb-link:hover{color:#fff!important;}
.hvb-link.active{font-weight:750;border-bottom-color:#fff;color:#fff!important;}
.hvb-admin{background:#fff;color:var(--navy)!important;text-decoration:none!important;padding:8px 18px;border-radius:7px;font-size:.86rem;font-weight:700;white-space:nowrap;}

/* Mobile bottom nav */
.hvb-mobile-nav{display:none;}

.page-kicker{font-size:.82rem;color:var(--green);font-weight:800;margin-bottom:.25rem;}
.page-title{font-size:2.2rem;line-height:1.1;margin:0 0 .35rem;color:#080d14;font-weight:550;letter-spacing:-.025em;}
.page-subtitle{font-size:.9rem;color:var(--muted);margin:0 0 1.6rem;}
.section-rule{width:34px;height:3px;background:var(--green);border-radius:5px;margin:1.8rem 0 .65rem;}
.section-heading{font-size:1.65rem;font-weight:550;letter-spacing:-.02em;color:#0e1420;margin:0 0 1rem;}

/* Hero */
.hero{
  border-radius:15px;
  background:var(--green-dark);
  color:#fff;
  overflow:hidden;
  min-height:345px;
  display:grid;
  grid-template-columns:1.08fr .92fr;
  margin-bottom:2rem;
}
.hero-copy{padding:46px 48px 40px;display:flex;flex-direction:column;justify-content:center;}
.hero-kicker{font-size:.86rem;font-weight:750;opacity:.9;margin-bottom:10px;}
.hero h1{font-size:2.25rem;line-height:1.12;margin:0 0 14px;font-weight:600;letter-spacing:-.025em;}
.hero-desc{max-width:570px;font-size:.93rem;line-height:1.65;opacity:.92;margin-bottom:28px;}
.hero-stats{display:flex;gap:58px;align-items:flex-end;flex-wrap:wrap;}
.hero-stat-label{font-size:.78rem;font-weight:750;opacity:.85;margin-bottom:3px;}
.hero-stat-value{font-size:3rem;line-height:1;font-weight:500;letter-spacing:-.035em;}
.hero-stat-note{font-size:.76rem;margin-top:7px;opacity:.92;}
.hero-art{position:relative;background-image:linear-gradient(rgba(255,255,255,.10) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.10) 1px,transparent 1px);background-size:82px 82px;opacity:.85;}
.hero-art:before{content:"";position:absolute;inset:17% 0 17% 0;border-top:2px solid rgba(255,255,255,.14);border-bottom:2px solid rgba(255,255,255,.14);}
.hero-art:after{content:"";position:absolute;top:0;bottom:0;left:50%;border-left:2px solid rgba(255,255,255,.18);}

.summary-card{border:1px solid var(--line);border-radius:13px;padding:24px 25px;display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:1.8rem;background:#fff;}
.summary-label{font-size:.78rem;color:#b27600;font-weight:700;margin-bottom:4px;}
.summary-main{font-size:1.45rem;font-weight:600;color:#0d1117;}
.summary-meta{font-size:.82rem;color:var(--muted);margin-top:5px;}
.summary-link{color:#111827!important;text-decoration:none!important;font-size:.82rem;white-space:nowrap;}

/* Quick cards */
.quick-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:1.3rem;}
.quick-card{border:1px solid var(--line);border-radius:11px;padding:18px 20px;text-decoration:none!important;background:#fff;color:var(--ink)!important;transition:.16s ease;}
.quick-card:hover{transform:translateY(-1px);box-shadow:0 7px 22px rgba(17,24,39,.07);border-color:#c7d1db;}
.quick-title{font-weight:800;font-size:.98rem;margin-bottom:4px;}
.quick-sub{color:var(--muted);font-size:.8rem;}

/* Match cards */
.match-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-bottom:1.2rem;}
.match-card{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden;min-width:0;}
.match-card-head{height:31px;background:#f5f7f8;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 11px;gap:6px;}
.match-chip{background:#e8ebee;border-radius:6px;padding:3px 8px;font-size:.65rem;font-weight:750;color:#444;white-space:nowrap;}
.match-bet{background:#e6f2ee;border-radius:6px;padding:3px 8px;font-size:.64rem;font-weight:750;color:#064f3d;white-space:nowrap;max-width:55%;overflow:hidden;text-overflow:ellipsis;}
.team-line{display:grid;grid-template-columns:1fr 42px;align-items:center;gap:8px;padding:11px 12px;min-height:58px;}
.team-line + .team-line{border-top:1px solid #edf0f2;}
.team-names{min-width:0;color:#8b97a6;font-size:.79rem;line-height:1.45;}
.team-names strong{color:#080d14;font-weight:800;}
.team-win-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#08765a;margin-right:8px;vertical-align:middle;}
.team-score{text-align:right;font-size:1.25rem;font-weight:800;color:#adb7c3;}
.team-line.winner .team-score{color:#006e53;}
.k-val{color:#0b725a;font-size:.68rem;margin-left:4px;white-space:nowrap;}
.video-pill{display:inline-block;margin-left:5px;font-size:.65rem;color:#365a8b;text-decoration:none!important;}

/* Top 3 */
.rank-tabs{display:grid;grid-template-columns:repeat(4,1fr);background:#f0f2f4;border-radius:9px;padding:4px;margin:1rem 0 1.1rem;gap:2px;}
.rank-tab{padding:8px 6px;text-align:center;border-radius:7px;font-size:.78rem;color:#273240;}
.rank-tab.active{background:#fff;font-weight:800;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.podium{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:1.4rem;}
.podium-card{border:1px solid var(--line);border-radius:13px;padding:24px 23px 21px;background:#fff;min-height:215px;position:relative;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.podium-card.first{background:#171d27;color:#fff;border-color:#171d27;}
.place-badge{position:absolute;top:18px;left:18px;width:28px;height:28px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.76rem;font-weight:900;background:var(--silver);color:#15202b;}
.first .place-badge{background:var(--gold);}
.podium-card:nth-child(3) .place-badge{background:var(--bronze);color:#fff;}
.avatar{width:58px;height:58px;border-radius:17px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.25rem;font-weight:900;margin-bottom:10px;background:#8b3ba5;}
.avatar.red{background:#bd382c}.avatar.gold{background:#ae6b00}.avatar.blue{background:#2c58b8}.avatar.purple{background:#8a3ea0}
.podium-name{font-weight:800;font-size:.95rem;margin-bottom:6px;}
.podium-meta{font-size:.77rem;color:#8793a3;margin-bottom:12px;}.first .podium-meta{color:#d7dee8;}
.podium-value{font-size:1.7rem;font-weight:650;line-height:1;}.podium-value small{font-size:.68rem;font-weight:500;margin-left:4px;opacity:.8;}

/* Ranking table custom */
.table-wrap{overflow-x:auto;border-top:1px solid transparent;}
.hvb-table{width:100%;border-collapse:collapse;min-width:720px;font-size:.82rem;}
.hvb-table th{text-align:left;padding:11px 13px;border-bottom:1px solid var(--line);font-weight:800;color:#111;white-space:nowrap;}
.hvb-table td{padding:12px 13px;border-bottom:1px solid var(--line);vertical-align:middle;}
.hvb-table tr:hover td{background:#fbfcfd;}
.rank-num{display:inline-flex;width:26px;height:26px;border-radius:6px;background:#aeb9c7;align-items:center;justify-content:center;font-weight:800;color:#203040;}
.rank-num.r1{background:var(--gold);}.rank-num.r3{background:var(--bronze);color:#fff;}
.member-cell{display:flex;align-items:center;gap:10px;font-weight:700;white-space:nowrap;}
.mini-avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:850;font-size:.75rem;background:#2c58b8;flex:0 0 auto;}
.highlight-col{background:#edf5f2!important;font-weight:800;text-align:right;}
.winbar{height:3px;background:#dbe7e3;width:95px;position:relative;margin-top:5px;}.winbar span{display:block;height:100%;background:#08765a;}
.form-dots{display:flex;gap:5px}.form-dot{width:20px;height:20px;border-radius:4px;background:#dfe4e9}.form-dot.win{background:#08765a}

/* Member cards */
.member-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;margin-top:1.35rem;}
.member-card{border:1px solid var(--line);border-radius:13px;min-height:170px;padding:24px 16px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;background:#fff;}
.member-card .avatar{margin-bottom:12px;}
.member-name{font-weight:800;font-size:.9rem;margin-bottom:9px;}
.member-stat{font-size:.75rem;color:var(--muted);display:flex;gap:7px;align-items:center;}
.member-tag{padding:3px 9px;border-radius:6px;background:#e6edf8;color:#21467a;font-weight:800;}

/* Admin box */
.admin-shell{border:1px solid var(--line);border-radius:14px;padding:1.25rem;background:#fff;}
[data-testid="stForm"]{border:1px solid var(--line)!important;border-radius:12px!important;padding:1rem!important;background:#fff!important;}

/* Widgets */
div[data-baseweb="select"]>div,.stDateInput>div>div,.stTextInput input,.stNumberInput div[data-baseweb="input"]{min-height:40px!important;border-radius:9px!important;background:#f7f8fa!important;border-color:#dce3ea!important;font-size:.86rem!important;}
.stButton button,.stFormSubmitButton button,.stPopover button{border-radius:9px!important;min-height:39px!important;font-size:.82rem!important;white-space:nowrap!important;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:var(--navy)!important;border-color:var(--navy)!important;}
.stTabs [data-baseweb="tab-list"]{gap:7px!important;overflow-x:auto!important;flex-wrap:nowrap!important;scrollbar-width:none;}.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar{display:none}.stTabs [data-baseweb="tab"]{white-space:nowrap!important;font-size:.82rem!important;padding:.45rem .75rem!important;}

/* Flash status */
.center-status-overlay{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.5);backdrop-filter:blur(2px);}
.center-status-overlay.wait-delayed{opacity:0;visibility:hidden;pointer-events:none;animation:showWaitDelayed 0s linear .8s forwards}@keyframes showWaitDelayed{to{opacity:1;visibility:visible;pointer-events:auto}}
.center-status-box{min-width:175px;max-width:calc(100vw - 48px);padding:18px 24px;background:#fff;border:1px solid #e4e8ec;border-radius:15px;box-shadow:0 16px 40px rgba(17,24,39,.16);display:flex;flex-direction:column;align-items:center;gap:7px;text-align:center}.center-status-icon{font-size:1.8rem}.center-status-text{font-size:.95rem;font-weight:800;color:#1d2733}.center-status-subtext{font-size:.75rem;color:#7b8794}.center-status-success{color:#08765a}.center-status-overlay.success-auto-hide{pointer-events:none;animation:successOverlayAutoHide 1.65s ease-out forwards}@keyframes successOverlayAutoHide{0%,72%{opacity:1;visibility:visible}100%{opacity:0;visibility:hidden}}

@media(max-width:768px){
  .main .block-container{padding:.65rem .72rem 5.4rem!important;}
  .hvb-nav-wrap{margin:-.65rem calc(50% - 50vw) 1.1rem;padding-left:calc(50vw - 50%);padding-right:calc(50vw - 50%);}
  .hvb-nav{min-height:54px;padding:0 .75rem;}
  .hvb-brand-name{font-size:.88rem}.hvb-logo{width:31px;height:31px;}
  .hvb-links,.hvb-admin{display:none!important;}
  .hvb-mobile-nav{position:fixed;z-index:99991;bottom:0;left:0;right:0;height:62px;background:#fff;border-top:1px solid #dce3ea;display:grid;grid-template-columns:repeat(5,1fr);padding:5px 5px max(5px,env(safe-area-inset-bottom));box-shadow:0 -8px 24px rgba(17,24,39,.06);}
  .hvb-mobile-nav a{text-decoration:none!important;color:#6f7b89!important;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;font-size:.59rem;font-weight:700;border-radius:8px;}
  .hvb-mobile-nav a span{font-size:1.05rem;line-height:1.05}.hvb-mobile-nav a.active{color:var(--navy)!important;background:#eef3f9;}
  .page-title{font-size:1.75rem}.page-subtitle{font-size:.8rem;margin-bottom:1rem}.section-heading{font-size:1.35rem}
  .hero{min-height:280px;grid-template-columns:1fr;margin-bottom:1rem}.hero-copy{padding:28px 24px}.hero-art{display:none}.hero h1{font-size:1.75rem}.hero-desc{font-size:.82rem;margin-bottom:22px}.hero-stats{gap:27px}.hero-stat-value{font-size:2.35rem}.hero-stat-label{font-size:.68rem}.hero-stat-note{font-size:.66rem}
  .summary-card{padding:17px 16px;margin-bottom:1.1rem}.summary-main{font-size:1.16rem}.summary-meta,.summary-link{font-size:.7rem}
  .quick-grid{grid-template-columns:1fr;gap:8px}.quick-card{padding:14px 15px}
  .match-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.match-card-head{padding:0 7px}.match-chip,.match-bet{font-size:.55rem;padding:3px 6px}.team-line{grid-template-columns:1fr 30px;padding:8px 8px;min-height:53px}.team-names{font-size:.66rem}.team-score{font-size:1rem}.k-val{font-size:.58rem;margin-left:2px}
  .podium{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}.podium-card{padding:18px 7px 14px;min-height:170px}.place-badge{top:8px;left:8px;width:23px;height:23px;font-size:.65rem}.avatar{width:44px;height:44px;border-radius:13px;font-size:1rem}.podium-name{font-size:.74rem}.podium-meta{font-size:.58rem}.podium-value{font-size:1.3rem}.rank-tabs{overflow-x:auto;grid-template-columns:repeat(4,minmax(105px,1fr));}.rank-tab{font-size:.66rem}
  .member-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.member-card{min-height:145px;padding:16px 7px}.member-name{font-size:.78rem}.member-stat{font-size:.62rem}
  div[data-testid="stHorizontalBlock"]{flex-direction:row!important;flex-wrap:nowrap!important;gap:.45rem!important}div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"]{min-width:0!important}
  div[data-baseweb="select"]>div,.stDateInput>div>div,.stTextInput input,.stNumberInput div[data-baseweb="input"]{min-height:37px!important;font-size:.76rem!important}.stButton button,.stFormSubmitButton button,.stPopover button{min-height:36px!important;font-size:.72rem!important;padding:0 .55rem!important}
}
@media(max-width:355px){.match-grid{grid-template-columns:1fr}.podium{grid-template-columns:1fr}.member-grid{grid-template-columns:1fr}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HTTP / CACHE / GHI DỮ LIỆU
# =========================================================
@st.cache_resource
def get_http_session():
    session = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.25,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=40)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


@st.cache_resource
def get_write_lock():
    return threading.Lock()


def show_wait_overlay(message="Đợi chút..."):
    holder = st.empty()
    holder.markdown(
        f'<div class="center-status-overlay wait-delayed"><div class="center-status-box"><div class="center-status-icon">🏸</div><div class="center-status-text">{html.escape(message)}</div></div></div>',
        unsafe_allow_html=True,
    )
    return holder


def queue_success_and_rerun(message="Thành công!", effect=False):
    st.session_state["_center_flash_success"] = message
    st.session_state["_center_flash_effect"] = bool(effect)
    st.rerun()


def render_queued_success():
    message = st.session_state.pop("_center_flash_success", None)
    st.session_state.pop("_center_flash_effect", None)
    if not message:
        return
    st.markdown(
        '<div class="center-status-overlay success-auto-hide"><div class="center-status-box"><div class="center-status-icon">✅</div>'
        f'<div class="center-status-text center-status-success">{html.escape(message)}</div><div class="center-status-subtext">Đã cập nhật dữ liệu</div></div></div>',
        unsafe_allow_html=True,
    )


def format_date_vn(dt_val):
    if dt_val is None or dt_val == "":
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
    if isinstance(dt_val, datetime):
        return dt_val
    if isinstance(dt_val, date):
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


def fetch_sheet_uncached(sheet_name):
    url = get_sheet_csv_url(SHEET_URL, sheet_name)
    response = get_http_session().get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))


@st.cache_data(ttl=DATA_CACHE_TTL, max_entries=1, show_spinner=False)
def load_data():
    try:
        df_m = fetch_sheet_uncached("Members")
        members = df_m["Tên Thành Viên"].dropna().astype(str).str.strip()
        members = members[members.ne("")].tolist()
    except Exception:
        members = []
    try:
        df_matches = fetch_sheet_uncached("Matches")
    except Exception:
        df_matches = pd.DataFrame()
    try:
        df_seasons = fetch_sheet_uncached("Seasons")
    except Exception:
        df_seasons = pd.DataFrame(columns=["Tên Mùa", "Ngày Bắt Đầu", "Ngày Kết Thúc", "Trạng Thái"])
    return members, df_matches, df_seasons


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


members_list, matches_df, seasons_df = load_data()


def parse_seasons_dict(df_s):
    seasons_data = []
    if not df_s.empty:
        for _, r in df_s.iterrows():
            name = str(get_val(r, "Tên Mùa", 0, "")).strip()
            start_str = format_date_vn(get_val(r, "Ngày Bắt Đầu", 1, ""))
            end_str = format_date_vn(get_val(r, "Ngày Kết Thúc", 2, ""))
            status = str(get_val(r, "Trạng Thái", 3, "")).strip()
            if name:
                seasons_data.append(
                    {
                        "name": name,
                        "start_str": start_str,
                        "start_obj": parse_date_obj(start_str),
                        "end_str": end_str,
                        "end_obj": parse_date_obj(end_str) if end_str else datetime.max,
                        "status": status,
                    }
                )
    if not seasons_data:
        seasons_data = [
            {
                "name": "Mùa 1 (2026)",
                "start_str": "01/01/2026",
                "start_obj": parse_date_obj("01/01/2026"),
                "end_str": "",
                "end_obj": datetime.max,
                "status": "Đang Khởi Tranh",
            }
        ]
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
        "season": season_name,
    }


def build_parsed_matches_df(df):
    if df.empty:
        return pd.DataFrame()
    records = []
    for idx, row in df.iterrows():
        m = parse_match_row(row)
        m["row_index"] = idx + 2
        records.append(m)
    return pd.DataFrame(records)


matches_parsed_df = build_parsed_matches_df(matches_df)


def _match_identity(m):
    return (
        str(m.get("date", "")).strip(),
        str(m.get("p1_1", "")).strip(),
        str(m.get("p1_2", "")).strip(),
        str(m.get("p2_1", "")).strip(),
        str(m.get("p2_2", "")).strip(),
    )


def resolve_match_row_index(match_context):
    try:
        fresh_df = fetch_sheet_uncached("Matches")
    except Exception:
        return None
    if fresh_df.empty:
        return None
    target_identity = _match_identity(match_context)
    original_row = to_int(match_context.get("row_index", 0), 0)
    original_pos = original_row - 2
    if 0 <= original_pos < len(fresh_df):
        candidate = parse_match_row(fresh_df.iloc[original_pos])
        if _match_identity(candidate) == target_identity:
            return original_row
    candidates = []
    for idx, row in fresh_df.iterrows():
        candidate = parse_match_row(row)
        if _match_identity(candidate) == target_identity:
            candidates.append((idx + 2, candidate))
    if len(candidates) == 1:
        return candidates[0][0]
    if len(candidates) > 1:
        exact = [
            row_index
            for row_index, candidate in candidates
            if candidate["score1"] == to_int(match_context.get("score1"), 0)
            and candidate["score2"] == to_int(match_context.get("score2"), 0)
        ]
        if len(exact) == 1:
            return exact[0]
    return None


def post_script(payload, match_context=None):
    wait_holder = show_wait_overlay("Đợi chút...")
    try:
        with get_write_lock():
            payload_to_send = dict(payload)
            if match_context is not None and "row_index" in payload_to_send:
                resolved_row = resolve_match_row_index(match_context)
                if resolved_row is None:
                    wait_holder.empty()
                    st.warning("⚠️ Danh sách trận vừa thay đổi. Hãy tải lại trang rồi thử lại để tránh sửa/xóa nhầm trận.")
                    load_data.clear()
                    return False
                payload_to_send["row_index"] = resolved_row
            response = get_http_session().post(
                SCRIPT_URL,
                json=payload_to_send,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            response.raise_for_status()
        wait_holder.empty()
        return True
    except requests.RequestException as exc:
        wait_holder.empty()
        st.error(f"❌ Không thể ghi dữ liệu lúc này. Vui lòng thử lại. ({type(exc).__name__})")
        return False


def finish_write(message):
    load_data.clear()
    queue_success_and_rerun(message)


# =========================================================
# HÀM THỐNG KÊ / RENDER
# =========================================================
def calculate_leaderboard(df_filtered):
    stats = {
        member: {"Thắng": 0, "Thua": 0, "Điểm": 0, "Tổng Trận": 0, "% Thắng": 0.0}
        for member in members_list
    }
    if df_filtered is None or df_filtered.empty:
        return pd.DataFrame(columns=["Tên VĐV", "Thắng", "Thua", "Điểm", "Tổng Trận", "% Thắng"])
    for _, m in df_filtered.iterrows():
        is_team1_win = (m["winner"] == "Đội 1") or (m["score1"] > m["score2"])
        if is_team1_win:
            winners = [m["p1_1"], m["p1_2"]]
            losers = [(m["p2_1"], m["k2_1"]), (m["p2_2"], m["k2_2"])]
        else:
            winners = [m["p2_1"], m["p2_2"]]
            losers = [(m["p1_1"], m["k1_1"]), (m["p1_2"], m["k1_2"])]
        for w in winners:
            if w in stats:
                stats[w]["Thắng"] += 1
                stats[w]["Tổng Trận"] += 1
        for l_player, l_bet in losers:
            if l_player in stats:
                stats[l_player]["Thua"] += 1
                stats[l_player]["Tổng Trận"] += 1
                stats[l_player]["Điểm"] += l_bet
    rows = []
    for name, s in stats.items():
        if s["Tổng Trận"] > 0:
            s["% Thắng"] = round(s["Thắng"] / s["Tổng Trận"] * 100, 1)
        rows.append({"Tên VĐV": name, **s})
    return pd.DataFrame(rows)


def initials(name):
    parts = [p for p in str(name).replace("/", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def avatar_class(index):
    return ["gold", "red", "purple", "blue"][index % 4]


def current_season_item():
    active = [s for s in seasons_info if "kết thúc" not in s["status"].lower() and not s["end_str"]]
    return active[-1] if active else seasons_info[-1]


def season_matches(season):
    if matches_parsed_df.empty:
        return pd.DataFrame()
    mask = matches_parsed_df["date_obj"].apply(lambda d: match_belong_to_season(d, season))
    return matches_parsed_df[mask].copy()


def leaderboard_for_season(season):
    df = season_matches(season)
    lb = calculate_leaderboard(df)
    if lb.empty:
        return lb
    return lb.sort_values(["Thắng", "% Thắng", "Tổng Trận"], ascending=[False, False, False]).reset_index(drop=True)


def match_bet_text(m):
    vals = [m["k1_1"], m["k1_2"], m["k2_1"], m["k2_2"]]
    return "Kèo " + "/".join(str(v) for v in vals)


def render_match_cards(df, limit=None):
    if df is None or df.empty:
        st.info("Chưa có trận đấu nào.")
        return
    work = df.sort_values(["date_obj", "row_index"], ascending=[False, False])
    if limit:
        work = work.head(limit)
    cards = []
    for pos, (_, m) in enumerate(work.iterrows(), start=1):
        t1win = (m["winner"] == "Đội 1") or (m["score1"] > m["score2"])
        n1 = f"{html.escape(str(m['p1_1']))} <span class='k-val'>+{m['k1_1']}</span><br>{html.escape(str(m['p1_2']))} <span class='k-val'>+{m['k1_2']}</span>"
        n2 = f"{html.escape(str(m['p2_1']))} <span class='k-val'>+{m['k2_1']}</span><br>{html.escape(str(m['p2_2']))} <span class='k-val'>+{m['k2_2']}</span>"
        if t1win:
            n1 = "<span class='team-win-dot'></span><strong>" + n1 + "</strong>"
        else:
            n2 = "<span class='team-win-dot'></span><strong>" + n2 + "</strong>"
        video = ""
        if str(m.get("video_url", "")).strip():
            video = f"<a class='video-pill' href='{html.escape(str(m['video_url']), quote=True)}' target='_blank'>🎥 Video</a>"
        cards.append(
            f"""
            <div class="match-card">
              <div class="match-card-head"><span class="match-chip">{html.escape(str(m['date']))}</span><span class="match-bet">{html.escape(match_bet_text(m))}</span></div>
              <div class="team-line {'winner' if t1win else ''}"><div class="team-names">{n1}{video if t1win else ''}</div><div class="team-score">{m['score1']}</div></div>
              <div class="team-line {'winner' if not t1win else ''}"><div class="team-names">{n2}{video if not t1win else ''}</div><div class="team-score">{m['score2']}</div></div>
            </div>
            """
        )
    st.markdown('<div class="match-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_podium(lb, value_col="Thắng", suffix="thắng"):
    if lb.empty:
        return
    top = lb.head(3).copy()
    cards = []
    for i, (_, r) in enumerate(top.iterrows()):
        card_cls = "podium-card first" if i == 0 else "podium-card"
        raw_value = float(r[value_col])
        value_text = str(int(raw_value)) if raw_value.is_integer() else f"{raw_value:.1f}"
        cards.append(
            f"""
            <div class="{card_cls}">
              <div class="place-badge">{i+1}</div>
              <div class="avatar {avatar_class(i)}">{html.escape(initials(r['Tên VĐV']))}</div>
              <div class="podium-name">{html.escape(str(r['Tên VĐV']))}</div>
              <div class="podium-meta">{int(r['Tổng Trận'])} trận · thắng {r['% Thắng']:.0f}%</div>
              <div class="podium-value">{value_text}<small>{html.escape(suffix)}</small></div>
            </div>
            """
        )
    st.markdown('<div class="podium">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_ranking_table(lb):
    if lb.empty:
        st.info("Chưa có dữ liệu xếp hạng.")
        return
    rows = []
    for i, (_, r) in enumerate(lb.iterrows(), start=1):
        rank_cls = "r1" if i == 1 else ("r3" if i == 3 else "")
        pct = max(0, min(100, float(r["% Thắng"])))
        # 5 ô phong độ minh họa theo tỉ lệ thắng, không giả lập kết quả từng trận.
        wins = round(pct / 20)
        form = "".join("<span class='form-dot win'></span>" if j < wins else "<span class='form-dot'></span>" for j in range(5))
        rows.append(
            f"""
            <tr>
              <td><span class="rank-num {rank_cls}">{i}</span></td>
              <td><div class="member-cell"><span class="mini-avatar">{html.escape(initials(r['Tên VĐV']))}</span>{html.escape(str(r['Tên VĐV']))}</div></td>
              <td class="highlight-col">{int(r['Thắng'])}</td>
              <td>{int(r['Tổng Trận'])}</td>
              <td>{pct:.0f}%<div class="winbar"><span style="width:{pct:.0f}%"></span></div></td>
              <td>{int(r['Điểm'])}</td>
              <td><div class="form-dots">{form}</div></td>
            </tr>
            """
        )
    table = f"""
    <div class="table-wrap"><table class="hvb-table">
      <thead><tr><th>Hạng</th><th>Thành viên</th><th>Thắng</th><th>Trận</th><th>Tỉ lệ</th><th>Điểm</th><th>Phong độ</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    """
    st.markdown(table, unsafe_allow_html=True)


def render_member_cards(lb_all):
    stats_map = {}
    if not lb_all.empty:
        stats_map = {r["Tên VĐV"]: r for _, r in lb_all.iterrows()}
    cards = []
    for i, member in enumerate(members_list):
        s = stats_map.get(member)
        total = int(s["Tổng Trận"]) if s is not None else 0
        win_pct = float(s["% Thắng"]) if s is not None else 0
        cards.append(
            f"""
            <div class="member-card">
              <div class="avatar {avatar_class(i+1)}">{html.escape(initials(member))}</div>
              <div class="member-name">{html.escape(member)}</div>
              <div class="member-stat"><span class="member-tag">{total} trận</span><span>{win_pct:.0f}% thắng</span></div>
            </div>
            """
        )
    st.markdown('<div class="member-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


# =========================================================
# NAVIGATION BẰNG QUERY PARAM - GIỮ ĐÚNG 1 APP STREAMLIT
# =========================================================
page = st.query_params.get("page", "home")
if isinstance(page, list):
    page = page[0]
allowed = {"home", "ranking", "matches", "members", "admin"}
if page not in allowed:
    page = "home"

nav_items = [
    ("home", "Trang chủ"),
    ("ranking", "Bảng xếp hạng"),
    ("matches", "Trận đấu"),
    ("members", "Thành viên"),
]
nav_links = "".join(
    f'<a class="hvb-link {"active" if page == key else ""}" href="?page={key}">{label}</a>'
    for key, label in nav_items
)
mobile_items = [
    ("home", "🏠", "Trang chủ"),
    ("ranking", "🏆", "BXH"),
    ("matches", "🏸", "Trận"),
    ("members", "👥", "VĐV"),
    ("admin", "⚙️", "Quản trị"),
]
mobile_links = "".join(
    f'<a class="{"active" if page == key else ""}" href="?page={key}"><span>{icon}</span>{label}</a>'
    for key, icon, label in mobile_items
)

st.markdown(
    f"""
    <div class="hvb-nav-wrap"><div class="hvb-nav">
      <a class="hvb-brand" href="?page=home"><span class="hvb-logo">HVB</span><span class="hvb-brand-name">HV BADMINTON</span></a>
      <div class="hvb-links">{nav_links}</div>
      <a class="hvb-admin" href="?page=admin">Quản trị</a>
    </div></div>
    <div class="hvb-mobile-nav">{mobile_links}</div>
    """,
    unsafe_allow_html=True,
)

render_queued_success()

# =========================================================
# TRANG CHỦ
# =========================================================
if page == "home":
    curr = current_season_item()
    curr_matches = season_matches(curr)
    lb = leaderboard_for_season(curr)
    leader = lb.iloc[0]["Tên VĐV"] if not lb.empty else "—"
    leader_wins = int(lb.iloc[0]["Thắng"]) if not lb.empty else 0
    total_matches = len(curr_matches)
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-copy">
            <div class="hero-kicker">Câu lạc bộ cầu lông HV</div>
            <h1>HV BADMINTON</h1>
            <div class="hero-desc">Theo dõi bảng xếp hạng, trận đấu và phong độ thành viên trong một giao diện gọn, nhanh và tối ưu cho cả điện thoại.</div>
            <div class="hero-stats">
              <div><div class="hero-stat-label">Thành viên</div><div class="hero-stat-value">{len(members_list)}</div></div>
              <div><div class="hero-stat-label">Trận đã ghi</div><div class="hero-stat-value">{total_matches}</div><div class="hero-stat-note">{html.escape(curr['name'])}</div></div>
              <div><div class="hero-stat-label">Dẫn đầu</div><div class="hero-stat-value">{leader_wins}</div><div class="hero-stat-note">{html.escape(str(leader))}</div></div>
            </div>
          </div>
          <div class="hero-art"></div>
        </div>
        <div class="summary-card">
          <div><div class="summary-label">Mùa hiện tại</div><div class="summary-main">{html.escape(curr['name'])}</div><div class="summary-meta">{html.escape(curr['status'] or 'Đang diễn ra')} · từ {html.escape(curr['start_str'])}</div></div>
          <a class="summary-link" href="?page=ranking">Xem bảng xếp hạng →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-rule"></div><div class="section-heading">Trận gần nhất</div>', unsafe_allow_html=True)
    render_match_cards(curr_matches, limit=6)

    st.markdown('<div class="section-rule"></div><div class="section-heading">Top phong độ</div>', unsafe_allow_html=True)
    render_podium(lb)

    st.markdown(
        """
        <div class="quick-grid">
          <a class="quick-card" href="?page=ranking"><div class="quick-title">🏆 Bảng xếp hạng</div><div class="quick-sub">Top thành viên và thống kê chi tiết</div></a>
          <a class="quick-card" href="?page=members"><div class="quick-title">👥 Thành viên</div><div class="quick-sub">Danh sách và thành tích VĐV</div></a>
          <a class="quick-card" href="?page=admin"><div class="quick-title">⚙️ Quản trị</div><div class="quick-sub">Ghi trận và quản lý dữ liệu</div></a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# BẢNG XẾP HẠNG
# =========================================================
elif page == "ranking":
    st.markdown('<div class="page-kicker">Trận giao lưu</div><div class="page-title">Bảng xếp hạng</div><div class="page-subtitle">Xếp hạng theo thành tích trong từng mùa giải.</div>', unsafe_allow_html=True)

    seasons_list = [s["name"] for s in seasons_info]
    c1, c2 = st.columns([3.4, 1.2])
    with c2:
        selected_season_name = st.selectbox("Giai đoạn", seasons_list, index=len(seasons_list) - 1, key="rank_season")
    curr = next((s for s in seasons_info if s["name"] == selected_season_name), seasons_info[-1])
    curr_matches = season_matches(curr)
    lb_base = calculate_leaderboard(curr_matches)

    metric = st.radio("Xếp theo", ["Trận thắng", "Số trận", "Tỉ lệ thắng", "Tổng điểm"], horizontal=True, label_visibility="collapsed", key="rank_metric")
    map_col = {"Trận thắng": "Thắng", "Số trận": "Tổng Trận", "Tỉ lệ thắng": "% Thắng", "Tổng điểm": "Điểm"}
    col = map_col[metric]
    ascending = metric == "Tổng điểm"
    if not lb_base.empty:
        lb = lb_base.sort_values([col, "% Thắng", "Thắng"], ascending=[ascending, False, False]).reset_index(drop=True)
    else:
        lb = lb_base

    value_suffix = {"Trận thắng": "thắng", "Số trận": "trận", "Tỉ lệ thắng": "%", "Tổng điểm": "điểm"}[metric]
    render_podium(lb, value_col=col, suffix=value_suffix)
    render_ranking_table(lb)

# =========================================================
# TRẬN ĐẤU
# =========================================================
elif page == "matches":
    st.markdown('<div class="page-kicker">Toàn câu lạc bộ</div><div class="page-title">Trận đấu</div><div class="page-subtitle">Lịch sử các trận đã ghi.</div>', unsafe_allow_html=True)
    if matches_parsed_df.empty:
        st.info("Chưa có trận đấu nào.")
    else:
        date_options = ["Tất cả các ngày"] + matches_parsed_df.sort_values("date_obj", ascending=False)["date"].drop_duplicates().tolist()
        selected_date = st.selectbox("Lọc theo ngày", date_options, key="match_date_filter")
        view = matches_parsed_df if selected_date == "Tất cả các ngày" else matches_parsed_df[matches_parsed_df["date"] == selected_date]
        for day in view.sort_values("date_obj", ascending=False)["date"].unique():
            day_df = view[view["date"] == day]
            st.markdown(f'<div class="section-rule"></div><div class="section-heading">{html.escape(day)} <span style="font-size:.75rem;color:#8a96a4;font-weight:500">· {len(day_df)} trận</span></div>', unsafe_allow_html=True)
            render_match_cards(day_df)

# =========================================================
# THÀNH VIÊN
# =========================================================
elif page == "members":
    st.markdown(f'<div class="page-kicker">Danh sách</div><div class="page-title">Thành viên</div><div class="page-subtitle">{len(members_list)} người</div>', unsafe_allow_html=True)
    query = st.text_input("Tìm thành viên", placeholder="Nhập tên VĐV...", label_visibility="collapsed")
    all_lb = calculate_leaderboard(matches_parsed_df)
    original = members_list[:]
    if query.strip():
        members_list[:] = [m for m in original if query.strip().lower() in m.lower()]
    render_member_cards(all_lb)
    members_list[:] = original

# =========================================================
# QUẢN TRỊ - GỘP TOÀN BỘ THAO TÁC Ở MỘT NƠI
# =========================================================
elif page == "admin":
    st.markdown('<div class="page-kicker">Khu vực quản lý</div><div class="page-title">Quản trị</div><div class="page-subtitle">Ghi trận, sửa/xóa dữ liệu, quản lý mùa và thành viên.</div>', unsafe_allow_html=True)
    tab_add, tab_edit, tab_season, tab_members = st.tabs(["📝 Ghi trận", "✏️ Sửa / Xóa trận", "🏆 Mùa giải", "👥 Thành viên"])

    with tab_add:
        curr = current_season_item()
        if len(members_list) < 4:
            st.warning("Cần tối thiểu 4 VĐV.")
        else:
            st.caption(f"Mùa hiện tại: **{curr['name']}**")
            with st.form("add_match_form", clear_on_submit=False):
                match_date = st.date_input("Ngày thi đấu", value=date.today(), format="DD/MM/YYYY")
                st.markdown("**🔵 Đội 1**")
                a1, a2, a3 = st.columns([2.2, 1, 1])
                with a1:
                    p1 = st.selectbox("VĐV 1", members_list, index=None, placeholder="Chọn VĐV...", key="add_p1")
                with a2:
                    k1_1 = st.number_input("Điểm", 0, 10, 1, key="add_k11")
                with a3:
                    score1 = st.number_input("Tỉ số", 0, 30, 21, key="add_s1")
                b1, b2, _ = st.columns([2.2, 1, 1])
                with b1:
                    p2 = st.selectbox("VĐV 2", members_list, index=None, placeholder="Chọn VĐV...", key="add_p2")
                with b2:
                    k1_2 = st.number_input("Điểm ", 0, 10, 1, key="add_k12")

                st.markdown("**🔴 Đội 2**")
                c1, c2, c3 = st.columns([2.2, 1, 1])
                with c1:
                    p3 = st.selectbox("VĐV 1 ", members_list, index=None, placeholder="Chọn VĐV...", key="add_p3")
                with c2:
                    k2_1 = st.number_input("Điểm  ", 0, 10, 1, key="add_k21")
                with c3:
                    score2 = st.number_input("Tỉ số ", 0, 30, 19, key="add_s2")
                d1, d2, _ = st.columns([2.2, 1, 1])
                with d1:
                    p4 = st.selectbox("VĐV 2 ", members_list, index=None, placeholder="Chọn VĐV...", key="add_p4")
                with d2:
                    k2_2 = st.number_input("Điểm   ", 0, 10, 1, key="add_k22")
                video_input = st.text_input("Link video YouTube (tùy chọn)")
                submitted = st.form_submit_button("💾 Lưu trận đấu", use_container_width=True, type="primary")
                if submitted:
                    players = [p1, p2, p3, p4]
                    if not all(players):
                        st.error("Vui lòng chọn đủ 4 VĐV.")
                    elif len(set(players)) < 4:
                        st.error("Không được trùng VĐV.")
                    elif score1 == score2:
                        st.error("Tỉ số hai đội không được bằng nhau.")
                    else:
                        m_date = format_date_vn(match_date)
                        assigned = curr["name"]
                        dt_obj = parse_date_obj(m_date)
                        for s in seasons_info:
                            if match_belong_to_season(dt_obj, s):
                                assigned = s["name"]
                                break
                        new_match = {
                            "Ngày": m_date,
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
                            "Đội Thắng": "Đội 1" if score1 > score2 else "Đội 2",
                            "Video": video_input.strip(),
                            "Mùa Giải": assigned,
                        }
                        if post_script({"action": "add_match", "match": new_match}):
                            finish_write("Đã lưu trận đấu!")

    with tab_edit:
        if matches_parsed_df.empty:
            st.info("Chưa có trận để chỉnh sửa.")
        else:
            work = matches_parsed_df.sort_values(["date_obj", "row_index"], ascending=[False, False]).copy()
            labels = []
            row_map = {}
            for _, m in work.iterrows():
                label = f"{m['date']} · {m['p1_1']}/{m['p1_2']} {m['score1']}-{m['score2']} {m['p2_1']}/{m['p2_2']}"
                labels.append(label)
                row_map[label] = m
            chosen = st.selectbox("Chọn trận", labels)
            m = row_map[chosen]
            with st.form("edit_match_form"):
                e1, e2 = st.columns(2)
                with e1:
                    st.markdown("**🔵 Đội 1**")
                    ep11 = st.selectbox("VĐV 1", members_list, index=members_list.index(m["p1_1"]) if m["p1_1"] in members_list else 0, key="ep11")
                    ep12 = st.selectbox("VĐV 2", members_list, index=members_list.index(m["p1_2"]) if m["p1_2"] in members_list else 0, key="ep12")
                    es1 = st.number_input("Tỉ số đội 1", 0, 30, int(m["score1"]), key="es1")
                with e2:
                    st.markdown("**🔴 Đội 2**")
                    ep21 = st.selectbox("VĐV 1 ", members_list, index=members_list.index(m["p2_1"]) if m["p2_1"] in members_list else 0, key="ep21")
                    ep22 = st.selectbox("VĐV 2 ", members_list, index=members_list.index(m["p2_2"]) if m["p2_2"] in members_list else 0, key="ep22")
                    es2 = st.number_input("Tỉ số đội 2", 0, 30, int(m["score2"]), key="es2")
                evideo = st.text_input("Link video", value=str(m["video_url"] or ""))
                save_edit = st.form_submit_button("💾 Lưu thay đổi", use_container_width=True, type="primary")
                if save_edit:
                    players = [ep11, ep12, ep21, ep22]
                    if len(set(players)) < 4:
                        st.error("Không được trùng VĐV.")
                    elif es1 == es2:
                        st.error("Tỉ số không được bằng nhau.")
                    else:
                        updated = {
                            "Ngày": m["date"],
                            "Đội 1 - VĐV 1": ep11,
                            "Kèo 1_1": int(m["k1_1"]),
                            "Đội 1 - VĐV 2": ep12,
                            "Kèo 1_2": int(m["k1_2"]),
                            "Điểm Đội 1": int(es1),
                            "Đội 2 - VĐV 1": ep21,
                            "Kèo 2_1": int(m["k2_1"]),
                            "Đội 2 - VĐV 2": ep22,
                            "Kèo 2_2": int(m["k2_2"]),
                            "Điểm Đội 2": int(es2),
                            "Đội Thắng": "Đội 1" if es1 > es2 else "Đội 2",
                            "Video": evideo.strip(),
                            "Mùa Giải": m["season"],
                        }
                        if post_script({"action": "edit_match", "row_index": int(m["row_index"]), "match": updated}, match_context=m):
                            finish_write("Đã cập nhật trận đấu!")
            if st.button("🗑️ Xóa trận đã chọn", use_container_width=True, key="delete_selected_match"):
                if post_script({"action": "delete_match", "row_index": int(m["row_index"])}, match_context=m):
                    finish_write("Đã xóa trận đấu!")

    with tab_season:
        seasons_list = [s["name"] for s in seasons_info]
        selected = st.selectbox("Chọn mùa", seasons_list, index=len(seasons_list) - 1, key="admin_season")
        item = next(s for s in seasons_info if s["name"] == selected)
        cadd, cedit = st.columns(2)
        with cadd:
            with st.form("add_season_form", clear_on_submit=True):
                st.markdown("**➕ Thêm mùa mới**")
                new_name = st.text_input("Tên mùa", placeholder=f"Mùa {len(seasons_list)+1} (2026)")
                new_start = st.date_input("Ngày bắt đầu", value=date.today(), format="DD/MM/YYYY")
                if st.form_submit_button("Tạo mùa", use_container_width=True):
                    name = new_name.strip() or f"Mùa {len(seasons_list)+1} (2026)"
                    if name in seasons_list:
                        st.error("Tên mùa đã tồn tại.")
                    elif post_script({"action": "add_season", "season_name": name, "start_date": format_date_vn(new_start)}):
                        finish_write(f"Đã tạo {name}!")
        with cedit:
            with st.form("edit_season_form"):
                st.markdown("**✏️ Chỉnh sửa mùa**")
                edit_name = st.text_input("Tên mùa ", value=item["name"])
                edit_start = st.date_input("Ngày bắt đầu ", value=item["start_obj"].date() if item["start_obj"] != datetime.min else date.today(), format="DD/MM/YYYY")
                edit_end = None
                if item["end_str"]:
                    edit_end = st.date_input("Ngày kết thúc", value=item["end_obj"].date(), format="DD/MM/YYYY")
                if st.form_submit_button("Lưu mùa", use_container_width=True):
                    payload = {"action": "edit_season", "old_name": selected, "new_name": edit_name.strip(), "start_date": format_date_vn(edit_start), "end_date": format_date_vn(edit_end) if edit_end else ""}
                    if post_script(payload):
                        finish_write("Đã cập nhật mùa!")
        cend, cdel = st.columns(2)
        with cend:
            if st.button("🛑 Kết thúc mùa", use_container_width=True):
                if post_script({"action": "end_season", "season_name": selected, "end_date": format_date_vn(date.today())}):
                    finish_write(f"Đã kết thúc {selected}!")
        with cdel:
            if st.button("🗑️ Xóa mùa", use_container_width=True):
                if post_script({"action": "delete_season", "season_name": selected}):
                    finish_write(f"Đã xóa {selected}!")

    with tab_members:
        with st.form("add_member_form", clear_on_submit=True):
            new_member = st.text_input("Tên VĐV mới")
            if st.form_submit_button("➕ Thêm thành viên", use_container_width=True, type="primary"):
                name = new_member.strip()
                if not name:
                    st.warning("Vui lòng nhập tên.")
                elif name in members_list:
                    st.error("Tên này đã tồn tại.")
                elif post_script({"action": "add_member", "name": name}):
                    finish_write(f"Đã thêm {name}!")
        if members_list:
            chosen_member = st.selectbox("Chọn thành viên để sửa/xóa", members_list)
            cedit, cdel = st.columns([2, 1])
            with cedit:
                with st.form("edit_member_form"):
                    updated_name = st.text_input("Tên mới", value=chosen_member)
                    if st.form_submit_button("Lưu tên", use_container_width=True):
                        clean = updated_name.strip()
                        if not clean:
                            st.warning("Tên không được để trống.")
                        elif clean in members_list and clean != chosen_member:
                            st.error("Tên đã tồn tại.")
                        elif post_script({"action": "edit_member", "old_name": chosen_member, "new_name": clean}):
                            finish_write("Đã cập nhật tên VĐV!")
            with cdel:
                st.write("")
                if st.button("🗑️ Xóa VĐV", use_container_width=True):
                    if post_script({"action": "delete_member", "name": chosen_member}):
                        finish_write(f"Đã xóa {chosen_member}!")
