import streamlit as st
import pandas as pd
import re

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG WEB & TỐI ƯU CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng", 
    page_icon="🛡️",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
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
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

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

    # Đọc các cột ngày
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, 27], dayfirst=True, errors='coerce')    # AB
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, 28], dayfirst=True, errors='coerce')        # AC
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, 32], dayfirst=True, errors='coerce')   # AG
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, 33], dayfirst=True, errors='coerce')    # AH (Cột Nhập Kho JSC)

    # Tự động điền dữ liệu gộp ô (ffill)
    df['So_DH'] = df['So_DH_Raw'].replace('', None).ffill()
    df['Nam_Col_D'] = df['Nam_Dat_Hang_Raw'].replace('', None).ffill().astype(str).str.extract(r'(\d{4})')[0]

    # Loại bỏ dòng không hợp lệ
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|TỔNG|STT|Số ĐH', case=False, na=False)]

    # Chuẩn hóa Số lượng
    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number_exact)
    df = df[df['So_Luong_Tong_DH'] > 0]

    # Trích xuất Năm Đặt Hàng (Cột D / Ngày Duyệt / Ngày Chốt)
    df['Nam_Duyet'] = df['Ngay_Duyet_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Dat_Hang'] = df['Nam_Col_D'].fillna(df['Nam_Duyet']).fillna(df['Nam_Chot']).fillna('Khác')

    # Trích xuất Năm / Tháng / Quý Nhập Kho thực tế từ Cột AH
    df['Nam_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Thang_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.month
    df['Quy_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.quarter

    # Làm sạch văn bản & Ghép chuỗi tìm kiếm
    df['Nhom_SP_Clean'] = df['Nhom_SP'].fillna('').astype(str).str.strip()
    df['Quy_Cach_Clean'] = df['Quy_Cach'].fillna('').astype(str).str.strip()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()
    df['Full_Text_Search'] = df['Nhom_SP_Clean'] + ' ' + df['Quy_Cach_Clean']

    # Định dạng Ngày hiển thị
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')

    # Phân loại Tháng/Quý của Đặt Hàng
    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month.fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter.fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)

    return df

# -----------------------------------------------------------------------------
# 3. GIAO DIỆN CHÍNH & BỘ LỌC
# -----------------------------------------------------------------------------
try:
    df = load_data()

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

    # -------------------------------------------------------------------------
    # 4. LOGIC LỌC ĐẶC THỤ: TÁCH BIỆT ĐẶT HÀNG & NHẬP KHO CỘT AH
    # -------------------------------------------------------------------------
    df_filtered = df.copy()

    # Bộ lọc Bộ phận (Áp dụng chung)
    if bp_sel != 'Tất cả bộ phận':
        df_filtered = df_filtered[df_filtered['Bo_Phan_KD'] == bp_sel]

    # Điều kiện Lọc Đặt Hàng theo Năm & Kỳ
    cond_dh_nam = (df_filtered['Nam_Dat_Hang'] == nam_sel) if nam_sel != 'Tất cả các năm' else True

    # Điều kiện Lọc Nhập Kho theo Cột AH (Ngày thực tế nhập kho JSC)
    cond_nk_nam = (df_filtered['Nam_Nhap_Kho'] == nam_sel) if nam_sel != 'Tất cả các năm' else True

    if ky_sel == "Theo Tháng":
        cond_dh_ky = df_filtered['Thang_Chot'] == thang_sel
        cond_nk_ky = df_filtered['Thang_Nhap_Kho'] == thang_sel
    elif ky_sel == "Theo Quý":
        cond_dh_ky = df_filtered['Quy_Chot'] == quy_sel
        cond_nk_ky = df_filtered['Quy_Nhap_Kho'] == quy_sel
    elif ky_sel == "6 Tháng Đầu Năm":
        cond_dh_ky = df_filtered['Thang_Chot'].isin([1, 2, 3, 4, 5, 6])
        cond_nk_ky = df_filtered['Thang_Nhap_Kho'].isin([1, 2, 3, 4, 5, 6])
    elif ky_sel == "6 Tháng Cuối Năm":
        cond_dh_ky = df_filtered['Thang_Chot'].isin([7, 8, 9, 10, 11, 12])
        cond_nk_ky = df_filtered['Thang_Nhap_Kho'].isin([7, 8, 9, 10, 11, 12])
    else:
        cond_dh_ky = True
        cond_nk_ky = True

    # Tính toán chính xác hai chỉ số:
    # 1. Đặt hàng: Đơn thuộc năm/kỳ chọn
    df_filtered['Is_Dat_Hang_Thuoc_Ky'] = cond_dh_nam & cond_dh_ky
    
    # 2. Nhập kho: Có ngày nhập ở Cột AH VÀ Ngày đó thuộc năm/kỳ chọn
    df_filtered['Is_Nhap_Kho_Thuoc_Ky'] = df_filtered['Ngay_Nhap_Kho_DT'].notna() & cond_nk_nam & cond_nk_ky

    # Gán số lượng tương ứng
    df_filtered['SL_Dat_Hang_Kỳ'] = df_filtered['So_Luong_Tong_DH'].where(df_filtered['Is_Dat_Hang_Thuoc_Ky'], 0.0)
    df_filtered['SL_Nhap_Kho'] = df_filtered['So_Luong_Tong_DH'].where(df_filtered['Is_Nhap_Kho_Thuoc_Ky'], 0.0)
    df_filtered['SL_Ton_Kho'] = df_filtered['SL_Dat_Hang_Kỳ'] - df_filtered['SL_Nhap_Kho']

    # Chỉ giữ lại dòng có phát sinh Đặt hàng hoặc Nhập kho trong kỳ chọn
    df_display = df_filtered[df_filtered['Is_Dat_Hang_Thuoc_Ky'] | df_filtered['Is_Nhap_Kho_Thuoc_Ky']].copy()

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 5. HIỂN THỊ CÁC TAB SẢN PHẨM
    # -------------------------------------------------------------------------
    nhom_sp_list = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Hệ Cột + Phụ Kiện', '📋 Nhóm Khác']
    tabs = st.tabs(nhom_sp_list)

    kw_goi_chau = r'Gối|Goi|Chậu|Chau|Bearing|Pot|Pots|Gối cao su|Gối cầu|Gối chậu'
    kw_khe_luoc = r'Khe|Lược|Luoc|Expansion|Co giãn'
    kw_tam_vco  = r'Tấm|Tam|VCO'
    kw_cot_pk   = r'Cột|Cot|Phụ Kiện|Phu Kien|Thiết bị'
    kw_loai_tru = f"({kw_goi_chau})|({kw_khe_luoc})|({kw_tam_vco})|({kw_cot_pk})"

    cols_show = [
        'So_DH', 'Nhom_SP', 'Trang_Thai_SX', 'Du_An', 'Quy_Cach', 'SL_Dat_Hang_Kỳ', 'DVT',
        'SL_Nhap_Kho', 'SL_Ton_Kho', 'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
    ]

    for i, tab_name in enumerate(nhom_sp_list):
        with tabs[i]:
            if tab_name == '📊 Dashboard Tổng':
                df_tab = df_display.copy()
            elif tab_name == '📦 Gối Chậu':
                df_tab = df_display[df_display['Full_Text_Search'].str.contains(kw_goi_chau, case=False, na=False)]
            elif tab_name == '⚙️ Khe Răng Lược':
                df_tab = df_display[df_display['Full_Text_Search'].str.contains(kw_khe_luoc, case=False, na=False)]
            elif tab_name == '🧱 Tấm VCO':
                df_tab = df_display[df_display['Full_Text_Search'].str.contains(kw_tam_vco, case=False, na=False)]
            elif tab_name == '🏗️ Hệ Cột + Phụ Kiện':
                df_tab = df_display[df_display['Full_Text_Search'].str.contains(kw_cot_pk, case=False, na=False)]
            else:
                df_tab = df_display[~df_display['Full_Text_Search'].str.contains(kw_loai_tru, case=False, na=False)]

            # METRIC TÍNH TOÁN
            total_so_luong = df_tab['SL_Dat_Hang_Kỳ'].sum()
            total_nhap_kho = df_tab['SL_Nhap_Kho'].sum()
            total_ton_kho  = df_tab['SL_Ton_Kho'].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Dòng / Đơn", f"{len(df_tab):,} Dòng")
            m2.metric("📦 Số lượng Đặt Hàng (Theo Kỳ)", f"{total_so_luong:,.0f}")
            m3.metric("✅ Thực Tế Nhập Kho (Cột AH)", f"{total_nhap_kho:,.0f}")
            m4.metric("⏳ Tồn Cần Sản Xuất", f"{total_ton_kho:,.0f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # SEARCH
            search_kw = st.text_input(f"🔍 Tìm kiếm nhanh trong [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                search_kw = search_kw.strip()
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            # BẢNG DỮ LIỆU
            st.dataframe(
                df_tab[cols_show],
                column_config={
                    "So_DH": st.column_config.TextColumn("Mã ĐH"),
                    "Nhom_SP": st.column_config.TextColumn("Nhóm SP (Cột M)"),
                    "Trang_Thai_SX": st.column_config.TextColumn("Trạng Thái (Cột C)"),
                    "Du_An": st.column_config.TextColumn("Dự Án"),
                    "Quy_Cach": st.column_config.TextColumn("Quy Cách Chủng Loại"),
                    "SL_Dat_Hang_Kỳ": st.column_config.NumberColumn("SL Đặt Hàng Kỳ Chọn", format="%,.0f"),
                    "DVT": st.column_config.TextColumn("ĐVT"),
                    "SL_Nhap_Kho": st.column_config.NumberColumn("Đã Nhập Kho (Cột AH)", format="%,.0f"),
                    "SL_Ton_Kho": st.column_config.NumberColumn("Còn Tồn Kỳ Chọn", format="%,.0f"),
                    "Ngay_Duyet_DH": st.column_config.TextColumn("1. Duyệt ĐH (AB)"),
                    "Ngay_YCGH": st.column_config.TextColumn("2. YCGH (AC)"),
                    "Ngay_Chot_Cuoi": st.column_config.TextColumn("3. Chốt Cuối (AG)"),
                    "Ngay_Nhap_Kho": st.column_config.TextColumn("4. Thực Tế Nhập Kho (AH)")
                },
                use_container_width=True,
                hide_index=True,
                height=450
            )

except Exception as e:
    st.error(f"❌ **Đã xảy ra lỗi trong quá trình xử lý dữ liệu:** {e}")
