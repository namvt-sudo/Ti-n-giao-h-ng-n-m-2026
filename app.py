import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
 
# 1. CẤU HÌNH TRANG WEB & CSS GIAO DIỆN SINH ĐỘNG - CHUYÊN NGHIỆP
st.set_page_config(page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng", layout="wide", initial_sidebar_state="collapsed")
 
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&display=swap');
 
    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }
 
    .stApp {
        background: linear-gradient(180deg, #eef4ff 0%, #f7faff 35%, #ffffff 100%);
    }
 
    .main { padding: 1rem 1.2rem; }
 
    /* ================= TIÊU ĐỀ CHÍNH ================= */
    .main-title {
        background: linear-gradient(90deg, #0d47a1 0%, #1565c0 45%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 32px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
        padding-bottom: 10px;
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
        margin-bottom: 10px;
    }
 
    /* ================= KHỐI BỘ LỌC (st.container(border=True)) ================= */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%) !important;
        border: 1.5px solid #bcd6ff !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 18px rgba(13,71,161,0.10) !important;
        padding: 6px 4px !important;
    }
 
    .sub-title-clean {
        color: #0d47a1;
        font-size: 21px;
        font-weight: 800;
        margin-top: 4px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
 
    /* NHÃN BỘ LỌC KIỂU "CHIP" MÀU SẮC - tự vẽ bằng HTML, không phụ thuộc testid nội bộ của Streamlit */
    .filter-chip-label {
        display: inline-block;
        background: linear-gradient(90deg, #e7f0ff, #ffffff);
        border: 1px solid #b9d4ff;
        border-left: 4px solid #1565c0;
        border-radius: 8px;
        padding: 5px 12px;
        margin-bottom: 6px;
        color: #0d47a1;
        font-weight: 800;
        font-size: 14.5px;
        box-shadow: 0 2px 6px rgba(13,71,161,0.08);
    }
    /* fallback: nếu bản Streamlit vẫn render label mặc định (label_visibility != collapsed) thì vẫn tô đậm */
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        opacity: 1 !important;
    }
 
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1.5px solid #93b8f2 !important;
        box-shadow: 0 1px 4px rgba(13,71,161,0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #1565c0 !important;
        box-shadow: 0 2px 10px rgba(21,101,192,0.18) !important;
    }
 
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #93b8f2 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1565c0 !important;
        box-shadow: 0 0 0 3px rgba(21,101,192,0.15) !important;
    }
 
    /* ================= TAB CHÍNH (DANH MỤC SẢN PHẨM) ================= */
    /* Bao phủ nhiều cấu trúc DOM khác nhau của Streamlit (role, baseweb, testid) */
    div[data-testid="stTabs"] [role="tablist"],
    div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
        gap: 10px !important;
        border-bottom: none !important;
        padding: 6px 6px 14px 6px !important;
        background: transparent !important;
        flex-wrap: wrap !important;
    }
 
    div[data-testid="stTabs"] [role="tab"],
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffffff, #f2f7ff) !important;
        border: 2px solid #93b8f2 !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        box-shadow: 0 3px 8px rgba(13,71,161,0.10) !important;
        transition: all 0.22s ease-in-out !important;
    }
 
    div[data-testid="stTabs"] [role="tab"] p,
    div[data-testid="stTabs"] [role="tab"] span,
    div[data-testid="stTabs"] [role="tab"] div {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }
 
    div[data-testid="stTabs"] [role="tab"]:hover {
        border-color: #00b4d8 !important;
        background: linear-gradient(135deg, #e6f7ff, #d6f0ff) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 6px 14px rgba(0,180,216,0.30) !important;
    }
 
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(120deg, #0d47a1, #1565c0 55%, #00b4d8) !important;
        border: 2px solid #0d47a1 !important;
        box-shadow: 0 6px 16px rgba(13,71,161,0.45) !important;
        transform: translateY(-2px) !important;
    }
 
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] div {
        color: #ffffff !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }
 
    /* Màu điểm nhấn riêng cho từng tab danh mục ở cấp ngoài cùng (Dashboard Tổng...) */
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(1)[aria-selected="true"] { background: linear-gradient(120deg, #0d47a1, #1565c0) !important; border-color: #0d47a1 !important; }
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(2)[aria-selected="true"] { background: linear-gradient(120deg, #00838f, #26c6da) !important; border-color: #00838f !important; }
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(3)[aria-selected="true"] { background: linear-gradient(120deg, #6a1b9a, #ab47bc) !important; border-color: #6a1b9a !important; }
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(4)[aria-selected="true"] { background: linear-gradient(120deg, #c2410c, #f97316) !important; border-color: #c2410c !important; }
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(5)[aria-selected="true"] { background: linear-gradient(120deg, #283593, #5c6bc0) !important; border-color: #283593 !important; }
    div[data-testid="stTabs"]:first-of-type > div > [role="tablist"] > [role="tab"]:nth-child(6)[aria-selected="true"] { background: linear-gradient(120deg, #37474f, #78909c) !important; border-color: #37474f !important; }
 
    /* Xoá vạch chỉ báo (indicator) mặc định màu đỏ của Streamlit */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }
 
    /* Tab con (Đơn Đặt Mới / Tồn / Đã Nhập Kho) - kiểu pill nhỏ nhẹ nhàng */
    div[data-testid="stTabs"] div[data-testid="stTabs"] [role="tab"] {
        border-radius: 20px !important;
        padding: 6px 16px !important;
    }
 
    /* ================= METRIC CARDS ================= */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #e3f2fd 60%, #d0ebff 100%);
        padding: 14px 16px;
        border-radius: 14px;
        border-left: 6px solid #1976d2;
        box-shadow: 0 4px 12px rgba(13,71,161,0.14);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 22px rgba(13,71,161,0.22);
    }
    div[data-testid="stMetricLabel"] {
        color: #0d47a1 !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0b3d91 !important;
        font-weight: 900 !important;
        font-size: 26px !important;
        background: linear-gradient(90deg, #0d47a1, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
 
    /* ================= BẢNG DỮ LIỆU (HTML table thật, thay cho st.dataframe canvas) ================= */
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
        font-size: 14px !important;
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
 
    /* ================= NÚT TẢI EXCEL ================= */
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #0d47a1, #00b4d8) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(13,71,161,0.30) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0,180,216,0.40) !important;
        filter: brightness(1.05);
    }
 
    .soft-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #b9d4ff, transparent);
        margin: 14px 0 18px 0;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)
 
# 2. HÀM XỬ LÝ DỮ LIỆU
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"
 
def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
 
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
    except:
        return 0.0
 
def clean_status(val):
    if pd.isna(val) or val is None:
        return 'Chưa SX'
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '']:
        return 'Chưa SX'
    return val_str
 
def tinh_canh_bao_tien_do(row):
    if row['Da_Nhap_Kho']:
        return "✅ Đã Hoàn Thành"
    if pd.isna(row['Ngay_Duyet_AB']):
        return "⚪ Chưa Duyệt SX (AB trống)"
    if pd.isna(row['Ngay_Chot_AG']):
        return "⚠️ Thiếu Ngày Chốt AG"
 
    ngay_hien_tai = pd.to_datetime('today').normalize()
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
 
def apply_style_safe(styler, func, subset):
    if hasattr(styler, 'map'):
        return styler.map(func, subset=subset)
    else:
        return styler.applymap(func, subset=subset)
 
def render_pretty_table(df_show, cols, q_col, table_key):
    """
    Render bảng bằng HTML table thật (qua pandas Styler.to_html) thay vì st.dataframe,
    vì st.dataframe render bằng canvas/WebGL nên CSS không style được tiêu đề/ô.
    Dùng HTML table cho phép kiểm soát toàn bộ giao diện: header rõ nét, dính khi cuộn, vằn màu.
    """
    label_map = {
        "Bo_Phan_KD": "Bộ Phận",
        "NV_KD": "NVKD",
        "Du_An": "Dự Án",
        "So_DH": "Mã ĐH",
        "Quy_Cach": "Quy Cách",
        "DVT": "ĐVT",
        q_col: "Số Lượng",
        "Canh_Bao_Tien_Do": "🚨 Cảnh Báo Tiến Độ",
        "Trang_Thai_SX": "Trạng Thái",
        "Ngay_Duyet_AB": "Duyệt SX (AB)",
        "Ngay_KD_Can_AC": "KD Cần (AC)",
        "Ngay_Chot_AG": "Chốt SX (AG)"
    }
 
    disp = df_show[cols].copy()
    for c in ['Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG']:
        if c in disp.columns:
            disp[c] = disp[c].dt.strftime('%d/%m/%Y')
            disp[c] = disp[c].fillna('')
    if q_col in disp.columns:
        disp[q_col] = disp[q_col].map(lambda v: f"{v:,.2f}")
 
    disp = disp.rename(columns=label_map)
    canh_bao_label = label_map.get("Canh_Bao_Tien_Do", "Canh_Bao_Tien_Do")
 
    styler = disp.style
    if canh_bao_label in disp.columns:
        styler = apply_style_safe(styler, style_canh_bao, subset=[canh_bao_label])
 
    try:
        styler = styler.hide(axis='index')
    except Exception:
        try:
            styler = styler.hide_index()
        except Exception:
            pass
 
    html = styler.to_html()
    if len(disp) == 0:
        st.markdown('<div class="table-wrap table-empty">Không có dữ liệu phù hợp.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="table-wrap">{html}</div>', unsafe_allow_html=True)
 
def convert_df_to_excel(df_moi, df_ton, df_done, cols, label_ky):
    output = io.BytesIO()
    clean_label = re.sub(r'[\/\\\?\*\:\[\]]', '-', str(label_ky))
    sheet_moi = f"Đặt Mới {clean_label}"[:31]
    sheet_ton = f"Tồn Trước {clean_label}"[:31]
    sheet_done = f"Đã Nhập Kho {clean_label}"[:31]
 
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_moi[cols].to_excel(writer, index=False, sheet_name=sheet_moi)
        df_ton[cols].to_excel(writer, index=False, sheet_name=sheet_ton)
        df_done[cols].to_excel(writer, index=False, sheet_name=sheet_done)
    return output.getvalue()
 
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)
 
    df = pd.DataFrame()
    df['So_DH'] = df_raw.iloc[3:, 1].replace('', None).ffill()
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].apply(clean_status)
    df['Nam_DatHang_Raw'] = df_raw.iloc[3:, 3].fillna('2026').astype(str).str.strip()
    df['Bo_Phan_KD'] = df_raw.iloc[3:, 4].astype(str).str.strip().fillna('Chưa phân loại')
    df['NV_KD'] = df_raw.iloc[3:, 6].astype(str).str.strip().fillna('Chưa phân loại')
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
 
    df['Nam_DatHang'] = df['Ngay_DatHang_DT'].dt.year.fillna(
        pd.to_numeric(df['Nam_DatHang_Raw'], errors='coerce')
    ).fillna(2026).astype(int)
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month.fillna(1).astype(int)
 
    df['Da_Nhap_Kho'] = (df['Trang_Thai_SX'].str.lower() == 'done') | (df['Ngay_NhapKho_DT'].notna())
    df['Ngay_NK_Check'] = df['Ngay_NhapKho_DT']
 
    df['Canh_Bao_Tien_Do'] = df.apply(tinh_canh_bao_tien_do, axis=1)
 
    return df
 
 
# 3. DASHBOARD MAIN RENDER
@st.fragment(run_every=10)
def render_dashboard():
    thoi_gian_cap_nhat = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
 
    st.markdown(f'<div class="update-badge">🔄 Cập nhật lúc: {thoi_gian_cap_nhat}</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG NĂM 2026</div>', unsafe_allow_html=True)
 
    try:
        df = load_data()
 
        filter_box = st.container(border=True)
        with filter_box:
            st.markdown('<div class="sub-title-clean">🎯 Bộ Lọc Tiến Độ Sản Xuất & Sản Lượng</div>', unsafe_allow_html=True)
 
            f1, f2, f3, f4, f5 = st.columns(5)
 
            with f1:
                st.markdown('<div class="filter-chip-label">📅 Chọn Năm Báo Cáo</div>', unsafe_allow_html=True)
                nam_list = ['Tất cả các năm'] + sorted(list(df['Nam_DatHang'].unique()))
                nam_sel = st.selectbox("Chọn Năm Báo Cáo", nam_list, index=nam_list.index(2026) if 2026 in nam_list else 0, label_visibility="collapsed")
 
            with f2:
                st.markdown('<div class="filter-chip-label">⏱️ Kỳ Báo Cáo</div>', unsafe_allow_html=True)
                ky_sel = st.selectbox("Kỳ Báo Cáo", ["Theo Tháng", "Theo Quý", "Cả Năm"], label_visibility="collapsed")
 
            with f3:
                thang_sel, quy_sel = None, None
                if ky_sel == "Theo Tháng":
                    st.markdown('<div class="filter-chip-label">🗓️ Chọn Tháng</div>', unsafe_allow_html=True)
                    danh_sach_thang = [f"Tháng {m}" for m in range(1, 13)]
                    thang_chon_str = st.selectbox("Chọn Tháng", danh_sach_thang, index=7, label_visibility="collapsed")
                    thang_sel = int(thang_chon_str.replace("Tháng ", ""))
                elif ky_sel == "Theo Quý":
                    st.markdown('<div class="filter-chip-label">📊 Chọn Quý</div>', unsafe_allow_html=True)
                    quy_chon_str = st.selectbox("Chọn Quý", ["Quý 1", "Quý 2", "Quý 3", "Quý 4"], index=2, label_visibility="collapsed")
                    quy_sel = int(quy_chon_str.replace("Quý ", ""))
                else:
                    st.markdown('<div class="filter-chip-label">🗓️ Chi Tiết Kỳ</div>', unsafe_allow_html=True)
                    st.selectbox("Chi Tiết Kỳ", ["Tất cả (Cả năm)"], disabled=True, label_visibility="collapsed")
 
            with f4:
                st.markdown('<div class="filter-chip-label">🏭 Tình Trạng SX</div>', unsafe_allow_html=True)
                tt_list = ['Tất cả tình trạng'] + sorted(list(df['Trang_Thai_SX'].unique()))
                tt_sel = st.selectbox("Tình Trạng SX", tt_list, label_visibility="collapsed")
 
            with f5:
                st.markdown('<div class="filter-chip-label">🏢 Bộ Phận KD</div>', unsafe_allow_html=True)
                bp_list = ['Tất cả bộ phận'] + sorted([x for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
                bp_sel = st.selectbox("Bộ Phận KD", bp_list, label_visibility="collapsed")
 
            col_nv, _ = st.columns([2, 3])
            with col_nv:
                st.markdown('<div class="filter-chip-label">👤 Nhân Viên KD</div>', unsafe_allow_html=True)
                df_nv_scope = df if bp_sel == 'Tất cả bộ phận' else df[df['Bo_Phan_KD'] == bp_sel]
                nv_list = ['Tất cả NVKD'] + sorted([x for x in df_nv_scope['NV_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
                nv_sel = st.selectbox("Nhân Viên KD", nv_list, label_visibility="collapsed")
 
        df_base = df.copy()
 
        if bp_sel != 'Tất cả bộ phận':
            df_base = df_base[df_base['Bo_Phan_KD'] == bp_sel]
        if nv_sel != 'Tất cả NVKD':
            df_base = df_base[df_base['NV_KD'] == nv_sel]
 
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
 
        # LỌC DỮ LIỆU
        cond_dat_moi = (df_base['Ngay_DatHang_DT'] >= start_date) & (df_base['Ngay_DatHang_DT'] <= end_date)
        df_moi = df_base[cond_dat_moi].copy()
 
        cond_dat_truoc = (df_base['Ngay_DatHang_DT'] < start_date)
        cond_chua_nk_truoc_ky = (~df_base['Da_Nhap_Kho']) | (df_base['Ngay_NK_Check'] >= start_date)
        df_ton = df_base[cond_dat_truoc & cond_chua_nk_truoc_ky].copy()
 
        cond_nhap_kho_trong_ky = (df_base['Ngay_NK_Check'] >= start_date) & (df_base['Ngay_NK_Check'] <= end_date)
        df_done = df_base[cond_nhap_kho_trong_ky].copy()
 
        if tt_sel != 'Tất cả tình trạng':
            df_moi = df_moi[df_moi['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
            df_ton = df_ton[df_ton['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
            df_done = df_done[df_done['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
 
        st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
 
        # TAB DANH MỤC
        tab_names = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Cột H (Phụ Kiện)', '📋 Sản Phẩm Khác']
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
                if tname == '📊 Dashboard Tổng':
                    q_col = 'So_Luong_Tong_DH'
                    sub_moi, sub_ton, sub_done = df_moi.copy(), df_ton.copy(), df_done.copy()
                else:
                    q_col = qty_mapping[tname]
                    sub_moi = df_moi[df_moi[q_col] > 0].copy()
                    sub_ton = df_ton[df_ton[q_col] > 0].copy()
                    sub_done = df_done[df_done[q_col] > 0].copy()
 
                cols_display = [
                    'Bo_Phan_KD', 'NV_KD', 'Du_An', 'So_DH', 'Quy_Cach', 'DVT', q_col,
                    'Canh_Bao_Tien_Do', 'Trang_Thai_SX', 'Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG'
                ]
 
                sl_dat_moi = sub_moi[q_col].sum()
                sl_ton_chuyen_sang = sub_ton[q_col].sum()
                sl_tong_can_sx = sl_dat_moi + sl_ton_chuyen_sang
                sl_da_nhap_kho = sub_done[q_col].sum()
                sl_con_lai = sl_tong_can_sx - sl_da_nhap_kho
 
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric(f"📦 Đặt Mới {ten_ky_hien_thi}", f"{sl_dat_moi:,.2f}")
                m2.metric(f"⏳ Tồn Lũy Kế Chuyển Sang", f"{sl_ton_chuyen_sang:,.2f}")
                m3.metric("🎯 Tổng Cần Sản Xuất", f"{sl_tong_can_sx:,.2f}")
                m4.metric(f"✅ Nhập Kho {ten_ky_hien_thi}", f"{sl_da_nhap_kho:,.2f}")
                m5.metric("⚠️ Còn Phải SX", f"{sl_con_lai:,.2f}")
 
                st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
 
                col_search, col_export = st.columns([3, 1])
                with col_search:
                    search_kw = st.text_input(f"🔍 Tìm kiếm nhanh (Mã ĐH, Dự án, Quy cách...):", key=f"s_{i}")
 
                if search_kw:
                    sub_moi = sub_moi[sub_moi['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]
                    sub_ton = sub_ton[sub_ton['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]
                    sub_done = sub_done[sub_done['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]
 
                with col_export:
                    st.write("")
                    st.write("")
                    excel_data = convert_df_to_excel(sub_moi, sub_ton, sub_done, cols_display, ten_ky_hien_thi)
                    tab_clean = tname.replace('📊 ', '').replace('📦 ', '').replace('⚙️ ', '').replace('🧱 ', '').replace('🏗️ ', '').replace('📋 ', '')
                    st.download_button(
                        label=f"📥 Trích Excel ({tab_clean})",
                        data=excel_data,
                        file_name=f"Bao_Cao_{tab_clean}_{re.sub(r'[\/\\\?\*\:\[\]]', '-', ten_ky_hien_thi)}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"btn_ex_{i}"
                    )
 
                sub_tab1, sub_tab2, sub_tab3 = st.tabs([
                    f"🆕 Đơn Đặt Mới ({len(sub_moi)} dòng)",
                    f"⌛ Đơn Tồn Quá Khứ Chuyển Sang ({len(sub_ton)} dòng)",
                    f"✅ Đơn Đã Nhập Kho Trong Kỳ ({len(sub_done)} dòng)"
                ])
 
                with sub_tab1:
                    render_pretty_table(sub_moi, cols_display, q_col, f"moi_{i}")
 
                with sub_tab2:
                    render_pretty_table(sub_ton, cols_display, q_col, f"ton_{i}")
 
                with sub_tab3:
                    render_pretty_table(sub_done, cols_display, q_col, f"done_{i}")
 
    except Exception as e:
        st.error(f"Lỗi kết nối hoặc xử lý dữ liệu: {e}")
 
# CHẠY HÀM DASHBOARD
render_dashboard()
 
