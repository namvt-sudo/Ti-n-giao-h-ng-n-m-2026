import streamlit as st
import pandas as pd

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stMetric { background-color: #f8f9fa; padding: 12px; border-radius: 10px; border: 1px solid #e9ecef; }
    div[data-baseweb="tab-list"] { gap: 8px; }
    button[data-baseweb="tab"] {
        border-radius: 20px !important;
        padding: 8px 16px !important;
        background-color: #f1f3f5 !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        background-color: #0d6efd !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# TIÊU ĐỀ VÀ NÚT CẬP NHẬT
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.title("🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG NĂM 2026")
with col_btn:
    st.write("")
    if st.button("🔄 Cập nhật dữ liệu mới nhất", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 2. HÀM ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238" # Tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

# 🟢 HÀM XỬ LÝ SỐ ĐÃ SỬA LỖI HIỂN THỊ HÀNG NGHÌN (2.140 -> 2140)
def clean_number(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip().replace('\xa0', '').replace(' ', '')
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
    
    # Nếu có dấu chấm và không có dấu phẩy (dạng phân cách hàng nghìn 2.140)
    if '.' in val_str and ',' not in val_str:
        val_str = val_str.replace('.', '')
    # Nếu dùng dấu phẩy làm thập phân hoặc ngăn cách
    elif ',' in val_str:
        val_str = val_str.replace('.', '').replace(',', '.')

    try:
        return float(val_str)
    except:
        return 0.0

@st.cache_data(ttl=5)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

    # Khởi tạo DataFrame từ dữ liệu raw
    df = pd.DataFrame()
    df['So_DH'] = df_raw.iloc[3:, 1].replace('', None).ffill()          # Col B (Index 1)
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].fillna('Chưa SX')          # Col C (Index 2)
    df['Nam_DatHang_Raw'] = df_raw.iloc[3:, 3].fillna('2026')           # Col D (Index 3)
    df['Bo_Phan_KD'] = df_raw.iloc[3:, 4].fillna('Chưa phân loại')      # Col E (Index 4)
    df['NV_KD'] = df_raw.iloc[3:, 6].fillna('Chưa phân loại')          # Col G (Index 6)
    df['Du_An'] = df_raw.iloc[3:, 7].fillna('')                         # Col H (Index 7)
    df['Quy_Cach'] = df_raw.iloc[3:, 9].fillna('')                      # Col J (Index 9)
    df['DVT'] = df_raw.iloc[3:, 10].fillna('cái')                        # Col K (Index 10)
    df['Nhom_SP'] = df_raw.iloc[3:, 12].fillna('')                      # Col M (Index 12)
    df['So_Luong_Tong_DH_Raw'] = df_raw.iloc[3:, 13]                    # Col N (Index 13)

    # LẤY ĐÚNG CÁC CỘT SẢN PHẨM THEO FILE EXCEL
    df['SL_KheRangLuoc'] = df_raw.iloc[3:, 14].apply(clean_number)     # Col O (Index 14) - KHE RĂNG LƯỢC
    df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)         # Col P (Index 15) - GỐI CHẬU
    df['SL_TamVCO'] = df_raw.iloc[3:, 23].apply(clean_number)          # Col X (Index 23) - TẤM VCO
    df['SL_HeCotPhuKien'] = df_raw.iloc[3:, 24].apply(clean_number)    # Col Y (Index 24) - HỆ CỘT + PHỤ KIỆN VCO

    # Các cột sản phẩm phụ (Sản phẩm khác)
    df['SL_KheRangLuocNhom'] = df_raw.iloc[3:, 16].apply(clean_number) # Col Q (Index 16)
    df['SL_LoXoNeo'] = df_raw.iloc[3:, 17].apply(clean_number)         # Col R (Index 17)
    df['SL_ThanhNeo'] = df_raw.iloc[3:, 18].apply(clean_number)        # Col S (Index 18)
    df['SL_SPKhac'] = df_raw.iloc[3:, 19].apply(clean_number)          # Col T (Index 19)
    df['SL_TamDeNeo'] = df_raw.iloc[3:, 20].apply(clean_number)        # Col U (Index 20)
    df['SL_StelPin'] = df_raw.iloc[3:, 21].apply(clean_number)         # Col V (Index 21)
    df['SL_VanKhuon'] = df_raw.iloc[3:, 22].apply(clean_number)        # Col W (Index 22)
    df['SL_LanCan'] = df_raw.iloc[3:, 25].apply(clean_number)          # Col Z (Index 25)

    # MỐC THỜI GIAN: ĐÃ CẬP NHẬT CỘT AA (INDEX 26) LÀM NGÀY ĐẶT HÀNG
    df['Ngay_GuiDH_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')   # Col AA (Index 26)
    df['Ngay_Duyet_DT'] = pd.to_datetime(df_raw.iloc[3:, 27], dayfirst=True, errors='coerce')   # Col AB (Index 27)
    df['Ngay_Chot_DT'] = pd.to_datetime(df_raw.iloc[3:, 32], dayfirst=True, errors='coerce')    # Col AG (Index 32)
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce') # Col AH (Index 33)

    # Lọc bỏ các dòng tiêu đề rác
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

    # Tính toán tổng sản lượng
    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number)
    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom'] + df['SL_LoXoNeo'] + df['SL_ThanhNeo'] +
        df['SL_SPKhac'] + df['SL_TamDeNeo'] + df['SL_StelPin'] +
        df['SL_VanKhuon'] + df['SL_LanCan']
    )
    df['SL_TongCalculated'] = df['SL_KheRangLuoc'] + df['SL_GoiChau'] + df['SL_TamVCO'] + df['SL_HeCotPhuKien'] + df['SL_NhomKhac']
    df.loc[df['So_Luong_Tong_DH'] <= 0, 'So_Luong_Tong_DH'] = df.loc[df['So_Luong_Tong_DH'] <= 0, 'SL_TongCalculated']

    # Chuẩn hóa Thời gian Đặt hàng (Ưu tiên Col AA -> AG -> AB)
    df['Ngay_DatHang_DT'] = df['Ngay_GuiDH_DT'].fillna(df['Ngay_Chot_DT']).fillna(df['Ngay_Duyet_DT'])
    df['Nam_DatHang'] = df['Ngay_DatHang_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_DatHang'] = df['Nam_DatHang'].replace('nan', None).fillna(df['Nam_DatHang_Raw']).fillna('2026')
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month
    df['Quy_DatHang'] = df['Ngay_DatHang_DT'].dt.quarter

    df['Da_Nhap_Kho'] = df['Trang_Thai_SX'].astype(str).str.strip().str.lower() == 'done'
    df['Nam_NhapKho'] = df['Ngay_NhapKho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Thang_NhapKho'] = df['Ngay_NhapKho_DT'].dt.month
    df['Quy_NhapKho'] = df['Ngay_NhapKho_DT'].dt.quarter

    return df

try:
    df = load_data()

    # 3. KHU VỰC BỘ LỌC 5 CỘT
    st.subheader("🎯 Bộ Lọc Báo Cáo Tiến Độ")
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        nam_list = ['Tất cả các năm'] + sorted([x for x in df['Nam_DatHang'].unique() if str(x) not in ['', 'nan', 'None']])
        nam_sel = st.selectbox("📅 Chọn Năm", nam_list, index=nam_list.index('2026') if '2026' in nam_list else 0)

    with f2:
        ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Cả Năm", "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm"])

    with f3:
        thang_sel, quy_sel = None, None
        if ky_sel == "Theo Tháng":
            thang_sel = st.selectbox("Tháng", list(range(1, 13)), index=8) # Mặc định Tháng 9
        elif ky_sel == "Theo Quý":
            quy_sel = st.selectbox("Quý", [1, 2, 3, 4], index=2) # Mặc định Quý 3
        else:
            st.write("")

    with f4:
        tt_list = ['Tất cả tình trạng'] + sorted(list(df['Trang_Thai_SX'].astype(str).str.strip().unique()))
        tt_sel = st.selectbox("🏭 Tình Trạng SX", tt_list)

    with f5:
        bp_list = ['Tất cả bộ phận'] + sorted([x for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan']])
        bp_sel = st.selectbox("🏢 Bộ Phận KD", bp_list)

    # Bộ lọc Nhân viên KD
    col_nv, _ = st.columns([2, 3])
    with col_nv:
        df_nv_scope = df if bp_sel == 'Tất cả bộ phận' else df[df['Bo_Phan_KD'] == bp_sel]
        nv_list = ['Tất cả NVKD'] + sorted([x for x in df_nv_scope['NV_KD'].unique() if str(x) not in ['', 'nan']])
        nv_sel = st.selectbox("👤 Nhân Viên KD", nv_list)

    # 4. LỌC ĐẶT HÀNG VÀ NHẬP KHO
    df_dh = df.copy()
    if nam_sel != 'Tất cả các năm':
        df_dh = df_dh[df_dh['Nam_DatHang'] == nam_sel]
    if ky_sel == "Theo Tháng" and thang_sel:
        df_dh = df_dh[df_dh['Thang_DatHang'] == thang_sel]
    elif ky_sel == "Theo Quý" and quy_sel:
        df_dh = df_dh[df_dh['Quy_DatHang'] == quy_sel]
    elif ky_sel == "6 Tháng Đầu Năm":
        df_dh = df_dh[df_dh['Thang_DatHang'].isin([1, 2, 3, 4, 5, 6])]
    elif ky_sel == "6 Tháng Cuối Năm":
        df_dh = df_dh[df_dh['Thang_DatHang'].isin([7, 8, 9, 10, 11, 12])]

    if tt_sel != 'Tất cả tình trạng':
        df_dh = df_dh[df_dh['Trang_Thai_SX'].astype(str).str.strip() == tt_sel]
    if bp_sel != 'Tất cả bộ phận':
        df_dh = df_dh[df_dh['Bo_Phan_KD'] == bp_sel]
    if nv_sel != 'Tất cả NVKD':
        df_dh = df_dh[df_dh['NV_KD'] == nv_sel]

    df_nk = df[df['Da_Nhap_Kho']].copy()
    if nam_sel != 'Tất cả các năm':
        df_nk = df_nk[df_nk['Nam_NhapKho'] == nam_sel]
    if ky_sel == "Theo Tháng" and thang_sel:
        df_nk = df_nk[df_nk['Thang_NhapKho'] == thang_sel]
    elif ky_sel == "Theo Quý" and quy_sel:
        df_nk = df_nk[df_nk['Quy_NhapKho'] == quy_sel]
    elif ky_sel == "6 Tháng Đầu Năm":
        df_nk = df_nk[df_nk['Thang_NhapKho'].isin([1, 2, 3, 4, 5, 6])]
    elif ky_sel == "6 Tháng Cuối Năm":
        df_nk = df_nk[df_nk['Thang_NhapKho'].isin([7, 8, 9, 10, 11, 12])]

    if tt_sel != 'Tất cả tình trạng':
        df_nk = df_nk[df_nk['Trang_Thai_SX'].astype(str).str.strip() == tt_sel]
    if bp_sel != 'Tất cả bộ phận':
        df_nk = df_nk[df_nk['Bo_Phan_KD'] == bp_sel]
    if nv_sel != 'Tất cả NVKD':
        df_nk = df_nk[df_nk['NV_KD'] == nv_sel]

    st.markdown("---")

    # 5. HIỂN THỊ DẠNG TAB SẢN PHẨM
    tab_names = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Cột H (Phụ Kiện)', '📋 Sản Phẩm Khác']
    tabs = st.tabs(tab_names)

    qty_mapping = {
        '📦 Gối Chậu': 'SL_GoiChau',
        '⚙️ Khe Răng Lược': 'SL_KheRangLuoc',
        '🧱 Tấm VCO': 'SL_TamVCO',
        '🏗️ Cột H (Phụ Kiện)': 'SL_HeCotPhuKien',
        '📋 Sản Phẩm Khác': 'SL_NhomKhac'
    }

    cols_display = ['So_DH', 'Trang_Thai_SX', 'Bo_Phan_KD', 'NV_KD', 'Du_An', 'Quy_Cach', 'DVT']

    for i, tname in enumerate(tab_names):
        with tabs[i]:
            if tname == '📊 Dashboard Tổng':
                df_dh_tab = df_dh.copy()
                df_nk_tab = df_nk.copy()
                q_col = 'So_Luong_Tong_DH'
            else:
                q_col = qty_mapping[tname]
                df_dh_tab = df_dh[df_dh[q_col] > 0].copy()
                df_nk_tab = df_nk[df_nk[q_col] > 0].copy()

            sum_dh = df_dh_tab[q_col].sum()
            sum_nk = df_nk_tab[q_col].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Số Đơn Đặt Hàng", f"{len(df_dh_tab)} Đơn")
            m2.metric("📦 Tổng SL Đặt Hàng", f"{sum_dh:,.2f}")
            m3.metric("✅ Tổng SL Nhập Kho", f"{sum_nk:,.2f}")
            m4.metric("⏳ Chênh Lệch Đặt - Nhập", f"{(sum_dh - sum_nk):,.2f}")

            st.markdown("<br>", unsafe_allow_html=True)
            search_kw = st.text_input(f"🔍 Tìm kiếm chi tiết trong [{tname}] (Mã ĐH, Dự án, Quy cách, Tấm đế neo...):", key=f"s_{i}")

            if search_kw:
                df_dh_tab = df_dh_tab[
                    df_dh_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_dh_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_dh_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_dh_tab['Nhom_SP'].astype(str).str.contains(search_kw, case=False, na=False)
                ]
                df_nk_tab = df_nk_tab[
                    df_nk_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_nk_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_nk_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_nk_tab['Nhom_SP'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            sub_tab1, sub_tab2 = st.tabs(["📋 Đơn Đặt Hàng Phụ Trách", "🏭 Đợt Nhập Kho Thực Tế"])

            with sub_tab1:
                st.caption(f"Danh sách các đơn đặt hàng chốt/duyệt theo bộ lọc ({len(df_dh_tab)} dòng):")
                st.dataframe(
                    df_dh_tab[cols_display + [q_col]],
                    column_config={
                        "So_DH": "Mã ĐH", "Trang_Thai_SX": "Trạng Thái", "Bo_Phan_KD": "Bộ Phận",
                        "NV_KD": "NVKD", "Du_An": "Dự Án", "Quy_Cach": "Quy Cách Chủng Loại", "DVT": "ĐVT",
                        q_col: st.column_config.NumberColumn("Số Lượng Đặt", format="%.2f")
                    },
                    use_container_width=True, hide_index=True
                )

            with sub_tab2:
                st.caption(f"Danh sách các đợt thực tế hoàn thành nhập kho theo bộ lọc ({len(df_nk_tab)} dòng):")
                st.dataframe(
                    df_nk_tab[cols_display + [q_col]],
                    column_config={
                        "So_DH": "Mã ĐH", "Trang_Thai_SX": "Trạng Thái", "Bo_Phan_KD": "Bộ Phận",
                        "NV_KD": "NVKD", "Du_An": "Dự Án", "Quy_Cach": "Quy Cách Chủng Loại", "DVT": "ĐVT",
                        q_col: st.column_config.NumberColumn("Số Lượng Nhập Kho", format="%.2f")
                    },
                    use_container_width=True, hide_index=True
                )

except Exception as e:
    st.error(f"Lỗi kết nối hoặc xử lý dữ liệu từ Google Sheets: {e}")
