import streamlit as st
import pandas as pd
import re

# ==========================================================
# 1. CẤU HÌNH
# ==========================================================

st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
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

st.title("🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG")


# ==========================================================
# 2. GOOGLE SHEETS
# ==========================================================

GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"


def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"  # Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


# ==========================================================
# 3. ĐỌC SỐ
# ==========================================================

def clean_number_exact(val):

    if pd.isna(val) or val is None:
        return 0.0

    val_str = str(val).strip()

    if not val_str or val_str.lower() in [
        'nan', 'none', 'null', '-', ''
    ]:
        return 0.0

    # Xóa khoảng trắng
    val_str = val_str.replace('\xa0', '').replace(' ', '')

    has_comma = ',' in val_str
    has_dot = '.' in val_str

    # Có cả . và ,
    if has_comma and has_dot:

        # Dấu đứng cuối là dấu thập phân
        if val_str.rfind(',') > val_str.rfind('.'):

            # 1.234,56 -> 1234.56
            val_str = val_str.replace('.', '')
            val_str = val_str.replace(',', '.')

        else:

            # 1,234.56 -> 1234.56
            val_str = val_str.replace(',', '')

    # Chỉ có ,
    elif has_comma:

        parts = val_str.split(',')

        if len(parts) > 1 and len(parts[-1]) == 3:

            # 1,500 -> 1500
            val_str = val_str.replace(',', '')

        else:

            # 12,5 -> 12.5
            val_str = val_str.replace(',', '.')

    # Chỉ có .
    elif has_dot:

        parts = val_str.split('.')

        if len(parts) > 1 and len(parts[-1]) == 3:

            # 1.500 -> 1500
            val_str = val_str.replace('.', '')

    try:
        return float(val_str)

    except:
        return 0.0


# ==========================================================
# 4. LOAD DATA
# ==========================================================

@st.cache_data(ttl=10)
def load_data():

    csv_url = get_ggs_export_url(GGS_URL)

    # Đọc tất cả dưới dạng text
    df_raw = pd.read_csv(
        csv_url,
        header=None,
        dtype=str
    )

    # ------------------------------------------------------
    # DÒNG 5 TRỞ ĐI
    # ------------------------------------------------------

    df = pd.DataFrame({

        # B
        'So_DH_Raw':
            df_raw.iloc[4:, 1],

        # C
        'Trang_Thai_SX':
            df_raw.iloc[4:, 2],

        # D
        'Nam_Dat_Hang_Raw':
            df_raw.iloc[4:, 3],

        # E
        'Bo_Phan_KD':
            df_raw.iloc[4:, 4],

        # G
        'NV_KD':
            df_raw.iloc[4:, 6],

        # H
        'Du_An':
            df_raw.iloc[4:, 7],

        # J
        'Quy_Cach':
            df_raw.iloc[4:, 9],

        # K
        'DVT':
            df_raw.iloc[4:, 10],

        # M
        'Nhom_SP':
            df_raw.iloc[4:, 12],

        # N
        'So_Luong_Tong_DH_Raw':
            df_raw.iloc[4:, 13],

        # O - KHE RĂNG LƯỢC
        'KheRangLuoc_Raw':
            df_raw.iloc[4:, 14],

        # P - GỐI CHẬU
        'GoiChau_Raw':
            df_raw.iloc[4:, 15],

        # Q - KHE RĂNG LƯỢC NHÔM
        'KheRangLuocNhom_Raw':
            df_raw.iloc[4:, 16],

        # R - LÒ XO NEO
        'LoXoNeo_Raw':
            df_raw.iloc[4:, 17],

        # S - THANH NEO
        'ThanhNeo_Raw':
            df_raw.iloc[4:, 18],

        # T - SP KHÁC
        'SPKhac_Raw':
            df_raw.iloc[4:, 19],

        # U - TẤM ĐẾ NEO
        'TamDeNeo_Raw':
            df_raw.iloc[4:, 20],

        # V - STEL PIN
        'StelPin_Raw':
            df_raw.iloc[4:, 21],

        # W - VÁN KHUÔN
        'VanKhuon_Raw':
            df_raw.iloc[4:, 22],

        # X - TẤM VCO
        'TamVCO_Raw':
            df_raw.iloc[4:, 23],

        # Y - HỆ CỘT + PHỤ KIỆN
        'HeCotPhuKien_Raw':
            df_raw.iloc[4:, 24],

        # Z - LAN CAN
        'LanCan_Raw':
            df_raw.iloc[4:, 25],
    })

    # ------------------------------------------------------
    # NGÀY THÁNG
    # ------------------------------------------------------

    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 27],
        dayfirst=True,
        errors='coerce'
    )

    df['Ngay_YCGH_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 28],
        dayfirst=True,
        errors='coerce'
    )

    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 32],
        dayfirst=True,
        errors='coerce'
    )

    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 33],
        dayfirst=True,
        errors='coerce'
    )

    # ======================================================
    # 5. XỬ LÝ SỐ ĐH MERGE
    # ======================================================

    df['So_DH'] = (
        df['So_DH_Raw']
        .replace('', None)
        .ffill()
    )

    df['Nam_Col_D'] = (
        df['Nam_Dat_Hang_Raw']
        .replace('', None)
        .ffill()
        .astype(str)
        .str.extract(r'(\d{4})')[0]
    )

    # ------------------------------------------------------
    # BỎ DÒNG TIÊU ĐỀ / TỔNG
    # ------------------------------------------------------

    df = df[df['So_DH'].notna()]

    df = df[
        ~df['So_DH']
        .astype(str)
        .str.contains(
            'Tổng|Tong|TỔNG|STT|Số ĐH',
            case=False,
            na=False
        )
    ]

    # ======================================================
    # 6. CHUYỂN TOÀN BỘ CỘT SỐ LƯỢNG
    # ======================================================

    df['So_Luong_Tong_DH'] = (
        df['So_Luong_Tong_DH_Raw']
        .apply(clean_number_exact)
    )

    df['SL_KheRangLuoc'] = (
        df['KheRangLuoc_Raw']
        .apply(clean_number_exact)
    )

    df['SL_GoiChau'] = (
        df['GoiChau_Raw']
        .apply(clean_number_exact)
    )

    df['SL_KheRangLuocNhom'] = (
        df['KheRangLuocNhom_Raw']
        .apply(clean_number_exact)
    )

    df['SL_LoXoNeo'] = (
        df['LoXoNeo_Raw']
        .apply(clean_number_exact)
    )

    df['SL_ThanhNeo'] = (
        df['ThanhNeo_Raw']
        .apply(clean_number_exact)
    )

    df['SL_SPKhac'] = (
        df['SPKhac_Raw']
        .apply(clean_number_exact)
    )

    df['SL_TamDeNeo'] = (
        df['TamDeNeo_Raw']
        .apply(clean_number_exact)
    )

    df['SL_StelPin'] = (
        df['StelPin_Raw']
        .apply(clean_number_exact)
    )

    df['SL_VanKhuon'] = (
        df['VanKhuon_Raw']
        .apply(clean_number_exact)
    )

    df['SL_TamVCO'] = (
        df['TamVCO_Raw']
        .apply(clean_number_exact)
    )

    df['SL_HeCotPhuKien'] = (
        df['HeCotPhuKien_Raw']
        .apply(clean_number_exact)
    )

    df['SL_LanCan'] = (
        df['LanCan_Raw']
        .apply(clean_number_exact)
    )

    # ======================================================
    # 7. NHÓM KHÁC
    # ======================================================

    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom']
        + df['SL_LoXoNeo']
        + df['SL_ThanhNeo']
        + df['SL_SPKhac']
        + df['SL_TamDeNeo']
        + df['SL_StelPin']
        + df['SL_VanKhuon']
        + df['SL_LanCan']
    )

    # ======================================================
    # 8. TỔNG SỐ LƯỢNG CÁC LOẠI
    # ======================================================

    df['SL_TongCacNhom'] = (
        df['SL_KheRangLuoc']
        + df['SL_GoiChau']
        + df['SL_TamVCO']
        + df['SL_HeCotPhuKien']
        + df['SL_NhomKhac']
    )

    # ------------------------------------------------------
    # Chỉ giữ dòng có số lượng
    # ------------------------------------------------------

    df = df[
        (df['So_Luong_Tong_DH'] > 0)
        | (df['SL_TongCacNhom'] > 0)
    ]

    # ======================================================
    # 9. TRẠNG THÁI NHẬP KHO
    # ======================================================

    df['Trang_Thai_SX_Clean'] = (
        df['Trang_Thai_SX']
        .fillna('')
        .astype(str)
        .str.strip()
    )

    df['Da_Nhap_Kho'] = (
        df['Trang_Thai_SX_Clean']
        .str.lower()
        .eq('done')
    )

    # ======================================================
    # 10. QUAN TRỌNG:
    # NHẬP KHO PHẢI THEO TỪNG LOẠI
    # ======================================================

    # Không còn dùng:
    #
    # SL_Nhap_Kho = So_Luong_Tong_DH
    #
    # vì cách đó làm Gối Chậu/Khe Răng Lược/Tấm VCO...
    # bị lấy nhầm toàn bộ số lượng ĐH.

    # Từng loại có cột nhập kho riêng
    df['SL_NhapKho_KheRangLuoc'] = (
        df['SL_KheRangLuoc']
        .where(df['Da_Nhap_Kho'], 0)
    )

    df['SL_NhapKho_GoiChau'] = (
        df['SL_GoiChau']
        .where(df['Da_Nhap_Kho'], 0)
    )

    df['SL_NhapKho_TamVCO'] = (
        df['SL_TamVCO']
        .where(df['Da_Nhap_Kho'], 0)
    )

    df['SL_NhapKho_HeCotPhuKien'] = (
        df['SL_HeCotPhuKien']
        .where(df['Da_Nhap_Kho'], 0)
    )

    df['SL_NhapKho_NhomKhac'] = (
        df['SL_NhomKhac']
        .where(df['Da_Nhap_Kho'], 0)
    )

    # ======================================================
    # 11. TỒN KHO THEO TỪNG LOẠI
    # ======================================================

    df['SL_Ton_Kho_KheRangLuoc'] = (
        df['SL_KheRangLuoc']
        - df['SL_NhapKho_KheRangLuoc']
    )

    df['SL_Ton_Kho_GoiChau'] = (
        df['SL_GoiChau']
        - df['SL_NhapKho_GoiChau']
    )

    df['SL_Ton_Kho_TamVCO'] = (
        df['SL_TamVCO']
        - df['SL_NhapKho_TamVCO']
    )

    df['SL_Ton_Kho_HeCotPhuKien'] = (
        df['SL_HeCotPhuKien']
        - df['SL_NhapKho_HeCotPhuKien']
    )

    df['SL_Ton_Kho_NhomKhac'] = (
        df['SL_NhomKhac']
        - df['SL_NhapKho_NhomKhac']
    )

    # ======================================================
    # 12. TỔNG NHẬP KHO
    # ======================================================

    df['SL_Nhap_Kho'] = (
        df['SL_NhapKho_KheRangLuoc']
        + df['SL_NhapKho_GoiChau']
        + df['SL_NhapKho_TamVCO']
        + df['SL_NhapKho_HeCotPhuKien']
        + df['SL_NhapKho_NhomKhac']
    )

    # ======================================================
    # 13. NĂM
    # ======================================================

    df['Nam_Duyet'] = (
        df['Ngay_Duyet_DH_DT']
        .dt.year
        .astype('Int64')
        .astype(str)
        .replace('<NA>', '')
    )

    df['Nam_Chot'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.year
        .astype('Int64')
        .astype(str)
        .replace('<NA>', '')
    )

    df['Nam_Dat_Hang'] = (
        df['Nam_Col_D']
        .fillna(df['Nam_Duyet'])
        .fillna(df['Nam_Chot'])
        .fillna('Khác')
    )

    # ======================================================
    # 14. LÀM SẠCH TEXT
    # ======================================================

    df['Nhom_SP_Clean'] = (
        df['Nhom_SP']
        .fillna('')
        .astype(str)
        .str.strip()
    )

    df['Quy_Cach_Clean'] = (
        df['Quy_Cach']
        .fillna('')
        .astype(str)
        .str.strip()
    )

    df['Bo_Phan_KD'] = (
        df['Bo_Phan_KD']
        .fillna('')
        .astype(str)
        .str.strip()
    )

    # ======================================================
    # 15. NGÀY HIỂN THỊ
    # ======================================================

    df['Ngay_Duyet_DH'] = (
        df['Ngay_Duyet_DH_DT']
        .dt.strftime('%d/%m/%Y')
        .fillna('-')
    )

    df['Ngay_YCGH'] = (
        df['Ngay_YCGH_DT']
        .dt.strftime('%d/%m/%Y')
        .fillna('-')
    )

    df['Ngay_Chot_Cuoi'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.strftime('%d/%m/%Y')
        .fillna('-')
    )

    df['Ngay_Nhap_Kho'] = (
        df['Ngay_Nhap_Kho_DT']
        .dt.strftime('%d/%m/%Y')
        .fillna('-')
    )

    # ======================================================
    # 16. THÁNG / QUÝ
    # ======================================================

    df['Thang_Chot'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.month
        .fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    )

    df['Quy_Chot'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.quarter
        .fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)
    )

    return df


# ==========================================================
# 17. LOAD
# ==========================================================

try:

    df = load_data()

    # ======================================================
    # 18. BỘ LỌC
    # ======================================================

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:

        raw_nams = [
            str(x)
            for x in df['Nam_Dat_Hang'].unique()
            if str(x) not in ['', 'nan', 'None', 'Khác']
        ]

        nam_list = ['Tất cả các năm'] + sorted(raw_nams)

        nam_sel = st.selectbox(
            "📅 Chọn Năm (Cột D)",
            nam_list,
            index=(
                nam_list.index('2026')
                if '2026' in nam_list
                else 0
            )
        )

    with col_f2:

        ky_sel = st.selectbox(
            "⏱️ Kỳ Báo Cáo",
            [
                "Cả Năm",
                "Theo Tháng",
                "Theo Quý",
                "6 Tháng Đầu Năm",
                "6 Tháng Cuối Năm"
            ]
        )

    with col_f3:

        if ky_sel == "Theo Tháng":

            thang_sel = st.selectbox(
                "Tháng",
                list(range(1, 13)),
                index=0
            )

        elif ky_sel == "Theo Quý":

            quy_sel = st.selectbox(
                "Quý",
                [1, 2, 3, 4],
                index=0
            )

        else:

            st.write("")

    with col_f4:

        raw_bps = [
            str(x)
            for x in df['Bo_Phan_KD'].unique()
            if str(x) not in ['', 'nan', 'None']
        ]

        bp_list = ['Tất cả bộ phận'] + sorted(raw_bps)

        bp_sel = st.selectbox(
            "🏢 Bộ Phận KD",
            bp_list
        )

    # ======================================================
    # 19. LỌC DỮ LIỆU
    # ======================================================

    df_filtered = df.copy()

    if nam_sel != 'Tất cả các năm':

        df_filtered = df_filtered[
            df_filtered['Nam_Dat_Hang'] == nam_sel
        ]

    if ky_sel == "Theo Tháng":

        df_filtered = df_filtered[
            df_filtered['Thang_Chot'] == thang_sel
        ]

    elif ky_sel == "Theo Quý":

        df_filtered = df_filtered[
            df_filtered['Quy_Chot'] == quy_sel
        ]

    elif ky_sel == "6 Tháng Đầu Năm":

        df_filtered = df_filtered[
            df_filtered['Thang_Chot'].isin(
                [1, 2, 3, 4, 5, 6]
            )
        ]

    elif ky_sel == "6 Tháng Cuối Năm":

        df_filtered = df_filtered[
            df_filtered['Thang_Chot'].isin(
                [7, 8, 9, 10, 11, 12]
            )
        ]

    if bp_sel != 'Tất cả bộ phận':

        df_filtered = df_filtered[
            df_filtered['Bo_Phan_KD'] == bp_sel
        ]

    # ======================================================
    # 20. DATA NHẬP KHO
    #
    # Giữ nguyên nguyên tắc:
    # nhập kho không phụ thuộc bộ lọc Năm/Kỳ
    # ======================================================

    df_bp = df.copy()

    if bp_sel != 'Tất cả bộ phận':

        df_bp = df_bp[
            df_bp['Bo_Phan_KD'] == bp_sel
        ]

    st.markdown("---")

    # ======================================================
    # 21. CÁC TAB
    # ======================================================

    nhom_sp_list = [
        '📊 Dashboard Tổng',
        '📦 Gối Chậu',
        '⚙️ Khe Răng Lược',
        '🧱 Tấm VCO',
        '🏗️ Hệ Cột + Phụ Kiện',
        '📋 Nhóm Khác'
    ]

    tabs = st.tabs(nhom_sp_list)

    # ======================================================
    # 22. CẤU HÌNH THEO TỪNG LOẠI
    # ======================================================

    tab_config = {

        '📦 Gối Chậu': {
            'qty_col': 'SL_GoiChau',
            'nhap_col': 'SL_NhapKho_GoiChau',
            'ton_col': 'SL_Ton_Kho_GoiChau',
            'title': 'Gối Chậu'
        },

        '⚙️ Khe Răng Lược': {
            'qty_col': 'SL_KheRangLuoc',
            'nhap_col': 'SL_NhapKho_KheRangLuoc',
            'ton_col': 'SL_Ton_Kho_KheRangLuoc',
            'title': 'Khe Răng Lược'
        },

        '🧱 Tấm VCO': {
            'qty_col': 'SL_TamVCO',
            'nhap_col': 'SL_NhapKho_TamVCO',
            'ton_col': 'SL_Ton_Kho_TamVCO',
            'title': 'Tấm VCO'
        },

        '🏗️ Hệ Cột + Phụ Kiện': {
            'qty_col': 'SL_HeCotPhuKien',
            'nhap_col': 'SL_NhapKho_HeCotPhuKien',
            'ton_col': 'SL_Ton_Kho_HeCotPhuKien',
            'title': 'Hệ Cột + Phụ Kiện'
        },

        '📋 Nhóm Khác': {
            'qty_col': 'SL_NhomKhac',
            'nhap_col': 'SL_NhapKho_NhomKhac',
            'ton_col': 'SL_Ton_Kho_NhomKhac',
            'title': 'Nhóm Khác'
        }
    }

    # ======================================================
    # 23. HIỂN THỊ
    # ======================================================

    for i, tab_name in enumerate(nhom_sp_list):

        with tabs[i]:

            # ==================================================
            # DASHBOARD TỔNG
            # ==================================================

            if tab_name == '📊 Dashboard Tổng':

                df_tab = df_filtered.copy()

                # Tổng ĐH lấy đúng tổng số lượng các nhóm
                total_so_luong = (
                    df_tab['SL_TongCacNhom'].sum()
                )

                # Tổng nhập kho cũng là tổng từng nhóm
                total_nhap_kho = (
                    df_bp['SL_Nhap_Kho'].sum()
                )

                # Tồn
                total_ton_kho = (
                    total_so_luong
                    - total_nhap_kho
                )

                m1, m2, m3, m4 = st.columns(4)

                m1.metric(
                    "📋 Tổng Số Dòng/Đơn",
                    f"{len(df_tab)} Dòng"
                )

                m2.metric(
                    "📦 Tổng SL Đặt Hàng",
                    f"{total_so_luong:,.0f}"
                )

                m3.metric(
                    "✅ Tổng SL Nhập Kho",
                    f"{total_nhap_kho:,.0f}"
                )

                m4.metric(
                    "⏳ SL Còn Tồn",
                    f"{total_ton_kho:,.0f}"
                )

                st.markdown("<br>", unsafe_allow_html=True)

                search_kw = st.text_input(
                    f"🔍 Tìm kiếm trong tab [{tab_name}]:",
                    key=f"search_{i}"
                )

                if search_kw:

                    df_tab = df_tab[
                        df_tab['So_DH']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                        |
                        df_tab['Du_An']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                        |
                        df_tab['Quy_Cach']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                    ]

                cols_show = [
                    'So_DH',
                    'Nhom_SP',
                    'Trang_Thai_SX',
                    'Du_An',
                    'Quy_Cach',
                    'So_Luong_Tong_DH',
                    'SL_TongCacNhom',
                    'DVT',
                    'SL_Nhap_Kho',
                    'Ngay_Duyet_DH',
                    'Ngay_YCGH',
                    'Ngay_Chot_Cuoi',
                    'Ngay_Nhap_Kho'
                ]

                st.dataframe(
                    df_tab[cols_show],
                    column_config={

                        "So_DH": "Mã ĐH",

                        "Nhom_SP":
                            "Nhóm SP",

                        "Trang_Thai_SX":
                            "Trạng Thái",

                        "Du_An":
                            "Dự Án",

                        "Quy_Cach":
                            "Quy Cách Chủng Loại",

                        "So_Luong_Tong_DH":
                            st.column_config.NumberColumn(
                                "Số lượng tổng ĐH",
                                format="%.0f"
                            ),

                        "SL_TongCacNhom":
                            st.column_config.NumberColumn(
                                "Tổng SL Các Loại",
                                format="%.0f"
                            ),

                        "DVT":
                            "ĐVT",

                        "SL_Nhap_Kho":
                            st.column_config.NumberColumn(
                                "Đã Nhập Kho",
                                format="%.0f"
                            ),

                        "Ngay_Duyet_DH":
                            "1. Duyệt ĐH (AB)",

                        "Ngay_YCGH":
                            "2. YCGH (AC)",

                        "Ngay_Chot_Cuoi":
                            "3. Chốt Cuối (AG)",

                        "Ngay_Nhap_Kho":
                            "4. Nhập Kho (AH)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            # ==================================================
            # TỪNG NHÓM SẢN PHẨM
            # ==================================================

            else:

                cfg = tab_config[tab_name]

                qty_col = cfg['qty_col']
                nhap_col = cfg['nhap_col']
                ton_col = cfg['ton_col']

                # ----------------------------------------------
                # Chỉ lấy dòng thực sự có loại sản phẩm này
                # ----------------------------------------------

                df_tab = df_filtered[
                    df_filtered[qty_col] > 0
                ].copy()

                df_tab_bp = df_bp[
                    df_bp[qty_col] > 0
                ].copy()

                # ----------------------------------------------
                # TỔNG ĐẶT HÀNG
                # ----------------------------------------------

                total_so_luong = (
                    df_tab[qty_col].sum()
                )

                # ----------------------------------------------
                # TỔNG NHẬP KHO
                # ----------------------------------------------

                total_nhap_kho = (
                    df_tab_bp[nhap_col].sum()
                )

                # ----------------------------------------------
                # TỒN
                # ----------------------------------------------

                total_ton_kho = (
                    total_so_luong
                    - total_nhap_kho
                )

                # ==================================================
                # METRIC
                # ==================================================

                m1, m2, m3, m4 = st.columns(4)

                m1.metric(
                    "📋 Tổng Số Dòng/Đơn",
                    f"{len(df_tab)} Dòng"
                )

                m2.metric(
                    "📦 SL Đặt Hàng",
                    f"{total_so_luong:,.0f}"
                )

                m3.metric(
                    "✅ SL Nhập Kho",
                    f"{total_nhap_kho:,.0f}"
                )

                m4.metric(
                    "⏳ SL Còn Tồn",
                    f"{total_ton_kho:,.0f}"
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # ==================================================
                # TÌM KIẾM
                # ==================================================

                search_kw = st.text_input(
                    f"🔍 Tìm kiếm trong tab [{tab_name}]:",
                    key=f"search_{i}"
                )

                if search_kw:

                    df_tab = df_tab[
                        df_tab['So_DH']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                        |
                        df_tab['Du_An']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                        |
                        df_tab['Quy_Cach']
                        .astype(str)
                        .str.contains(
                            search_kw,
                            case=False,
                            na=False
                        )
                    ]

                # ==================================================
                # TẠO CỘT HIỂN THỊ RIÊNG CHO LOẠI
                # ==================================================

                df_show = df_tab.copy()

                df_show['SL_Dat_Hang'] = (
                    df_show[qty_col]
                )

                df_show['SL_Nhap_Kho_Loai'] = (
                    df_show[nhap_col]
                )

                df_show['SL_Ton_Loai'] = (
                    df_show[ton_col]
                )

                cols_show = [
                    'So_DH',
                    'Nhom_SP',
                    'Trang_Thai_SX',
                    'Du_An',
                    'Quy_Cach',
                    'SL_Dat_Hang',
                    'DVT',
                    'SL_Nhap_Kho_Loai',
                    'SL_Ton_Loai',
                    'Ngay_Duyet_DH',
                    'Ngay_YCGH',
                    'Ngay_Chot_Cuoi',
                    'Ngay_Nhap_Kho'
                ]

                # ==================================================
                # BẢNG CHI TIẾT
                # ==================================================

                st.dataframe(

                    df_show[cols_show],

                    column_config={

                        "So_DH":
                            "Mã ĐH",

                        "Nhom_SP":
                            "Nhóm SP",

                        "Trang_Thai_SX":
                            "Trạng Thái",

                        "Du_An":
                            "Dự Án",

                        "Quy_Cach":
                            "Quy Cách Chủng Loại",

                        "SL_Dat_Hang":
                            st.column_config.NumberColumn(
                                "SL Đặt Hàng",
                                format="%.0f"
                            ),

                        "DVT":
                            "ĐVT",

                        "SL_Nhap_Kho_Loai":
                            st.column_config.NumberColumn(
                                "SL Nhập Kho",
                                format="%.0f"
                            ),

                        "SL_Ton_Loai":
                            st.column_config.NumberColumn(
                                "SL Còn Tồn",
                                format="%.0f"
                            ),

                        "Ngay_Duyet_DH":
                            "1. Duyệt ĐH (AB)",

                        "Ngay_YCGH":
                            "2. YCGH (AC)",

                        "Ngay_Chot_Cuoi":
                            "3. Chốt Cuối (AG)",

                        "Ngay_Nhap_Kho":
                            "4. Nhập Kho (AH)"
                    },

                    use_container_width=True,
                    hide_index=True
                )


except Exception as e:

    st.error(
        f"Lỗi tải hoặc xử lý dữ liệu: {e}"
    )
