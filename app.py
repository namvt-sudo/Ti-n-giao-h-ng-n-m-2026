import streamlit as st
import pandas as pd
import re

# ==========================================================
# 1. CẤU HÌNH TRANG WEB
# ==========================================================

st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        padding: 1rem;
    }

    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
    }

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
# 2. LINK GOOGLE SHEETS
# ==========================================================

GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

SHEET_ID = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"

# Tab Theo dõi ĐH
GID_THEO_DOI = "984933238"


def get_ggs_export_url(url):
    return (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/export?format=csv&gid={GID_THEO_DOI}"
    )


# ==========================================================
# 3. HÀM XỬ LÝ SỐ
# ==========================================================

def clean_number_exact(val):

    if pd.isna(val) or val is None:
        return 0.0

    val_str = str(val).strip()

    if not val_str:
        return 0.0

    if val_str.lower() in [
        'nan',
        'none',
        'null',
        '-'
    ]:
        return 0.0

    # Loại bỏ khoảng trắng
    val_str = (
        val_str
        .replace('\xa0', '')
        .replace(' ', '')
    )

    has_comma = ',' in val_str
    has_dot = '.' in val_str

    # Có cả dấu phẩy và dấu chấm
    if has_comma and has_dot:

        # Dấu nào nằm cuối cùng => dấu thập phân
        if val_str.rfind(',') > val_str.rfind('.'):

            # 1.234,56 => 1234.56
            val_str = (
                val_str
                .replace('.', '')
                .replace(',', '.')
            )

        else:

            # 1,234.56 => 1234.56
            val_str = val_str.replace(',', '')

    # Chỉ có dấu phẩy
    elif has_comma:

        parts = val_str.split(',')

        # 1,500 => 1500
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace(',', '')

        # 12,5 => 12.5
        else:
            val_str = val_str.replace(',', '.')

    # Chỉ có dấu chấm
    elif has_dot:

        parts = val_str.split('.')

        # 1.500 => 1500
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace('.', '')

        # 12.5 => 12.5
        else:
            pass

    try:
        return float(val_str)

    except Exception:
        return 0.0


# ==========================================================
# 4. HÀM ĐỌC GOOGLE SHEETS
# ==========================================================

@st.cache_data(ttl=10)
def load_data():

    csv_url = get_ggs_export_url(GGS_URL)

    # Đọc toàn bộ dữ liệu dạng text
    df_raw = pd.read_csv(
        csv_url,
        header=None,
        dtype=str
    )

    # ------------------------------------------------------
    # DỮ LIỆU CƠ BẢN
    # Dòng Excel 5 => index 4
    # ------------------------------------------------------

    df = pd.DataFrame({

        # B - Số ĐH
        'So_DH_Raw':
            df_raw.iloc[4:, 1],

        # C - Tình trạng sản xuất
        'Trang_Thai_SX':
            df_raw.iloc[4:, 2],

        # D - Năm
        'Nam_Dat_Hang_Raw':
            df_raw.iloc[4:, 3],

        # E - Bộ phận KD
        'Bo_Phan_KD':
            df_raw.iloc[4:, 4],

        # G - Nhân viên KD
        'NV_KD':
            df_raw.iloc[4:, 6],

        # H - Dự án
        'Du_An':
            df_raw.iloc[4:, 7],

        # J - Quy cách
        'Quy_Cach':
            df_raw.iloc[4:, 9],

        # K - ĐVT
        'DVT':
            df_raw.iloc[4:, 10],

        # M - Tên nhóm sản phẩm
        'Nhom_SP':
            df_raw.iloc[4:, 12],

        # N - Số lượng Tổng ĐH
        'So_Luong_Tong_DH_Raw':
            df_raw.iloc[4:, 13],

        # --------------------------------------------------
        # CÁC CỘT SẢN LƯỢNG THỰC TẾ THEO NHÓM
        # --------------------------------------------------

        # O - KHE RĂNG LƯỢC
        'SL_KHE_RANG_LUOC_Raw':
            df_raw.iloc[4:, 14],

        # P - GỐI CHẬU
        'SL_GOI_CHAU_Raw':
            df_raw.iloc[4:, 15],

        # Q - Khe răng lược nhôm
        'SL_KHE_NHOM_Raw':
            df_raw.iloc[4:, 16],

        # R - Lò xo neo
        'SL_LO_XO_NEO_Raw':
            df_raw.iloc[4:, 17],

        # S - Thanh neo
        'SL_THANH_NEO_Raw':
            df_raw.iloc[4:, 18],

        # T - SP KHÁC
        'SL_SP_KHAC_Raw':
            df_raw.iloc[4:, 19],

        # U - Tấm đế neo
        'SL_TAM_DE_NEO_Raw':
            df_raw.iloc[4:, 20],

        # V - Stel pin
        'SL_STEL_PIN_Raw':
            df_raw.iloc[4:, 21],

        # W - Ván khuôn
        'SL_VAN_KHUON_Raw':
            df_raw.iloc[4:, 22],

        # X - TẤM VCO
        'SL_TAM_VCO_Raw':
            df_raw.iloc[4:, 23],

        # Y - HỆ CỘT + PHỤ KIỆN VCO
        'SL_HE_COT_VCO_Raw':
            df_raw.iloc[4:, 24],

        # Z - LAN CAN
        'SL_LAN_CAN_Raw':
            df_raw.iloc[4:, 25],
    })

    # ======================================================
    # 5. CÁC MỐC THỜI GIAN
    # ======================================================

    # AB - Ngày duyệt hoàn toàn
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 27],
        dayfirst=True,
        errors='coerce'
    )

    # AC - Ngày YCGH
    df['Ngay_YCGH_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 28],
        dayfirst=True,
        errors='coerce'
    )

    # AG - Ngày chốt cuối
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 32],
        dayfirst=True,
        errors='coerce'
    )

    # AH - Ngày thực tế nhập kho JSC
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(
        df_raw.iloc[4:, 33],
        dayfirst=True,
        errors='coerce'
    )

    # ======================================================
    # 6. TỰ ĐỘNG ĐIỀN SỐ ĐH CHO Ô MERGE
    # ======================================================

    df['So_DH'] = (
        df['So_DH_Raw']
        .replace('', None)
        .ffill()
    )

    # ======================================================
    # 7. NĂM
    # ======================================================

    df['Nam_Col_D'] = (
        df['Nam_Dat_Hang_Raw']
        .replace('', None)
        .ffill()
        .astype(str)
        .str.extract(r'(\d{4})')[0]
    )

    # ======================================================
    # 8. LOẠI DÒNG KHÔNG HỢP LỆ
    # ======================================================

    df = df[
        df['So_DH'].notna()
    ]

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
    # 9. CHUYỂN TOÀN BỘ CỘT SẢN LƯỢNG SANG SỐ
    # ======================================================

    quantity_columns = [

        'So_Luong_Tong_DH_Raw',

        'SL_KHE_RANG_LUOC_Raw',
        'SL_GOI_CHAU_Raw',
        'SL_KHE_NHOM_Raw',
        'SL_LO_XO_NEO_Raw',
        'SL_THANH_NEO_Raw',
        'SL_SP_KHAC_Raw',
        'SL_TAM_DE_NEO_Raw',
        'SL_STEL_PIN_Raw',
        'SL_VAN_KHUON_Raw',
        'SL_TAM_VCO_Raw',
        'SL_HE_COT_VCO_Raw',
        'SL_LAN_CAN_Raw'
    ]

    for col in quantity_columns:

        df[col] = (
            df[col]
            .apply(clean_number_exact)
        )

    # ======================================================
    # 10. ĐỔI TÊN THÀNH CÁC CỘT SẢN LƯỢNG DỄ DÙNG
    # ======================================================

    df['So_Luong_Tong_DH'] = (
        df['So_Luong_Tong_DH_Raw']
    )

    # O
    df['SL_KHE_RANG_LUOC'] = (
        df['SL_KHE_RANG_LUOC_Raw']
    )

    # P
    df['SL_GOI_CHAU'] = (
        df['SL_GOI_CHAU_Raw']
    )

    # Q
    df['SL_KHE_NHOM'] = (
        df['SL_KHE_NHOM_Raw']
    )

    # R
    df['SL_LO_XO_NEO'] = (
        df['SL_LO_XO_NEO_Raw']
    )

    # S
    df['SL_THANH_NEO'] = (
        df['SL_THANH_NEO_Raw']
    )

    # T
    df['SL_SP_KHAC'] = (
        df['SL_SP_KHAC_Raw']
    )

    # U
    df['SL_TAM_DE_NEO'] = (
        df['SL_TAM_DE_NEO_Raw']
    )

    # V
    df['SL_STEL_PIN'] = (
        df['SL_STEL_PIN_Raw']
    )

    # W
    df['SL_VAN_KHUON'] = (
        df['SL_VAN_KHUON_Raw']
    )

    # X
    df['SL_TAM_VCO'] = (
        df['SL_TAM_VCO_Raw']
    )

    # Y
    df['SL_HE_COT_VCO'] = (
        df['SL_HE_COT_VCO_Raw']
    )

    # Z
    df['SL_LAN_CAN'] = (
        df['SL_LAN_CAN_Raw']
    )

    # ======================================================
    # 11. LỌC DÒNG CÓ TỔNG ĐƠN HÀNG
    # ======================================================

    df = df[
        df['So_Luong_Tong_DH'] > 0
    ]

    # ======================================================
    # 12. TRÍCH XUẤT NĂM
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
    # 13. LÀM SẠCH VĂN BẢN
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
    # 14. ĐỊNH DẠNG NGÀY
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
    # 15. XÁC ĐỊNH ĐÃ NHẬP KHO
    # ======================================================

    df['Da_Nhap_Kho'] = (
        df['Ngay_Nhap_Kho_DT'].notna()
    )

    # ======================================================
    # 16. TÍNH NHẬP KHO THEO TỪNG NHÓM
    #
    # QUAN TRỌNG:
    # Không lấy N cho mọi nhóm nữa.
    #
    # Nếu AH có ngày nhập kho:
    #   Nhập = sản lượng của chính nhóm đó
    #
    # Nếu AH chưa có:
    #   Nhập = 0
    # ======================================================

    group_quantity_columns = [

        'SL_KHE_RANG_LUOC',
        'SL_GOI_CHAU',
        'SL_KHE_NHOM',
        'SL_LO_XO_NEO',
        'SL_THANH_NEO',
        'SL_SP_KHAC',
        'SL_TAM_DE_NEO',
        'SL_STEL_PIN',
        'SL_VAN_KHUON',
        'SL_TAM_VCO',
        'SL_HE_COT_VCO',
        'SL_LAN_CAN'
    ]

    for col in group_quantity_columns:

        nhap_col = (
            'NHAP_' + col
        )

        df[nhap_col] = (
            df[col]
            .where(
                df['Da_Nhap_Kho'],
                0
            )
        )

        ton_col = (
            'TON_' + col
        )

        df[ton_col] = (
            df[col]
            - df[nhap_col]
        )

    # ======================================================
    # 17. NHẬP KHO / TỒN CHO TỔNG ĐƠN HÀNG
    #
    # Chỉ dùng cho Dashboard Tổng.
    # ======================================================

    df['SL_Nhap_Kho_Tong'] = (
        df['So_Luong_Tong_DH']
        .where(
            df['Da_Nhap_Kho'],
            0
        )
    )

    df['SL_Ton_Kho_Tong'] = (
        df['So_Luong_Tong_DH']
        - df['SL_Nhap_Kho_Tong']
    )

    # Giữ tên cũ để tương thích các phần khác
    df['SL_Nhap_Kho'] = df['SL_Nhap_Kho_Tong']
    df['SL_Ton_Kho'] = df['SL_Ton_Kho_Tong']

    # ======================================================
    # 18. PHÂN LOẠI THÁNG / QUÝ
    # ======================================================

    df['Thang_Chot'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.month
        .fillna(
            df['Ngay_Duyet_DH_DT'].dt.month
        )
    )

    df['Quy_Chot'] = (
        df['Ngay_Chot_Cuoi_DT']
        .dt.quarter
        .fillna(
            df['Ngay_Duyet_DH_DT'].dt.quarter
        )
    )

    return df


# ==========================================================
# 19. HÀM XÁC ĐỊNH SẢN LƯỢNG THEO TAB
# ==========================================================

def get_tab_quantity_columns(tab_name):

    if tab_name == '📦 Gối Chậu':

        return {
            'order': 'SL_GOI_CHAU',
            'import': 'NHAP_SL_GOI_CHAU',
            'stock': 'TON_SL_GOI_CHAU'
        }

    elif tab_name == '⚙️ Khe Răng Lược':

        return {
            'order': 'SL_KHE_RANG_LUOC',
            'import': 'NHAP_SL_KHE_RANG_LUOC',
            'stock': 'TON_SL_KHE_RANG_LUOC'
        }

    elif tab_name == '🧱 Tấm VCO':

        return {
            'order': 'SL_TAM_VCO',
            'import': 'NHAP_SL_TAM_VCO',
            'stock': 'TON_SL_TAM_VCO'
        }

    elif tab_name == '🏗️ Hệ Cột + Phụ Kiện':

        return {
            'order': 'SL_HE_COT_VCO',
            'import': 'NHAP_SL_HE_COT_VCO',
            'stock': 'TON_SL_HE_COT_VCO'
        }

    elif tab_name == '📋 Nhóm Khác':

        return {
            'order': 'SL_NHOM_KHAC',
            'import': 'NHAP_SL_NHOM_KHAC',
            'stock': 'TON_SL_NHOM_KHAC'
        }

    else:

        return {
            'order': 'So_Luong_Tong_DH',
            'import': 'SL_Nhap_Kho_Tong',
            'stock': 'SL_Ton_Kho_Tong'
        }


# ==========================================================
# 20. CHẠY LOAD DATA
# ==========================================================

try:

    df = load_data()

    # ======================================================
    # TẠO NHÓM KHÁC
    #
    # Nhóm khác = tất cả sản lượng các nhóm:
    # Q + R + S + T + U + V + W + Z
    #
    # Không tính:
    # O - Khe răng lược
    # P - Gối chậu
    # X - Tấm VCO
    # Y - Hệ cột + phụ kiện VCO
    # ======================================================

    df['SL_NHOM_KHAC'] = (
        df['SL_KHE_NHOM']
        + df['SL_LO_XO_NEO']
        + df['SL_THANH_NEO']
        + df['SL_SP_KHAC']
        + df['SL_TAM_DE_NEO']
        + df['SL_STEL_PIN']
        + df['SL_VAN_KHUON']
        + df['SL_LAN_CAN']
    )

    df['NHAP_SL_NHOM_KHAC'] = (
        df['NHAP_SL_KHE_NHOM']
        + df['NHAP_SL_LO_XO_NEO']
        + df['NHAP_SL_THANH_NEO']
        + df['NHAP_SL_SP_KHAC']
        + df['NHAP_SL_TAM_DE_NEO']
        + df['NHAP_SL_STEL_PIN']
        + df['NHAP_SL_VAN_KHUON']
        + df['NHAP_SL_LAN_CAN']
    )

    df['TON_SL_NHOM_KHAC'] = (
        df['SL_NHOM_KHAC']
        - df['NHAP_SL_NHOM_KHAC']
    )

    # ======================================================
    # 21. BỘ LỌC THỜI GIAN & NHÂN SỰ
    # ======================================================

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    # ------------------------------------------------------
    # NĂM
    # ------------------------------------------------------

    with col_f1:

        raw_nams = [
            str(x)
            for x in df['Nam_Dat_Hang'].unique()
            if str(x) not in [
                '',
                'nan',
                'None',
                'Khác'
            ]
        ]

        nam_list = (
            ['Tất cả các năm']
            + sorted(raw_nams)
        )

        default_index = 0

        if '2026' in nam_list:
            default_index = nam_list.index('2026')

        nam_sel = st.selectbox(
            "📅 Chọn Năm (Cột D)",
            nam_list,
            index=default_index
        )

    # ------------------------------------------------------
    # KỲ BÁO CÁO
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # THÁNG / QUÝ
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # BỘ PHẬN
    # ------------------------------------------------------

    with col_f4:

        raw_bps = [
            str(x)
            for x in df['Bo_Phan_KD'].unique()
            if str(x) not in [
                '',
                'nan',
                'None'
            ]
        ]

        bp_list = (
            ['Tất cả bộ phận']
            + sorted(raw_bps)
        )

        bp_sel = st.selectbox(
            "🏢 Bộ Phận KD",
            bp_list
        )

    # ======================================================
    # 22. LỌC DỮ LIỆU
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

    st.markdown("---")

    # ======================================================
    # 23. DANH SÁCH TAB
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
    # 24. TỪ KHÓA PHÂN NHÓM
    # ======================================================

    kw_goi_chau = (
        'Gối|Chậu'
    )

    kw_khe_luoc = (
        'Khe|Lược'
    )

    kw_tam_vco = (
        'Tấm|VCO'
    )

    kw_cot_pk = (
        'Cột|Phụ Kiện'
    )

    kw_loai_tru = (
        'Gối|Chậu|Khe|Lược|Tấm|VCO|Cột|Phụ Kiện'
    )

    # ======================================================
    # 25. HIỂN THỊ TỪNG TAB
    # ======================================================

    for i, tab_name in enumerate(nhom_sp_list):

        with tabs[i]:

            # ------------------------------------------------
            # PHÂN LOẠI TAB
            # ------------------------------------------------

            if tab_name == '📊 Dashboard Tổng':

                df_tab = (
                    df_filtered.copy()
                )

            elif tab_name == '📦 Gối Chậu':

                df_tab = df_filtered[
                    df_filtered[
                        'Nhom_SP_Clean'
                    ].str.contains(
                        kw_goi_chau,
                        case=False,
                        na=False
                    )
                ].copy()

            elif tab_name == '⚙️ Khe Răng Lược':

                df_tab = df_filtered[
                    df_filtered[
                        'Nhom_SP_Clean'
                    ].str.contains(
                        kw_khe_luoc,
                        case=False,
                        na=False
                    )
                ].copy()

            elif tab_name == '🧱 Tấm VCO':

                df_tab = df_filtered[
                    df_filtered[
                        'Nhom_SP_Clean'
                    ].str.contains(
                        kw_tam_vco,
                        case=False,
                        na=False
                    )
                ].copy()

            elif tab_name == '🏗️ Hệ Cột + Phụ Kiện':

                df_tab = df_filtered[
                    df_filtered[
                        'Nhom_SP_Clean'
                    ].str.contains(
                        kw_cot_pk,
                        case=False,
                        na=False
                    )
                ].copy()

            else:

                df_tab = df_filtered[
                    ~df_filtered[
                        'Nhom_SP_Clean'
                    ].str.contains(
                        kw_loai_tru,
                        case=False,
                        na=False
                    )
                ].copy()

            # ------------------------------------------------
            # CỘT SẢN LƯỢNG CỦA TAB
            # ------------------------------------------------

            qty_info = get_tab_quantity_columns(
                tab_name
            )

            order_col = qty_info['order']
            import_col = qty_info['import']
            stock_col = qty_info['stock']

            # ------------------------------------------------
            # METRIC
            # ------------------------------------------------

            total_so_luong = (
                df_tab[order_col].sum()
            )

            total_nhap_kho = (
                df_tab[import_col].sum()
            )

            total_ton_kho = (
                df_tab[stock_col].sum()
            )

            # ------------------------------------------------
            # 4 METRIC
            # ------------------------------------------------

            m1, m2, m3, m4 = st.columns(4)

            m1.metric(
                "📋 Tổng Số Dòng/Đơn",
                f"{len(df_tab):,} Dòng"
            )

            m2.metric(
                "📦 Số lượng đặt hàng",
                f"{total_so_luong:,.0f}"
            )

            m3.metric(
                "✅ Tổng SL Nhập Kho",
                f"{total_nhap_kho:,.0f}"
            )

            m4.metric(
                "⏳ SL Tồn Cần Sản Xuất",
                f"{total_ton_kho:,.0f}"
            )

            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )

            # ------------------------------------------------
            # TÌM KIẾM
            # ------------------------------------------------

            search_kw = st.text_input(
                f"🔍 Tìm kiếm trong tab [{tab_name}]:",
                key=f"search_{i}"
            )

            if search_kw:

                search_text = (
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
                )

                df_tab = df_tab[
                    search_text
                ].copy()

            # ------------------------------------------------
            # BẢNG HIỂN THỊ
            # ------------------------------------------------

            cols_show = [

                'So_DH',

                'Nhom_SP',

                'Trang_Thai_SX',

                'Du_An',

                'Quy_Cach',

                # Số lượng tổng ĐH
                'So_Luong_Tong_DH',

                # Sản lượng nhóm
                'SL_KHE_RANG_LUOC',
                'SL_GOI_CHAU',
                'SL_KHE_NHOM',
                'SL_LO_XO_NEO',
                'SL_THANH_NEO',
                'SL_SP_KHAC',
                'SL_TAM_DE_NEO',
                'SL_STEL_PIN',
                'SL_VAN_KHUON',
                'SL_TAM_VCO',
                'SL_HE_COT_VCO',
                'SL_LAN_CAN',

                'DVT',

                # Tổng nhập / tồn
                'SL_Nhap_Kho_Tong',
                'SL_Ton_Kho_Tong',

                'Ngay_Duyet_DH',
                'Ngay_YCGH',
                'Ngay_Chot_Cuoi',
                'Ngay_Nhap_Kho'
            ]

            # Chỉ lấy những cột thực sự tồn tại
            cols_show = [
                c for c in cols_show
                if c in df_tab.columns
            ]

            # ------------------------------------------------
            # CẤU HÌNH TIÊU ĐỀ
            # ------------------------------------------------

            column_config = {

                "So_DH":
                    "Mã ĐH",

                "Nhom_SP":
                    "Nhóm SP (Cột M)",

                "Trang_Thai_SX":
                    "Trạng Thái (Cột C)",

                "Du_An":
                    "Dự Án",

                "Quy_Cach":
                    "Quy Cách Chủng Loại",

                "So_Luong_Tong_DH":
                    st.column_config.NumberColumn(
                        "Số lượng Tổng ĐH",
                        format="%.0f"
                    ),

                "SL_KHE_RANG_LUOC":
                    st.column_config.NumberColumn(
                        "KHE RĂNG LƯỢC",
                        format="%.0f"
                    ),

                "SL_GOI_CHAU":
                    st.column_config.NumberColumn(
                        "GỐI CHẬU",
                        format="%.0f"
                    ),

                "SL_KHE_NHOM":
                    st.column_config.NumberColumn(
                        "Khe răng lược nhôm",
                        format="%.0f"
                    ),

                "SL_LO_XO_NEO":
                    st.column_config.NumberColumn(
                        "LÒ XO NEO",
                        format="%.0f"
                    ),

                "SL_THANH_NEO":
                    st.column_config.NumberColumn(
                        "Thanh neo",
                        format="%.0f"
                    ),

                "SL_SP_KHAC":
                    st.column_config.NumberColumn(
                        "SP KHÁC",
                        format="%.0f"
                    ),

                "SL_TAM_DE_NEO":
                    st.column_config.NumberColumn(
                        "Tấm đế neo",
                        format="%.0f"
                    ),

                "SL_STEL_PIN":
                    st.column_config.NumberColumn(
                        "Stel pin",
                        format="%.0f"
                    ),

                "SL_VAN_KHUON":
                    st.column_config.NumberColumn(
                        "Ván khuôn",
                        format="%.0f"
                    ),

                "SL_TAM_VCO":
                    st.column_config.NumberColumn(
                        "TẤM VCO",
                        format="%.0f"
                    ),

                "SL_HE_COT_VCO":
                    st.column_config.NumberColumn(
                        "HỆ CỘT + PHỤ KIỆN VCO",
                        format="%.0f"
                    ),

                "SL_LAN_CAN":
                    st.column_config.NumberColumn(
                        "LAN CAN",
                        format="%.0f"
                    ),

                "DVT":
                    "ĐVT",

                "SL_Nhap_Kho_Tong":
                    st.column_config.NumberColumn(
                        "Đã Nhập Kho",
                        format="%.0f"
                    ),

                "SL_Ton_Kho_Tong":
                    st.column_config.NumberColumn(
                        "Còn Tồn",
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
            }

            # ------------------------------------------------
            # HIỂN THỊ BẢNG
            # ------------------------------------------------

            st.dataframe(

                df_tab[cols_show],

                column_config=column_config,

                use_container_width=True,

                hide_index=True
            )

except Exception as e:

    st.error(
        f"Lỗi tải hoặc xử lý dữ liệu: {e}"
    )

    st.exception(e)
