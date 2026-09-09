import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG WEB
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng", 
    page_icon="🛡️",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG")

# -----------------------------------------------------------------------------
# 2. HÀM LÀM SẠCH SỐ LƯỢNG CHUẨN XÁC
# -----------------------------------------------------------------------------
def clean_number_exact(val):
    if pd.isna(val) or val is None:
        return 0.0
    
    val_str = str(val).replace('\xa0', '').replace(' ', '').strip()
    
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0

    if ',' in val_str and '.' in val_str:
        if val_str.rfind(',') > val_str.rfind('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')

    try:
        return float(val_str)
    except ValueError:
        return 0.0

# -----------------------------------------------------------------------------
# 3. TẢI DỮ LIỆU TỪ GOOGLE SHEETS
# -----------------------------------------------------------------------------
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"  # Tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=10, show_spinner="Đang đọc dữ liệu mới nhất...")
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

    # Các cột ngày
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, 27], dayfirst=True, errors='coerce')    # AB
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, 28], dayfirst=True, errors='coerce')        # AC
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, 32], dayfirst=True, errors='coerce')   # AG
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, 33], dayfirst=True, errors='coerce')    # AH (Thực tế nhập kho JSC)

    # Điền ô gộp
    df['So_DH'] = df['So_DH_Raw'].replace('', None).ffill()
    df['Nam_Col_D'] = df['Nam_Dat_Hang_Raw'].replace('', None).ffill().astype(str).str.extract(r'(\d{4})')[0]

    # Loại bỏ hàng rác
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|TỔNG|STT|Số ĐH', case=False, na=False)]

    # Số lượng
    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number_exact)
    df = df[df['So_Luong_Tong_DH'] > 0]

    # TRÍCH XUẤT THỜI GIAN ĐẶT HÀNG
    df['Nam_Duyet'] = df['Ngay_Duyet_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Dat_Hang'] = df['Nam_Col_D'].fillna(df['Nam_Chot']).fillna(df['Nam_Duyet']).fillna('Khác')

    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month.fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter.fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)

    # TRÍCH XUẤT THỜI GIAN NHẬP KHO THỰC TẾ
    df['Nam_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Thang_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.month
    df['Quy_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.quarter

    # Làm sạch văn bản
    df['Nhom_SP_Clean'] = df['Nhom_SP'].fillna('').astype(str).str.strip().str.upper()
    df['Quy_Cach_Clean'] = df['Quy_Cach'].fillna('').astype(str).str.strip().str.upper()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()

    df['Full_Info'] = df['Nhom_SP_Clean'] + ' ' + df['Quy_Cach_Clean']

    # Formatting ngày hiển thị
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')

    return df

# -----------------------------------------------------------------------------
# 4. CHUẨN HÓA PHÂN LOẠI TAB (SỬA LỖI LÂN LỘN CỘT / GỐI CHẬU)
# -----------------------------------------------------------------------------
def classify_tab(row):
    info = row['Full_Info']
    nhom = row['Nhom_SP_Clean']

    # Ưu tiên 1: Hệ Cột + Phụ Kiện (Phải lọc trước để tránh từ "THÉP" đè sang Gối)
    kw_cot = ['CỘT', 'LAN CAN', 'PHỤ KIỆN', 'THIẾT BỊ', 'XÀ', 'ĐẾ']
    if any(k in nhom for k in ['CỘT', 'LAN CAN', 'PHỤ KIỆN']) or any(k in info for k in kw_cot):
        return '🏗️ Hệ Cột + Phụ Kiện'

    # Ưu tiên 2: Khe Răng Lược / Khe Co Giãn
    kw_khe = ['KHE', 'LƯỢC', 'EXPANSION', 'CO GIÃN']
    if any(k in nhom for k in kw_khe) or any(k in info for k in kw_khe):
        return '⚙️ Khe Răng Lược'

    # Ưu tiên 3: Tấm VCO / Tấm Chống Ồn
    kw_tam = ['VCO', 'CHỐNG ỒN', 'GIẢM ÂM', 'TẤM']
    if any(k in nhom for k in kw_tam) or any(k in info for k in kw_tam):
        return '🧱 Tấm VCO'

    # Ưu tiên 4: Gối Chậu (Loại bỏ các từ khóa quá rộng như "THÉP", "CẦU")
    kw_goi_chau = ['GỐI', 'CHẬU', 'BEARING', 'POT', 'ELASTOMERIC', 'GIAO THOA']
    if any(k in nhom for k in kw_goi_chau) or any(k in info for k in kw_goi_chau):
        return '📦 Gối Chậu'

    return '📋 Nhóm Khác'

# -----------------------------------------------------------------------------
# 5. GIAO DIỆN VÀ TÍNH TOÁN
# -----------------------------------------------------------------------------
try:
    df = load_data()
    df['Tab_Category'] = df.apply(classify_tab, axis=1)

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        raw_nams = [str(x) for x in df['Nam_Dat_Hang'].unique() if str(x) not in ['', 'nan', 'None', 'Khác']]
        nam_list = ['Tất cả các năm'] + sorted(raw_nams)
        default_year_idx = nam_list.index('2026') if '2026' in nam_list else 0
        nam_sel = st.selectbox("📅 Chọn Năm", nam_list, index=default_year_idx)

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
    # TÍNH TOÁN LOGIC LỌC DỮ LIỆU
    # -------------------------------------------------------------------------
    df_filtered = df.copy()

    if bp_sel != 'Tất cả bộ phận':
        df_filtered = df_filtered[df_filtered['Bo_Phan_KD'] == bp_sel]

    # Điều kiện lọc theo Thời gian
    if nam_sel != 'Tất cả các năm':
        cond_nam = (df_filtered['Nam_Dat_Hang'] == nam_sel)
    else:
        cond_nam = True

    if ky_sel == "Theo Tháng":
        cond_ky = df_filtered['Thang_Chot'] == thang_sel
    elif ky_sel == "Theo Quý":
        cond_ky = df_filtered['Quy_Chot'] == quy_sel
    elif ky_sel == "6 Tháng Đầu Năm":
        cond_ky = df_filtered['Thang_Chot'].isin([1, 2, 3, 4, 5, 6])
    elif ky_sel == "6 Tháng Cuối Năm":
        cond_ky = df_filtered['Thang_Chot'].isin([7, 8, 9, 10, 11, 12])
    else:
        cond_ky = True

    # Giữ nguyên toàn bộ dòng thuộc kỳ Đặt hàng được chọn
    df_display = df_filtered[cond_nam & cond_ky].copy()

    # Tính toán chính xác Số lượng Nhập kho và Tồn kho lũy kế theo từng Đơn hàng
    df_display['SL_Dat_Hang_Display'] = df_display['So_Luong_Tong_DH']
    df_display['SL_Nhap_Kho_Display'] = df_display.apply(
        lambda r: r['So_Luong_Tong_DH'] if pd.notna(r['Ngay_Nhap_Kho_DT']) else 0.0, axis=1
    )
    df_display['SL_Ton_Kho_Display'] = df_display['SL_Dat_Hang_Display'] - df_display['SL_Nhap_Kho_Display']

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TAB HIỂN THỊ
    # -------------------------------------------------------------------------
    nhom_sp_list = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Hệ Cột + Phụ Kiện', '📋 Nhóm Khác']
    tabs = st.tabs(nhom_sp_list)

    cols_show = [
        'So_DH', 'Nhom_SP', 'Trang_Thai_SX', 'Du_An', 'Quy_Cach', 'SL_Dat_Hang_Display', 'DVT',
        'SL_Nhap_Kho_Display', 'SL_Ton_Kho_Display', 'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
    ]

    for i, tab_name in enumerate(nhom_sp_list):
        with tabs[i]:
            if tab_name == '📊 Dashboard Tổng':
                df_tab = df_display.copy()
            else:
                df_tab = df_display[df_display['Tab_Category'] == tab_name]

            total_dat_hang = df_tab['SL_Dat_Hang_Display'].sum()
            total_nhap_kho = df_tab['SL_Nhap_Kho_Display'].sum()
            total_ton_kho  = df_tab['SL_Ton_Kho_Display'].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Dòng / Đơn", f"{len(df_tab):,} Dòng")
            m2.metric("📦 SL Đặt Hàng", f"{total_dat_hang:,.2f}".rstrip('0').rstrip('.'))
            m3.metric("✅ SL Nhập Kho (Cột AH)", f"{total_nhap_kho:,.2f}".rstrip('0').rstrip('.'))
            m4.metric("⏳ Tồn Cần Sản Xuất", f"{total_ton_kho:,.2f}".rstrip('0').rstrip('.'))

            st.markdown("<br>", unsafe_allow_html=True)

            search_kw = st.text_input(f"🔍 Tìm kiếm nhanh trong [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                search_kw = search_kw.strip()
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            st.dataframe(
                df_tab[cols_show],
                column_config={
                    "So_DH": st.column_config.TextColumn("Mã ĐH"),
                    "Nhom_SP": st.column_config.TextColumn("Nhóm SP (Cột M)"),
                    "Trang_Thai_SX": st.column_config.TextColumn("Trạng Thái (Cột C)"),
                    "Du_An": st.column_config.TextColumn("Dự Án"),
                    "Quy_Cach": st.column_config.TextColumn("Quy Cách Chủng Loại"),
                    "SL_Dat_Hang_Display": st.column_config.NumberColumn("SL Đặt Hàng Kỳ Chọn", format="%.2f"),
                    "DVT": st.column_config.TextColumn("ĐVT"),
                    "SL_Nhap_Kho_Display": st.column_config.NumberColumn("Đã Nhập Kho (Cột AH)", format="%.2f"),
                    "SL_Ton_Kho_Display": st.column_config.NumberColumn("Còn Tồn Kỳ Chọn", format="%.2f"),
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
