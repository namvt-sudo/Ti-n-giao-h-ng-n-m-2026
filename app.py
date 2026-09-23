import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. CẤU HÌNH TRANG WEB & CSS
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ẨN TOÀN BỘ THANH HEADER */
    header[data-testid="stHeader"],
    #MainMenu,
    .stAppDeployButton,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    .stApp {
        background: linear-gradient(180deg, #eef4ff 0%, #f7faff 35%, #ffffff 100%);
    }

    .main { padding: 0.8rem 1.2rem; }

    [data-stale="true"],
    [data-stale="true"] *,
    .main [data-stale="true"],
    .main [data-stale="true"] * {
        opacity: 1 !important;
        transition: none !important;
        animation: none !important;
        filter: none !important;
    }

    /* TIÊU ĐỀ CHÍNH */
    .main-title {
        background: linear-gradient(90deg, #0d47a1 0%, #1565c0 45%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 28px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
        padding-bottom: 8px;
        border-bottom: 4px solid transparent;
        border-image: linear-gradient(90deg, #0d47a1, #00b4d8, #90e0ef) 1;
    }

    .update-badge {
        display: inline-block;
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        background: linear-gradient(90deg, #1e88e5, #00acc1);
        padding: 4px 14px;
        border-radius: 20px;
        box-shadow: 0 3px 8px rgba(30,136,229,0.35);
        margin-bottom: 8px;
    }

    /* KHỐI BỘ LỌC */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%) !important;
        border: 1.5px solid #bcd6ff !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(13,71,161,0.08) !important;
        padding: 8px 12px !important;
    }

    .sub-title-clean {
        color: #0d47a1;
        font-size: 18px;
        font-weight: 800;
        margin-top: 2px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .filter-chip-label {
        display: inline-block;
        background: linear-gradient(90deg, #e7f0ff, #ffffff);
        border: 1px solid #b9d4ff;
        border-left: 4px solid #1565c0;
        border-radius: 8px;
        padding: 4px 8px;
        margin-bottom: 5px;
        color: #0d47a1;
        font-weight: 800;
        font-size: 13px;
        box-shadow: 0 2px 6px rgba(13,71,161,0.06);
    }

    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1.5px solid #93b8f2 !important;
        box-shadow: 0 1px 4px rgba(13,71,161,0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Ô TÌM KIẾM */
    .search-input-wrap div[data-testid="stTextInput"] {
        max-width: 320px !important;
    }
    .search-input-wrap div[data-testid="stTextInput"] input {
        border-radius: 20px !important;
        border: 1.5px solid #93b8f2 !important;
        padding-left: 14px !important;
        font-size: 13.5px !important;
        background-color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(13,71,161,0.06) !important;
    }

    /* TAB DANH MỤC */
    div[data-testid="stTabs"] [role="tablist"],
    div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: none !important;
        padding: 4px 6px 12px 6px !important;
        background: transparent !important;
        flex-wrap: wrap !important;
    }

    div[data-testid="stTabs"] [role="tab"],
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffffff, #f2f7ff) !important;
        border: 2px solid #93b8f2 !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        box-shadow: 0 3px 8px rgba(13,71,161,0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[data-testid="stTabs"] [role="tab"] p,
    div[data-testid="stTabs"] [role="tab"] span,
    div[data-testid="stTabs"] [role="tab"] div {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(120deg, #0d47a1, #1565c0 55%, #00b4d8) !important;
        border: 2px solid #0d47a1 !important;
        box-shadow: 0 6px 16px rgba(13,71,161,0.40) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] div {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }

    /* ================= THẺ METRIC: CĂN RA CHÍNH GIỮA TUYỆT ĐỐI ================= */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #edf5ff 60%, #d8edff 100%) !important;
        padding: 12px 16px !important;
        border-radius: 14px !important;
        border-left: 6px solid #1976d2 !important;
        box-shadow: 0 4px 12px rgba(13,71,161,0.12) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        margin: 0 auto !important;
        max-width: 320px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(13,71,161,0.22) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 14px !important;
        text-align: center !important;
        margin: 0 auto 4px auto !important;
        width: 100% !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0b3d91 !important;
        font-weight: 900 !important;
        font-size: 28px !important; /* Chữ số to nổi bật */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        width: 100% !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }
    div[data-testid="stMetricValue"] div {
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    /* BẢNG DỮ LIỆU */
    .table-wrap {
        max-height: 480px;
        overflow: auto;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(13,71,161,0.12);
        border: 1px solid #cfe0ff;
        margin-bottom: 8px;
    }
    .table-wrap.table-empty {
        max-height: none;
        padding: 18px;
        text-align: center;
        color: #64748b;
        font-weight: 600;
        background: #f8fafc;
    }
    .table-wrap table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 13.5px;
        background: #ffffff;
    }
    .table-wrap thead th {
        position: sticky;
        top: 0;
        z-index: 2;
        background: linear-gradient(90deg, #0d47a1, #1565c0 55%, #0d47a1) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        text-align: center !important;
        padding: 10px 12px !important;
        border-bottom: 2px solid #08306b !important;
        white-space: nowrap;
    }
    .table-wrap tbody td {
        padding: 8px 12px !important;
        color: #0f172a;
        border-bottom: 1px solid #e6edf7;
        white-space: nowrap;
    }
    .table-wrap tbody tr:nth-child(even) td {
        background-color: #f4f8ff;
    }
    .table-wrap tbody tr:hover td {
        background-color: #e3f0ff !important;
        transition: background-color 0.15s ease-in-out;
    }
    .table-wrap tbody th {
        display: none;
    }

    /* CỐ ĐỊNH & THU GỌN CỘT DỰ ÁN & QUY CÁCH */
    .table-wrap tbody td:nth-child(4),
    .table-wrap tbody td:nth-child(5) {
        max-width: 190px !important;
        min-width: 140px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        cursor: pointer !important;
        position: relative;
    }

    .table-wrap tbody td:nth-child(4):hover,
    .table-wrap tbody td:nth-child(5):hover,
    .table-wrap tbody td:nth-child(4):active,
    .table-wrap tbody td:nth-child(5):active {
        max-width: none !important;
        overflow: visible !important;
        white-space: normal !important;
        word-break: break-word !important;
        position: relative !important;
        z-index: 99 !important;
        background-color: #fff9c4 !important;
        color: #0d47a1 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
        border-radius: 6px !important;
    }

    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #0d47a1, #00b4d8) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 20px !important;
        border: none !important;
        font-size: 13.5px !important;
        padding: 6px 16px !important;
        box-shadow: 0 4px 12px rgba(13,71,161,0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,180,216,0.40) !important;
    }

    .soft-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #b9d4ff, transparent);
        margin: 12px 0 14px 0;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 2. XỬ LÝ DỮ LIỆU
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

_app_login_secrets = st.secrets.get("app_login", {}) if hasattr(st, "secrets") else {}
TEN_DANG_NHAP_CHUNG = _app_login_secrets.get("username", "VHIP")
MAT_KHAU_CHUNG = _app_login_secrets.get("password", "1")

def man_hinh_dang_nhap():
    st.markdown("""
        <div style='text-align:center; margin-top:30px; margin-bottom:10px;'>
            <div class="main-title" style="font-size:26px; display:inline-block;">🛡️ VHIP - ĐĂNG NHẬP HỆ THỐNG</div>
        </div>
    """, unsafe_allow_html=True)
    col_l, col_mid, col_r = st.columns([1, 1.4, 1])
    with col_mid:
        with st.container(border=True):
            st.caption("Nhập Tên đăng nhập và Mật khẩu chung của công ty để vào dashboard.")
            ten = st.text_input("Tên đăng nhập", key="login_ten")
            mk = st.text_input("Mật khẩu", type="password", key="login_mk")
            if st.button("Đăng Nhập", use_container_width=True, key="btn_dangnhap"):
                if ten.strip() == TEN_DANG_NHAP_CHUNG and mk == MAT_KHAU_CHUNG:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu.")

def clean_number(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip().replace('\xa0', '').replace(' ', '')
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
    if '.' in val_str and ',' in val_str:
        val_str = val_str.replace('.', '').replace(',', '.')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')
    elif '.' in val_str:
        parts = val_str.split('.')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace('.', '')
    try:
        return float(val_str)
    except Exception:
        return 0.0

def clean_status(val):
    if pd.isna(val) or val is None:
        return 'Chưa SX'
    val_str = str(val).strip()
    val_str = re.sub(r'\s+', ' ', val_str)
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '']:
        return 'Chưa SX'
    ban_do_chuan_hoa = {
        'chua sx': 'Chưa SX',
        'chưa sx': 'Chưa SX',
        'chua sản xuất': 'Chưa SX',
        'chưa sản xuất': 'Chưa SX',
        'dang sx': 'Đang SX',
        'đang sx': 'Đang SX',
        'dang sản xuất': 'Đang SX',
        'đang sản xuất': 'Đang SX',
        'tam dung sx': 'Tạm Dừng SX',
        'tạm dừng sx': 'Tạm Dừng SX',
        'tam dung': 'Tạm Dừng SX',
        'tạm dừng': 'Tạm Dừng SX',
        'done': 'Done',
        'hoan thanh': 'Done',
        'hoàn thành': 'Done',
    }
    return ban_do_chuan_hoa.get(val_str.lower(), val_str)

def chuan_hoa_ten_nv(ten):
    if pd.isna(ten) or ten is None:
        return ''
    s = str(ten).strip()
    s_new = re.sub(r'^(mr|ms|mrs)\.?\s*', '', s, flags=re.IGNORECASE).strip()
    s_new = re.sub(r'\s+', ' ', s_new)
    return s_new if s_new else s

def tinh_canh_bao_tien_do(row):
    if row['Da_Nhap_Kho']:
        return "✅ Đã Hoàn Thành"
    if pd.isna(row['Ngay_Duyet_AB']):
        return "⚪ Chưa Duyệt SX (AB trống)"
    if pd.isna(row['Ngay_Chot_AG']):
        return "⚠️ Thiếu Ngày Chốt AG"

    ngay_hien_tai = pd.Timestamp.now(tz=ZoneInfo("Asia/Ho_Chi_Minh")).tz_localize(None).normalize()
    songay_con_lai = (row['Ngay_Chot_AG'] - ngay_hien_tai).days

    if songay_con_lai <= 5:
        return "🔴 Rất Nguy Hiểm (≤ 5 Ngày)"
    elif songay_con_lai <= 7:
        return "🟠 Cấp Bách / Ưu Tiên (6-7 Ngày)"
    elif songay_con_lai <= 15:
        return "🟡 Tiến Độ Bình Thường (8-15 Ngày)"
    elif songay_con_lai <= 30:
        return "🟢 An Toàn (16-30 Ngày)"
    else:
        return "🔵 Rất An Toàn (> 30 Ngày)"

def style_canh_bao(val):
    if '🔴' in str(val):
        return 'background-color: #ffc9c9; color: #900C3F; font-weight: bold;'
    elif '🟠' in str(val):
        return 'background-color: #ffe5b4; color: #d35400; font-weight: bold;'
    elif '🟡' in str(val):
        return 'background-color: #fff9c4; color: #856404;'
    elif '🟢' in str(val):
        return 'background-color: #d4edda; color: #155724;'
    elif '⚪' in str(val):
        return 'background-color: #e9ecef; color: #6c757d;'
    return ''

def format_number_smart(val):
    if pd.isna(val) or val is None:
        return "0"
    try:
        f_val = float(val)
        if f_val.is_integer():
            return f"{int(f_val):,}"
        return f"{f_val:,.2f}"
    except Exception:
        return str(val)

def render_pretty_table(df_show, cols, q_col, table_key):
    label_map = {
        "So_DH": "Mã ĐH",
        "Bo_Phan_KD": "Bộ Phận",
        "NV_KD": "NVKD",
        "Du_An": "Dự Án",
        "Quy_Cach": "Quy Cách",
        "DVT": "ĐVT",
        q_col: "Số Lượng",
        "Canh_Bao_Tien_Do": "🚨 Cảnh Báo Tiến Độ",
        "Trang_Thai_SX": "Trạng Thái",
        "Ngay_Duyet_AB": "Duyệt Base SX",
        "Ngay_KD_Can_AC": "KD Cần Ngày Giao Hàng",
        "Ngay_Chot_AG": "Chốt Tiến Độ Giao Hàng VHIP-KD",
        "Ngay_NhapKho_DT": "Ngày Nhập Kho Thực Tế"
    }

    disp = df_show[cols].copy()
    for c in ['Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG', 'Ngay_NhapKho_DT']:
        if c in disp.columns:
            disp[c] = disp[c].dt.strftime('%d/%m/%Y').fillna('')
    if q_col in disp.columns:
        disp[q_col] = disp[q_col].map(format_number_smart)

    disp = disp.rename(columns=label_map)
    canh_bao_label = label_map.get("Canh_Bao_Tien_Do", "Canh_Bao_Tien_Do")

    styler = disp.style.set_uuid(re.sub(r'[^a-zA-Z0-9_-]', '_', str(table_key)))
    if canh_bao_label in disp.columns:
        if hasattr(styler, 'map'):
            styler = styler.map(style_canh_bao, subset=[canh_bao_label])
        else:
            styler = styler.applymap(style_canh_bao, subset=[canh_bao_label])

    try:
        styler = styler.hide(axis='index')
    except Exception:
        try:
            styler = styler.hide_index()
        except Exception:
            pass

    if len(disp) == 0:
        st.markdown('<div class="table-wrap table-empty">Không có dữ liệu phù hợp.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="table-wrap">{styler.to_html()}</div>', unsafe_allow_html=True)

def convert_df_to_excel_by_product(df_moi, df_ton, df_done, cols, ten_ky, ten_san_pham):
    output = io.BytesIO()
    clean_sp = re.sub(r'[\/\\\?\*\:\[\]]', '-', str(ten_san_pham)).strip()
    sheet_moi = f"Đặt mới {clean_sp}"[:31]
    sheet_ton = f"Tồn {clean_sp}"[:31]
    sheet_done = f"Nhập kho {clean_sp}"[:31]

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_moi[cols].to_excel(writer, index=False, sheet_name=sheet_moi)
        df_ton[cols].to_excel(writer, index=False, sheet_name=sheet_ton)
        df_done[cols].to_excel(writer, index=False, sheet_name=sheet_done)
    return output.getvalue()

@st.cache_data(ttl=180, show_spinner=False)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

    df = pd.DataFrame()
    df['So_DH'] = df_raw.iloc[3:, 1].replace('', None).ffill()
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].apply(clean_status)
    df['Nam_DatHang_Raw'] = df_raw.iloc[3:, 3].fillna('2026').astype(str).str.strip()
    df['Bo_Phan_KD'] = df_raw.iloc[3:, 4].astype(str).str.strip().fillna('Chưa phân loại')
    df['NV_KD'] = df_raw.iloc[3:, 6].astype(str).str.strip().fillna('Chưa phân loại')
    df['NV_KD_ChuanHoa'] = df['NV_KD'].apply(chuan_hoa_ten_nv)
    df['Du_An'] = df_raw.iloc[3:, 7].fillna('')
    df['Quy_Cach'] = df_raw.iloc[3:, 9].fillna('')
    df['DVT'] = df_raw.iloc[3:, 10].fillna('cái')
    df['So_Luong_Tong_DH_Raw'] = df_raw.iloc[3:, 13]

    df['SL_KheRangLuoc'] = df_raw.iloc[3:, 14].apply(clean_number)
    df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)
    df['SL_TamVCO'] = df_raw.iloc[3:, 23].apply(clean_number)
    df['SL_HeCotPhuKien'] = df_raw.iloc[3:, 24].apply(clean_number)

    df['SL_KheRangLuocNhom'] = df_raw.iloc[3:, 16].apply(clean_number)
    df['SL_LoXoNeo'] = df_raw.iloc[3:, 17].apply(clean_number)
    df['SL_ThanhNeo'] = df_raw.iloc[3:, 18].apply(clean_number)
    df['SL_SPKhac'] = df_raw.iloc[3:, 19].apply(clean_number)
    df['SL_TamDeNeo'] = df_raw.iloc[3:, 20].apply(clean_number)
    df['SL_StelPin'] = df_raw.iloc[3:, 21].apply(clean_number)
    df['SL_VanKhuon'] = df_raw.iloc[3:, 22].apply(clean_number)
    df['SL_LanCan'] = df_raw.iloc[3:, 25].apply(clean_number)

    df['Ngay_GuiDH_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')
    df['Ngay_Duyet_AB'] = pd.to_datetime(df_raw.iloc[3:, 27], dayfirst=True, errors='coerce')
    df['Ngay_KD_Can_AC'] = pd.to_datetime(df_raw.iloc[3:, 28], dayfirst=True, errors='coerce')
    df['Ngay_Chot_AG'] = pd.to_datetime(df_raw.iloc[3:, 32], dayfirst=True, errors='coerce')
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce')

    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number)
    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom'] + df['SL_LoXoNeo'] + df['SL_ThanhNeo'] +
        df['SL_SPKhac'] + df['SL_TamDeNeo'] + df['SL_StelPin'] +
        df['SL_VanKhuon'] + df['SL_LanCan']
    )
    df['SL_TongCalculated'] = df['SL_KheRangLuoc'] + df['SL_GoiChau'] + df['SL_TamVCO'] + df['SL_HeCotPhuKien'] + df['SL_NhomKhac']
    df.loc[df['So_Luong_Tong_DH'] <= 0, 'So_Luong_Tong_DH'] = df.loc[df['So_Luong_Tong_DH'] <= 0, 'SL_TongCalculated']

    df['Ngay_DatHang_DT'] = df['Ngay_GuiDH_DT'].fillna(df['Ngay_Chot_AG']).fillna(df['Ngay_Duyet_AB'])
    df['Nam_DatHang'] = df['Ngay_DatHang_DT'].dt.year.fillna(pd.to_numeric(df['Nam_DatHang_Raw'], errors='coerce')).fillna(2026).astype(int)
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month.fillna(1).astype(int)
    df['Da_Nhap_Kho'] = (df['Trang_Thai_SX'].str.lower() == 'done') | (df['Ngay_NhapKho_DT'].notna())
    df['Ngay_NK_Check'] = df['Ngay_NhapKho_DT']
    df['Canh_Bao_Tien_Do'] = df.apply(tinh_canh_bao_tien_do, axis=1)

    return df

# 3. GIAO DIỆN CHÍNH
@st.fragment(run_every=180)
def render_dashboard():
    thoi_gian_cap_nhat = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y %H:%M:%S")

    col_badge, col_refresh = st.columns([5, 1])
    with col_badge:
        st.markdown(f'<div class="update-badge">🔄 Cập nhật lúc: {thoi_gian_cap_nhat} (tự động mỗi 3 phút)</div>', unsafe_allow_html=True)
    with col_refresh:
        if st.button("⚡ Làm Mới Ngay", use_container_width=True, key="btn_lam_moi_ngay"):
            load_data.clear()

    st.markdown('<div class="main-title">🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG NĂM 2026</div>', unsafe_allow_html=True)

    try:
        df = load_data()

        with st.container(border=True):
            st.markdown('<div class="sub-title-clean">🎯 Bộ Lọc Tiến Độ Sản Xuất & Sản Lượng</div>', unsafe_allow_html=True)
            f1, f2, f3, f4, f5, f6 = st.columns(6)

            with f1:
                st.markdown('<div class="filter-chip-label">📅 Chọn Năm</div>', unsafe_allow_html=True)
                nam_list = ['Tất cả các năm'] + sorted(list(df['Nam_DatHang'].unique()))
                nam_sel = st.selectbox("Năm", nam_list, index=nam_list.index(2026) if 2026 in nam_list else 0, label_visibility="collapsed")

            with f2:
                st.markdown('<div class="filter-chip-label">⏱️ Kỳ Báo Cáo</div>', unsafe_allow_html=True)
                ky_sel = st.selectbox("Kỳ", ["Theo Tháng", "Theo Quý", "Cả Năm"], index=2, label_visibility="collapsed")

            with f3:
                thang_sel, quy_sel = None, None
                if ky_sel == "Theo Tháng":
                    st.markdown('<div class="filter-chip-label">🗓️ Chọn Tháng</div>', unsafe_allow_html=True)
                    danh_sach_thang = [f"Tháng {m}" for m in range(1, 13)]
                    thang_chon_str = st.selectbox("Tháng", danh_sach_thang, index=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).month - 1, label_visibility="collapsed")
                    thang_sel = int(thang_chon_str.replace("Tháng ", ""))
                elif ky_sel == "Theo Quý":
                    st.markdown('<div class="filter-chip-label">📊 Chọn Quý</div>', unsafe_allow_html=True)
                    quy_chon_str = st.selectbox("Quý", ["Quý 1", "Quý 2", "Quý 3", "Quý 4"], index=2, label_visibility="collapsed")
                    quy_sel = int(quy_chon_str.replace("Quý ", ""))
                else:
                    st.markdown('<div class="filter-chip-label">🗓️ Chi Tiết Kỳ</div>', unsafe_allow_html=True)
                    st.selectbox("Kỳ chi tiết", ["Tất cả (Cả năm)"], disabled=True, label_visibility="collapsed")

            with f4:
                st.markdown('<div class="filter-chip-label">🏭 Tình Trạng SX</div>', unsafe_allow_html=True)
                tt_list = ['Tất cả tình trạng'] + sorted([x for x in df['Trang_Thai_SX'].unique() if str(x).strip().lower() != 'vhip'])
                tt_sel = st.selectbox("Tình trạng", tt_list, label_visibility="collapsed")

            with f5:
                st.markdown('<div class="filter-chip-label">🏢 Bộ Phận KD</div>', unsafe_allow_html=True)
                bp_list = ['Tất cả bộ phận'] + sorted([x for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
                bp_sel = st.selectbox("Bộ phận", bp_list, label_visibility="collapsed")

            with f6:
                st.markdown('<div class="filter-chip-label">👤 Nhân Viên KD</div>', unsafe_allow_html=True)
                df_nv_scope = df if bp_sel == 'Tất cả bộ phận' else df[df['Bo_Phan_KD'] == bp_sel]
                nv_list = ['Tất cả NVKD'] + sorted([x for x in df_nv_scope['NV_KD_ChuanHoa'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
                nv_sel = st.selectbox("NVKD", nv_list, label_visibility="collapsed")

        df_base = df.copy()
        if bp_sel != 'Tất cả bộ phận':
            df_base = df_base[df_base['Bo_Phan_KD'] == bp_sel]
        if nv_sel != 'Tất cả NVKD':
            df_base = df_base[df_base['NV_KD_ChuanHoa'] == nv_sel]

        nam_eff = 2026 if nam_sel == 'Tất cả các năm' else int(nam_sel)
        if ky_sel == "Theo Tháng" and thang_sel:
            start_date = pd.Timestamp(year=nam_eff, month=thang_sel, day=1)
            end_date = start_date + pd.offsets.MonthEnd(1)
            ten_ky_hien_thi = f"Tháng {thang_sel}/{nam_eff}"
        elif ky_sel == "Theo Quý" and quy_sel:
            start_month = (quy_sel - 1) * 3 + 1
            start_date = pd.Timestamp(year=nam_eff, month=start_month, day=1)
            end_date = start_date + pd.DateOffset(months=3) - pd.Timedelta(days=1)
            ten_ky_hien_thi = f"Quý {quy_sel}/{nam_eff}"
        else:
            start_date = pd.Timestamp(year=nam_eff, month=1, day=1)
            end_date = pd.Timestamp(year=nam_eff, month=12, day=31)
            ten_ky_hien_thi = f"Năm {nam_eff}"

        cond_dat_moi = (df_base['Ngay_DatHang_DT'] >= start_date) & (df_base['Ngay_DatHang_DT'] <= end_date)
        df_moi = df_base[cond_dat_moi].copy()
        cond_dat_truoc = (df_base['Ngay_DatHang_DT'] < start_date)
        cond_chua_nk_truoc_ky = (~df_base['Da_Nhap_Kho']) | (df_base['Ngay_NK_Check'] >= start_date)
        df_ton = df_base[cond_dat_truoc & cond_chua_nk_truoc_ky].copy()
        cond_nhap_kho_trong_ky = (df_base['Ngay_NK_Check'] >= start_date) & (df_base['Ngay_NK_Check'] <= end_date)
        df_done = df_base[cond_nhap_kho_trong_ky].copy()

        if tt_sel != 'Tất cả tình trạng':
            mask_trang_thai = lambda df_x: df_x['Trang_Thai_SX'].str.lower().isin(['đang sx', 'done']) if tt_sel.lower() == 'đang sx' else df_x['Trang_Thai_SX'].str.lower() == tt_sel.lower()
            df_moi = df_moi[mask_trang_thai(df_moi)]
            df_ton = df_ton[mask_trang_thai(df_ton)]
            df_done = df_done[mask_trang_thai(df_done)]

        st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

        tab_names = ['📊 Dashboard Tổng', '🚨 Chưa Chốt Tiến Độ Giao Hàng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Cột H (Phụ Kiện)', '📋 Sản Phẩm Khác']
        tabs = st.tabs(tab_names)
        qty_mapping = {
            '📦 Gối Chậu': 'SL_GoiChau',
            '⚙️ Khe Răng Lược': 'SL_KheRangLuoc',
            '🧱 Tấm VCO': 'SL_TamVCO',
            '🏗️ Cột H (Phụ Kiện)': 'SL_HeCotPhuKien',
            '📋 Sản Phẩm Khác': 'SL_NhomKhac'
        }

        for i, tname in enumerate(tab_names):
            with tabs[i]:
                ten_sp_thuan = tname.replace('📊 ', '').replace('🚨 ', '').replace('📦 ', '').replace('⚙️ ', '').replace('🧱 ', '').replace('🏗️ ', '').replace('📋 ', '')

                if tname == '🚨 Chưa Chốt Tiến Độ Giao Hàng':
                    q_col = 'So_Luong_Tong_DH'
                    df_chua_chot = pd.concat([df_moi, df_ton])
                    df_chua_chot = df_chua_chot[df_chua_chot['Ngay_Chot_AG'].isna()]
                    cols_display = ['So_DH', 'Bo_Phan_KD', 'NV_KD', 'Du_An', 'Quy_Cach', 'DVT', q_col, 'Canh_Bao_Tien_Do', 'Trang_Thai_SX', 'Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG', 'Ngay_NhapKho_DT']

                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    mc0, mc1, mc2, mc3 = st.columns(4)
                    mc0.metric("📄 ĐH Chưa Chốt", format_number_smart(len(df_chua_chot)))
                    mc1.metric("📦 Gối Chậu", format_number_smart(df_chua_chot['SL_GoiChau'].sum()))
                    mc2.metric("⚙️ Khe Răng", format_number_smart(df_chua_chot['SL_KheRangLuoc'].sum()))
                    mc3.metric("🧱 Tấm VCO", format_number_smart(df_chua_chot['SL_TamVCO'].sum()))

                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    mc4, mc5, mc6 = st.columns(3)
                    mc4.metric("🏗️ Cột H (Phụ Kiện)", format_number_smart(df_chua_chot['SL_HeCotPhuKien'].sum()))
                    mc5.metric("📋 Sản Phẩm Khác", format_number_smart(df_chua_chot['SL_NhomKhac'].sum()))
                    mc6.metric("🎯 Tổng Cộng", format_number_smart(df_chua_chot[q_col].sum()))

                    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
                    
                    col_search, col_export, _ = st.columns([1.8, 1.4, 2.8])
                    with col_search:
                        st.markdown('<div class="search-input-wrap">', unsafe_allow_html=True)
                        search_kw = st.text_input("Tìm:", placeholder="🔍 Nhập Mã ĐH, Dự án...", key=f"s_{i}", label_visibility="collapsed")
                        st.markdown('</div>', unsafe_allow_html=True)

                    df_show = df_chua_chot[df_chua_chot['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)] if search_kw else df_chua_chot

                    with col_export:
                        excel_buf = io.BytesIO()
                        with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
                            df_show[cols_display].to_excel(writer, index=False, sheet_name="Chua Chot Tien Do")
                        st.download_button(
                            label="📥 Xuất Excel (Chưa Chốt)",
                            data=excel_buf.getvalue(),
                            file_name=f"Chua_Chot_Tien_Do_{re.sub(r'[\/\\\?\*\:\[\]]', '-', ten_ky_hien_thi)}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key=f"btn_ex_{i}"
                        )

                    render_pretty_table(df_show, cols_display, q_col, f"chuachot_{i}")
                    continue

                q_col = 'So_Luong_Tong_DH' if tname == '📊 Dashboard Tổng' else qty_mapping[tname]
                sub_moi = df_moi if tname == '📊 Dashboard Tổng' else df_moi[df_moi[q_col] > 0]
                sub_ton = df_ton if tname == '📊 Dashboard Tổng' else df_ton[df_ton[q_col] > 0]
                sub_done = df_done if tname == '📊 Dashboard Tổng' else df_done[df_done[q_col] > 0]

                cols_display = ['So_DH', 'Bo_Phan_KD', 'NV_KD', 'Du_An', 'Quy_Cach', 'DVT', q_col, 'Canh_Bao_Tien_Do', 'Trang_Thai_SX', 'Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG', 'Ngay_NhapKho_DT']

                sub_ton_can = sub_ton[sub_ton['Ngay_KD_Can_AC'].isna() | ((sub_ton['Ngay_KD_Can_AC'] >= start_date) & (sub_ton['Ngay_KD_Can_AC'] <= end_date))]
                sub_moi_can = sub_moi[sub_moi['Ngay_KD_Can_AC'].isna() | ((sub_moi['Ngay_KD_Can_AC'] >= start_date) & (sub_moi['Ngay_KD_Can_AC'] <= end_date))]
                
                _khong_tam_dung = lambda d: d[~d['Trang_Thai_SX'].astype(str).str.lower().str.contains('tạm dừng', na=False)]
                _ton_dong = lambda d: d[~(d['Da_Nhap_Kho'] & d['Ngay_NhapKho_DT'].notna() & (d['Ngay_NhapKho_DT'] <= end_date))]

                # BỐ TRÍ 2 HÀNG x 3 CỘT: CĂN GIỮA NỘI DUNG, CHỮ TO RÕ RÀNG
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric(f"📦 Đặt Mới {ten_ky_hien_thi}", format_number_smart(sub_moi[q_col].sum()))
                m2.metric("🔥 Đặt & Cần Giao", format_number_smart(sub_moi_can[q_col].sum()))
                m3.metric("⏳ Tồn Lũy Kế", format_number_smart(sub_ton_can[q_col].sum()))

                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                m4, m5, m6 = st.columns(3)
                m4.metric("🎯 Tổng Cần SX", format_number_smart(_khong_tam_dung(sub_moi_can)[q_col].sum() + _khong_tam_dung(sub_ton_can)[q_col].sum()))
                m5.metric("✅ Đã Nhập Kho", format_number_smart(sub_done[q_col].sum()))
                m6.metric("⚠️ Còn Phải SX", format_number_smart(_khong_tam_dung(_ton_dong(sub_moi_can))[q_col].sum() + _khong_tam_dung(_ton_dong(sub_ton_can))[q_col].sum()))

                st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

                col_s, col_e, _ = st.columns([1.8, 1.4, 2.8])
                with col_s:
                    st.markdown('<div class="search-input-wrap">', unsafe_allow_html=True)
                    search_kw = st.text_input(f"Tìm:", placeholder=f"🔍 Tìm trong {ten_sp_thuan}...", key=f"s_{i}", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)

                sub_moi_view = sub_moi[sub_moi['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)] if search_kw else sub_moi
                sub_ton_view = sub_ton_can[sub_ton_can['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)] if search_kw else sub_ton_can
                sub_done_view = sub_done[sub_done['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)] if search_kw else sub_done

                with col_e:
                    excel_data = convert_df_to_excel_by_product(sub_moi_view, sub_ton_view, sub_done_view, cols_display, ten_ky_hien_thi, ten_sp_thuan)
                    st.download_button(
                        label=f"📥 Xuất Excel ({ten_sp_thuan})",
                        data=excel_data,
                        file_name=f"Bao_Cao_{re.sub(r'[^a-zA-Z0-9_-]', '_', ten_sp_thuan)}_{re.sub(r'[\/\\\?\*\:\[\]]', '-', ten_ky_hien_thi)}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"btn_ex_{i}"
                    )

                st1, st2, st3 = st.tabs(["🆕 Đơn Đặt Mới", "⌛ Đơn Tồn Cần Giao", "✅ Đơn Đã Nhập Kho"])
                with st1:
                    render_pretty_table(sub_moi_view, cols_display, q_col, f"moi_{i}")
                with st2:
                    render_pretty_table(sub_ton_view, cols_display, q_col, f"ton_{i}")
                with st3:
                    render_pretty_table(sub_done_view, cols_display, q_col, f"done_{i}")

    except Exception as e:
        st.error(f"Lỗi kết nối hoặc xử lý dữ liệu: {e}")

# 4. ĐĂNG NHẬP
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    man_hinh_dang_nhap()
    st.stop()

col_user, col_logout = st.columns([5, 1])
with col_user:
    st.markdown("👤 Đã đăng nhập")
with col_logout:
    if st.button("🚪 Đăng Xuất", use_container_width=True, key="btn_dangxuat"):
        st.session_state.logged_in = False
        st.rerun()

render_dashboard()
