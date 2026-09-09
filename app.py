import streamlit as st
import pandas as pd
import re

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG WEB & TỐI ƯU CSS (GIAO DIỆN HIỆN ĐẠI)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng", 
    page_icon="🛡️",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Bố cục & Spacing */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Custom Card Metric */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #6c757d;
        font-size: 0.875rem;
    }
    div[data-testid="stMetricValue"] {
        font-weight: 700;
        color: #212529;
    }

    /* Custom Style Cho Tab Header */
    div[data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 8px;
    }
    button[data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 18px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        font-weight: 600 !important;
        color: #495057 !important;
        transition: all 0.2s ease;
    }
    button[aria-selected="true"] {
        background-color: #0d6efd !important;
        color: white !important;
        border-color: #0d6efd !important;
        box-shadow: 0 2px 6px rgba(13, 110, 253, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG")

# -----------------------------------------------------------------------------
# 2. XỬ LÝ DỮ LIỆU & CACHING
# -----------------------------------------------------------------------------
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"  # Tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

def clean_number_exact(val):
    """
    Hàm chuẩn hóa chuỗi số về kiểu float an toàn.
    Xử lý thông minh dấu phân cách hàng nghìn (, hoặc .) và dấu thập phân.
    """
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip().replace('\xa0', '').replace(' ', '')
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0

    has_comma = ',' in val_str
    has_dot = '.' in val_str

    if has_comma and has_dot:
        if val_str.rfind(',') > val_str.rfind('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif has_comma:
        parts = val_str.split(',')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace(',', '')
        else:
            val_str = val_str.replace(',', '.')
    elif has_dot:
        parts = val_str.split('.')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace('.', '')

    try:
        return float(val_str)
    except ValueError:
        return 0.0

@st.cache_data(ttl=60, show_spinner="Đang đồng bộ dữ liệu từ Google Sheets...")
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    
    # Đọc tất cả dòng dưới dạng string để tránh lỗi định dạng tự động của Pandas
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

    # Đọc từ dòng index 4 (Dòng 5 Excel)
    df = pd.DataFrame({
        'So_DH_Raw': df_raw.iloc[4:, 1],              # Cột B
        'Trang_Thai_SX': df_raw.iloc[4:, 2],          # Cột C
        'Nam_Dat_Hang_Raw': df_raw.iloc[4:, 3],       # Cột D
        'Bo_Phan_KD': df_raw.iloc[4:, 4],             # Cột E
        'NV_KD': df_raw.iloc[4:, 6],                 # Cột G
        'Du_An': df_raw.iloc[4:, 7],                 # Cột H
        'Quy_Cach': df_raw.iloc[4:, 9],              # Cột J
        'DVT': df_raw.iloc[4:, 10],                  # Cột K
        'Nhom_SP': df_raw.iloc[4:, 12],              # Cột M
        'So_Luong_Tong_DH_Raw': df_raw.iloc[4:, 13]  # Cột N
    })

    # Đọc cột ngày
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, 27], dayfirst=True, errors='coerce')    # AB
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, 28], dayfirst=True, errors='coerce')        # AC
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, 32], dayfirst=True, errors='coerce')   # AG
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, 33], dayfirst=True, errors='coerce')    # AH

    # Tự động điền dữ liệu cho các ô gộp Merge Center (ffill)
    df['So_DH'] = df['So_DH_Raw'].replace('', None).ffill()
    df['Nam_Col_D'] = df['Nam_Dat_Hang_Raw'].replace('', None).ffill().astype(str).str.extract(r'(\d{4})')[0]

    # Loại bỏ dòng tiêu đề lặp hoặc dòng tổng
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|TỔNG|STT|Số ĐH', case=False, na=False)]

    # Chuẩn hóa Số lượng
    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number_exact)
    df = df[df['So_Luong_Tong_DH'] > 0]

    # Trích xuất Năm
    df['Nam_Duyet'] = df['Ngay_Duyet_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Dat_Hang'] = df['Nam_Col_D'].fillna(df['Nam_Duyet']).fillna(df['Nam_Chot']).fillna('Khác')

    # Làm sạch văn bản
    df['Nhom_SP_Clean'] = df['Nhom_SP'].fillna('').astype(str).str.strip()
    df['Quy_Cach_Clean'] = df['Quy_Cach'].fillna('').astype(str).str.strip()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()

    # Định dạng Ngày hiển thị
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')

    # Tính toán Nhập kho / Tồn kho (Dùng numpy/vectorization tối ưu tốc độ)
    df['Da_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].notna()
    df['SL_Nhap_Kho'] = df['So_Luong_Tong_DH'].where(df['Da_Nhap_Kho'], 0.0)
    df['SL_Ton_Kho'] = df['So_Luong_Tong_DH'] - df['SL_Nhap_Kho']

    # Phân loại Tháng/Quý
    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month.fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter.fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)

    return df

# -----------------------------------------------------------------------------
# 3. GIAO DIỆN CHÍNH & BỘ LỌC
# -----------------------------------------------------------------------------
try:
    df = load_data()

    # Bộ lọc Thời gian & Bộ phận
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        raw_nams = [str(x) for x in df['Nam_Dat_Hang'].unique() if str(x) not in ['', 'nan', 'None', 'Khác']]
        nam_list = ['Tất cả các năm'] + sorted(raw_nams)
        default_year_idx = nam_list.index('2026') if '2026' in nam_list else 0
        nam_sel = st.selectbox("📅 Chọn Năm (Cột D)", nam_list, index=default_year_idx)

    with col_f2:
        ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Cả Năm", "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm"])

    with col_f3:
        if ky_sel == "Theo Tháng":
            thang_sel = st.selectbox("Tháng", list(range(1, 13)), index=0)
        elif ky_sel == "Theo Quý":
            quy_sel = st.selectbox("Quý", [1, 2, 3, 4], index=0)
        else:
            st.empty()

    with col_f4:
        raw_bps = [str(x) for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'None']]
        bp_list = ['Tất cả bộ phận'] + sorted(raw_bps)
        bp_sel = st.selectbox("🏢 Bộ Phận KD", bp_list)

    # Thực thi lọc dữ liệu
    df_filtered = df.copy()

    if nam_sel != 'Tất cả các năm':
        df_filtered = df_filtered[df_filtered['Nam_Dat_Hang'] == nam_sel]

    if ky_sel == "Theo Tháng":
        df_filtered = df_filtered[df_filtered['Thang_Chot'] == thang_sel]
    elif ky_sel == "Theo Quý":
        df_filtered = df_filtered[df_filtered['Quy_Chot'] == quy_sel]
    elif ky_sel == "6 Tháng Đầu Năm":
        df_filtered = df_filtered[df_filtered['Thang_Chot'].isin([1, 2, 3, 4, 5, 6])]
    elif ky_sel == "6 Tháng Cuối Năm":
        df_filtered = df_filtered[df_filtered['Thang_Chot'].isin([7, 8, 9, 10, 11, 12])]

    if bp_sel != 'Tất cả bộ phận':
        df_filtered = df_filtered[df_filtered['Bo_Phan_KD'] == bp_sel]

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4. DANH SÁCH TAB & PHÂN LOẠI SẢN PHẨM
    # -------------------------------------------------------------------------
    nhom_sp_list = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Hệ Cột + Phụ Kiện', '📋 Nhóm Khác']
    tabs = st.tabs(nhom_sp_list)

    # Regex khớp chính xác các nhóm theo từ khóa Tiếng Việt
    kw_goi_chau = r'Gối|Chậu'
    kw_khe_luoc = r'Khe|Lược'
    kw_tam_vco  = r'Tấm|VCO'
    kw_cot_pk   = r'Cột|Phụ Kiện'
    kw_loai_tru = r'Gối|Chậu|Khe|Lược|Tấm|VCO|Cột|Phụ Kiện'

    cols_show = [
        'So_DH', 'Nhom_SP', 'Trang_Thai_SX', 'Du_An', 'Quy_Cach', 'So_Luong_Tong_DH', 'DVT',
        'SL_Nhap_Kho', 'SL_Ton_Kho', 'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
    ]

    for i, tab_name in enumerate(nhom_sp_list):
        with tabs[i]:
            # Lọc theo Tab tương ứng
            if tab_name == '📊 Dashboard Tổng':
                df_tab = df_filtered.copy()
            elif tab_name == '📦 Gối Chậu':
                df_tab = df_filtered[df_filtered['Nhom_SP_Clean'].str.contains(kw_goi_chau, case=False, na=False)]
            elif tab_name == '⚙️ Khe Răng Lược':
                df_tab = df_filtered[df_filtered['Nhom_SP_Clean'].str.contains(kw_khe_luoc, case=False, na=False)]
            elif tab_name == '🧱 Tấm VCO':
                df_tab = df_filtered[df_filtered['Nhom_SP_Clean'].str.contains(kw_tam_vco, case=False, na=False)]
            elif tab_name == '🏗️ Hệ Cột + Phụ Kiện':
                df_tab = df_filtered[df_filtered['Nhom_SP_Clean'].str.contains(kw_cot_pk, case=False, na=False)]
            else:
                df_tab = df_filtered[~df_filtered['Nhom_SP_Clean'].str.contains(kw_loai_tru, case=False, na=False)]

            # 5. HIỂN THỊ METRIC TỔNG SỐ LƯỢNG
            total_so_luong = df_tab['So_Luong_Tong_DH'].sum()
            total_nhap_kho = df_tab['SL_Nhap_Kho'].sum()
            total_ton_kho  = df_tab['SL_Ton_Kho'].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Dòng / Đơn", f"{len(df_tab):,} Dòng")
            m2.metric("📦 Số lượng tổng ĐH", f"{total_so_luong:,.0f}")
            m3.metric("✅ Đã Nhập Kho", f"{total_nhap_kho:,.0f}")
            m4.metric("⏳ Tồn Cần Sản Xuất", f"{total_ton_kho:,.0f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # 6. Ô TÌM KIẾM THEO TAB
            search_kw = st.text_input(f"🔍 Tìm kiếm nhanh trong [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                search_kw = search_kw.strip()
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            # 7. BẢNG HIỂN THỊ CHI TIẾT
            st.dataframe(
                df_tab[cols_show],
                column_config={
                    "So_DH": st.column_config.TextColumn("Mã ĐH"),
                    "Nhom_SP": st.column_config.TextColumn("Nhóm SP (Cột M)"),
                    "Trang_Thai_SX": st.column_config.TextColumn("Trạng Thái (Cột C)"),
                    "Du_An": st.column_config.TextColumn("Dự Án"),
                    "Quy_Cach": st.column_config.TextColumn("Quy Cách Chủng Loại"),
                    "So_Luong_Tong_DH": st.column_config.NumberColumn("Số lượng tổng ĐH", format="%,.0f"),
                    "DVT": st.column_config.TextColumn("ĐVT"),
                    "SL_Nhap_Kho": st.column_config.NumberColumn("Đã Nhập Kho", format="%,.0f"),
                    "SL_Ton_Kho": st.column_config.NumberColumn("Còn Tồn", format="%,.0f"),
                    "Ngay_Duyet_DH": st.column_config.TextColumn("1. Duyệt ĐH (AB)"),
                    "Ngay_YCGH": st.column_config.TextColumn("2. YCGH (AC)"),
                    "Ngay_Chot_Cuoi": st.column_config.TextColumn("3. Chốt Cuối (AG)"),
                    "Ngay_Nhap_Kho": st.column_config.TextColumn("4. Nhập Kho (AH)")
                },
                use_container_width=True,
                hide_index=True,
                height=450
            )

except Exception as e:
    st.error(f"❌ **Đã xảy ra lỗi trong quá trình xử lý dữ liệu:** {e}")
