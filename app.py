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

# 2. HÀM ĐỌC & LÀM SẠCH DỮ LIỆU TỪ GOOGLE SHEETS
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
    if val_str.lower() == 'done':
        return 'Done'
    return val_str

@st.cache_data(ttl=5)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

    df = pd.DataFrame()
    df['So_DH'] = df_raw.iloc[3:, 1].replace('', None).ffill()          # Col B
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].apply(clean_status)       # Col C
    df['Nam_DatHang_Raw'] = df_raw.iloc[3:, 3].fillna('2026').astype(str).str.strip() # Col D
    df['Bo_Phan_KD'] = df_raw.iloc[3:, 4].astype(str).str.strip().fillna('Chưa phân loại')  # Col E
    df['NV_KD'] = df_raw.iloc[3:, 6].astype(str).str.strip().fillna('Chưa phân loại')      # Col G
    df['Du_An'] = df_raw.iloc[3:, 7].fillna('')                         # Col H
    df['Quy_Cach'] = df_raw.iloc[3:, 9].fillna('')                      # Col J
    df['DVT'] = df_raw.iloc[3:, 10].fillna('cái')                        # Col K
    df['Nhom_SP'] = df_raw.iloc[3:, 12].fillna('')                      # Col M
    df['So_Luong_Tong_DH_Raw'] = df_raw.iloc[3:, 13]                    # Col N

    # CỘT SẢN PHẨM CHÍNH
    df['SL_KheRangLuoc'] = df_raw.iloc[3:, 14].apply(clean_number)
    df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)
    df['SL_TamVCO'] = df_raw.iloc[3:, 23].apply(clean_number)
    df['SL_HeCotPhuKien'] = df_raw.iloc[3:, 24].apply(clean_number)

    # CỘT SẢN PHẨM PHỤ
    df['SL_KheRangLuocNhom'] = df_raw.iloc[3:, 16].apply(clean_number)
    df['SL_LoXoNeo'] = df_raw.iloc[3:, 17].apply(clean_number)
    df['SL_ThanhNeo'] = df_raw.iloc[3:, 18].apply(clean_number)
    df['SL_SPKhac'] = df_raw.iloc[3:, 19].apply(clean_number)
    df['SL_TamDeNeo'] = df_raw.iloc[3:, 20].apply(clean_number)
    df['SL_StelPin'] = df_raw.iloc[3:, 21].apply(clean_number)
    df['SL_VanKhuon'] = df_raw.iloc[3:, 22].apply(clean_number)
    df['SL_LanCan'] = df_raw.iloc[3:, 25].apply(clean_number)

    # MỐC THỜI GIAN
    df['Ngay_GuiDH_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')   # Col AA
    df['Ngay_Duyet_DT'] = pd.to_datetime(df_raw.iloc[3:, 27], dayfirst=True, errors='coerce')   # Col AB
    df['Ngay_Chot_DT'] = pd.to_datetime(df_raw.iloc[3:, 32], dayfirst=True, errors='coerce')    # Col AG
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce') # Col AH

    # LỌC CÁC DÒNG TIÊU ĐỀ & DÒNG RỐNG
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

    df['Ngay_DatHang_DT'] = df['Ngay_GuiDH_DT'].fillna(df['Ngay_Chot_DT']).fillna(df['Ngay_Duyet_DT'])
    
    # LẤY NĂM ĐẶT HÀNG CHUẨN
    df['Nam_DatHang'] = df['Ngay_DatHang_DT'].dt.year.fillna(
        pd.to_numeric(df['Nam_DatHang_Raw'], errors='coerce')
    ).fillna(2026).astype(int)
    
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month.fillna(1).astype(int)
    df['Quy_DatHang'] = df['Ngay_DatHang_DT'].dt.quarter.fillna(1).astype(int)

    # CỜ ĐÁNH DẤU ĐẪ NHẬP KHO
    df['Da_Nhap_Kho'] = df['Trang_Thai_SX'].astype(str).str.lower() == 'done'

    return df

try:
    df = load_data()

    # 3. KHU VỰC BỘ LỌC GIAO DIỆN
    st.subheader("🎯 Bộ Lọc Tiến Độ Sản Xuất & Sản Lượng")
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        nam_list = ['Tất cả các năm'] + sorted(list(df['Nam_DatHang'].unique()))
        nam_sel = st.selectbox("📅 Chọn Năm", nam_list, index=nam_list.index(2026) if 2026 in nam_list else 0)

    with f2:
        ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Cả Năm", "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm"])

    with f3:
        thang_sel, quy_sel = None, None
        if ky_sel == "Theo Tháng":
            danh_sach_thang = [f"Tháng {m}" for m in range(1, 13)]
            thang_chon_str = st.selectbox("🗓️ Chọn Tháng", danh_sach_thang, index=8) # Mặc định Tháng 9
            thang_sel = int(thang_chon_str.replace("Tháng ", ""))
        elif ky_sel == "Theo Quý":
            quy_chon_str = st.selectbox("📊 Chọn Quý", ["Quý 1", "Quý 2", "Quý 3", "Quý 4"], index=0)
            quy_sel = int(quy_chon_str.replace("Quý ", ""))
        else:
            st.selectbox("🗓️ Chi Tiết Kỳ", ["Tất cả (Cả năm)"], disabled=True)

    with f4:
        tt_list = ['Tất cả tình trạng'] + sorted(list(df['Trang_Thai_SX'].unique()))
        tt_sel = st.selectbox("🏭 Tình Trạng SX", tt_list)

    with f5:
        bp_list = ['Tất cả bộ phận'] + sorted([x for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
        bp_sel = st.selectbox("🏢 Bộ Phận KD", bp_list)

    col_nv, _ = st.columns([2, 3])
    with col_nv:
        df_nv_scope = df if bp_sel == 'Tất cả bộ phận' else df[df['Bo_Phan_KD'] == bp_sel]
        nv_list = ['Tất cả NVKD'] + sorted([x for x in df_nv_scope['NV_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
        nv_sel = st.selectbox("👤 Nhân Viên KD", nv_list)

    # 4. LOGIC LỌC DỮ LIỆU CẢI TIẾN
    df_dh = df.copy()

    # TH 1: Người dùng chủ động chọn Tình Trạng SX cụ thể -> BỎ QUA lọc thời gian để rà soát toàn bộ
    if tt_sel != 'Tất cả tình trạng':
        df_dh = df_dh[df_dh['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
    # TH 2: Chọn "Tất cả tình trạng" -> Áp dụng bộ lọc thời gian + Gom đơn chưa hoàn thành
    else:
        cond_nam = (df_dh['Nam_DatHang'] == nam_sel) if nam_sel != 'Tất cả các năm' else True
        cond_thuoc_ky = True
        cond_truoc_ky = False

        if ky_sel == "Theo Tháng" and thang_sel:
            cond_thuoc_ky = (df_dh['Thang_DatHang'] == thang_sel)
            cond_truoc_ky = (df_dh['Thang_DatHang'] < thang_sel)
        elif ky_sel == "Theo Quý" and quy_sel:
            cond_thuoc_ky = (df_dh['Quy_DatHang'] == quy_sel)
            cond_truoc_ky = (df_dh['Quy_DatHang'] < quy_sel)
        elif ky_sel == "6 Tháng Đầu Năm":
            cond_thuoc_ky = df_dh['Thang_DatHang'].isin([1, 2, 3, 4, 5, 6])
        elif ky_sel == "6 Tháng Cuối Năm":
            cond_thuoc_ky = df_dh['Thang_DatHang'].isin([7, 8, 9, 10, 11, 12])
            cond_truoc_ky = df_dh['Thang_DatHang'] < 7

        cond_dang_lam = (~df_dh['Trang_Thai_SX'].str.lower().isin(['done', 'tạm dừng sx', 'tam dung sx']))
        df_dh = df_dh[cond_nam & (cond_thuoc_ky | (cond_truoc_ky & cond_dang_lam))]

    # Áp dụng bộ lọc Bộ Phận & NVKD
    if bp_sel != 'Tất cả bộ phận':
        df_dh = df_dh[df_dh['Bo_Phan_KD'] == bp_sel]
    if nv_sel != 'Tất cả NVKD':
        df_dh = df_dh[df_dh['NV_KD'] == nv_sel]

    # DỮ LIỆU NHẬP KHO: Lấy tất cả dòng có đánh dấu Done trong danh sách lọc
    df_nk = df_dh[df_dh['Da_Nhap_Kho']].copy()

    st.markdown("---")

    # 5. HIỂN THỊ CÁC TAB VÀ THỐNG KÊ METRIC
    tab_names = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Cột H (Phụ Kiện)', '📋 Sản Phẩm Khác']
    tabs = st.tabs(tab_names)

    qty_mapping = {
        '📦 Gối Chậu': 'SL_GoiChau',
        '⚙️ Khe Răng Lược': 'SL_KheRangLuoc',
        '🧱 Tấm VCO': 'SL_TamVCO',
        '🏗️ Cột H (Phụ Kiện)': 'SL_HeCotPhuKien',
        '📋 Sản Phẩm Khác': 'SL_NhomKhac'
    }

    cols_display = ['So_DH', 'Trang_Thai_SX', 'Thang_DatHang', 'Bo_Phan_KD', 'NV_KD', 'Du_An', 'Quy_Cach', 'DVT']

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

            # ĐẾM SỐ LƯỢNG MÃ ĐƠN HÀNG DUY NHẤT (NUNIQUE)
            so_luong_don_hang = df_dh_tab['So_DH'].nunique()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Số Đơn Quản Lý", f"{so_luong_don_hang} Đơn")
            m2.metric("📦 Tổng SL Đặt Hàng", f"{sum_dh:,.2f}")
            m3.metric("✅ Tổng SL Nhập Kho (Done)", f"{sum_nk:,.2f}")
            m4.metric("⏳ Chênh Lệch Đặt - Nhập", f"{(sum_dh - sum_nk):,.2f}")

            st.markdown("<br>", unsafe_allow_html=True)
            search_kw = st.text_input(f"🔍 Tìm kiếm chi tiết trong [{tname}] (Mã ĐH, Dự án, Quy cách...):", key=f"s_{i}")

            if search_kw:
                df_dh_tab = df_dh_tab[
                    df_dh_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_dh_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_dh_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            sub_tab1, sub_tab2 = st.tabs(["📋 Danh Sách Đơn Hàng Cần Theo Dõi", "🏭 Danh Sách Đã Nhập Kho (Done)"])

            with sub_tab1:
                st.caption(f"Chi tiết các đơn theo điều kiện lọc ({len(df_dh_tab)} dòng quy cách):")
                st.dataframe(
                    df_dh_tab[cols_display + [q_col]],
                    column_config={
                        "So_DH": "Mã ĐH", "Trang_Thai_SX": "Trạng Thái", "Thang_DatHang": "Tháng Đặt",
                        "Bo_Phan_KD": "Bộ Phận", "NV_KD": "NVKD", "Du_An": "Dự Án", 
                        "Quy_Cach": "Quy Cách Chủng Loại", "DVT": "ĐVT",
                        q_col: st.column_config.NumberColumn("Số Lượng Đặt", format="%.2f")
                    },
                    use_container_width=True, hide_index=True
                )

            with sub_tab2:
                st.caption(f"Chi tiết các đơn đã hoàn thành nhập kho ({len(df_nk_tab)} dòng quy cách):")
                st.dataframe(
                    df_nk_tab[cols_display + [q_col]],
                    column_config={
                        "So_DH": "Mã ĐH", "Trang_Thai_SX": "Trạng Thái", "Thang_DatHang": "Tháng Đặt",
                        "Bo_Phan_KD": "Bộ Phận", "NV_KD": "NVKD", "Du_An": "Dự Án", 
                        "Quy_Cach": "Quy Cách Chủng Loại", "DVT": "ĐVT",
                        q_col: st.column_config.NumberColumn("Số Lượng Nhập Kho", format="%.2f")
                    },
                    use_container_width=True, hide_index=True
                )

except Exception as e:
    st.error(f"Lỗi kết nối hoặc xử lý dữ liệu từ Google Sheets: {e}")
