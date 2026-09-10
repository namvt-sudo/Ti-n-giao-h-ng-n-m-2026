import streamlit as st
import pandas as pd
import re
 
# 1. Cấu hình trang web
st.set_page_config(page_title="VHIP - Quản Lý Tiến Độ Đơn Hàng", layout="wide", initial_sidebar_state="collapsed")
 
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
 
st.title("🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG")
 
# 2. Link Google Sheets
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"
 
def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238" # Tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
 
# HÀM BÓC TÁCH SỐ LƯỢNG AN TOÀN TUYỆT ĐỐI
def clean_number_exact(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
 
    # Loại bỏ ký tự khoảng trắng không ngắt
    val_str = val_str.replace('\xa0', '').replace(' ', '')
 
    has_comma = ',' in val_str
    has_dot = '.' in val_str
 
    if has_comma and has_dot:
        # Có cả 2 dấu: dấu nào đứng sau cùng là dấu thập phân
        if val_str.rfind(',') > val_str.rfind('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif has_comma:
        # Chỉ có dấu phẩy: nếu 3 chữ số sau dấu phẩy -> phân cách hàng nghìn (VD: 1,500 -> 1500)
        # nếu không -> dấu thập phân (VD: 12,5 -> 12.5)
        parts = val_str.split(',')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace(',', '')
        else:
            val_str = val_str.replace(',', '.')
    elif has_dot:
        # Chỉ có dấu chấm: nếu 3 chữ số sau dấu chấm -> phân cách hàng nghìn (VD: 1.500 -> 1500)
        # nếu không -> giữ nguyên là dấu thập phân (VD: 12.5 vẫn là 12.5)
        parts = val_str.split('.')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace('.', '')
 
    try:
        return float(val_str)
    except:
        return 0.0
 
@st.cache_data(ttl=10)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    # Đọc tất cả các dòng dạng string
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)
 
    # DÒ CỘT THEO TÊN TIÊU ĐỀ (không dùng vị trí cố định A,B,C...) để không bị lệch
    # nếu sau này có ai chèn/xoá cột trên Google Sheet.
    header_main = df_raw.iloc[1]   # dòng tiêu đề chính (dòng 2 Excel)
    header_sub = df_raw.iloc[2]    # dòng tiêu đề phụ - cho các cột mốc thời gian (dòng 3 Excel)
 
    def find_col_exact(text, header_row, occurrence=0, default=None):
        matches = [i for i, h in enumerate(header_row) if not pd.isna(h) and str(h).strip().lower() == text.strip().lower()]
        return matches[occurrence] if len(matches) > occurrence else default
 
    def find_col_contains(text, header_row, default=None):
        for i, h in enumerate(header_row):
            if pd.isna(h):
                continue
            if text.lower() in str(h).strip().lower():
                return i
        return default
 
    idx_so_dh = find_col_exact('Số ĐH', header_main, occurrence=0, default=1)
    idx_trang_thai = find_col_exact('TÌNH TRẠNG SẢN XUẤT', header_main, default=2)
    idx_nam = find_col_exact('Năm', header_main, default=3)
    idx_bp = find_col_exact('Bộ phận KD', header_main, default=4)
    idx_nv = find_col_exact('Nhân viên KD', header_main, default=6)
    idx_duan = find_col_exact('DỰ ÁN', header_main, default=7)
    idx_quycach = find_col_exact('QUY CÁCH CHỦNG LOẠI', header_main, default=9)
    idx_dvt = find_col_exact('ĐVT', header_main, default=10)
    idx_nhomsp = find_col_exact('TÊN NHÓM SẢN PHẨM', header_main, default=12)
    idx_sl_tong = find_col_exact('Số lượng Tổng ĐH', header_main, default=13)
    idx_khe = find_col_exact('KHE RĂNG LƯỢC', header_main, default=14)
    idx_goi = find_col_exact('GỐI CHẬU', header_main, default=15)
    idx_khe_nhom = find_col_exact('Khe răng lược nhôm', header_main, default=16)
    idx_loxo = find_col_exact('LÒ XO NEO', header_main, default=17)
    idx_thanhneo = find_col_exact('Thanh neo', header_main, default=18)
    idx_spkhac = find_col_exact('SP KHÁC', header_main, default=19)
    idx_tamdeneo = find_col_exact('Tấm đế neo', header_main, default=20)
    idx_stelpin = find_col_exact('Stel pin', header_main, default=21)
    idx_vankhuon = find_col_exact('Ván khuôn', header_main, default=22)
    idx_tamvco = find_col_exact('TẤM VCO', header_main, default=23)
    idx_hecot = find_col_exact('HỆ CỘT + PHỤ KIỆN VCO', header_main, default=24)
    idx_lancan = find_col_exact('LAN CAN', header_main, default=25)
 
    idx_ngay_kd_gui = find_col_contains('Ngày KD gửi ĐH', header_sub, default=26)
    idx_ngay_duyet = find_col_contains('DUYỆT HOÀN TOÀN', header_sub, default=27)
    idx_ngay_ycgh = find_col_contains('YCGH', header_sub, default=28)
    idx_ngay_chot = find_col_contains('chốt lần cuối', header_sub, default=32)
    idx_ngay_nhapkho = find_col_contains('thực tế nhập kho', header_sub, default=33)
 
    # Đọc dữ liệu từ dòng index 4 (dòng 5 Excel)
    df = pd.DataFrame({
        'So_DH_Raw': df_raw.iloc[4:, idx_so_dh],
        'Trang_Thai_SX': df_raw.iloc[4:, idx_trang_thai],
        'Nam_Dat_Hang_Raw': df_raw.iloc[4:, idx_nam],
        'Bo_Phan_KD': df_raw.iloc[4:, idx_bp],
        'NV_KD': df_raw.iloc[4:, idx_nv],
        'Du_An': df_raw.iloc[4:, idx_duan],
        'Quy_Cach': df_raw.iloc[4:, idx_quycach],
        'DVT': df_raw.iloc[4:, idx_dvt],
        'Nhom_SP': df_raw.iloc[4:, idx_nhomsp],
        'So_Luong_Tong_DH_Raw': df_raw.iloc[4:, idx_sl_tong],
        # Mỗi nhóm sản phẩm có 1 cột riêng, giá trị = số lượng thực tế thuộc nhóm đó
        'KheRangLuoc_Raw': df_raw.iloc[4:, idx_khe],
        'GoiChau_Raw': df_raw.iloc[4:, idx_goi],
        'KheRangLuocNhom_Raw': df_raw.iloc[4:, idx_khe_nhom],
        'LoXoNeo_Raw': df_raw.iloc[4:, idx_loxo],
        'ThanhNeo_Raw': df_raw.iloc[4:, idx_thanhneo],
        'SPKhac_Raw': df_raw.iloc[4:, idx_spkhac],
        'TamDeNeo_Raw': df_raw.iloc[4:, idx_tamdeneo],
        'StelPin_Raw': df_raw.iloc[4:, idx_stelpin],
        'VanKhuon_Raw': df_raw.iloc[4:, idx_vankhuon],
        'TamVCO_Raw': df_raw.iloc[4:, idx_tamvco],
        'HeCotPhuKien_Raw': df_raw.iloc[4:, idx_hecot],
        'LanCan_Raw': df_raw.iloc[4:, idx_lancan],
    })
 
    # Lấy các mốc thời gian
    df['Ngay_KD_Gui_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_kd_gui], dayfirst=True, errors='coerce')
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_duyet], dayfirst=True, errors='coerce')
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_ycgh], dayfirst=True, errors='coerce')
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_chot], dayfirst=True, errors='coerce')
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_nhapkho], dayfirst=True, errors='coerce')
 
    # KỸ THUẬT QUAN TRỌNG: Tự động điền dữ liệu cho các ô gộp Merge Center (ffill)
    df['So_DH'] = df['So_DH_Raw'].replace('', None).ffill()
    df['Nam_Col_D'] = df['Nam_Dat_Hang_Raw'].replace('', None).ffill().astype(str).str.extract(r'(\d{4})')[0]
 
    # Bỏ dòng tiêu đề lặp lại hoặc dòng tổng
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|TỔNG|STT|Số ĐH', case=False, na=False)]
 
    # Chuyển đổi Số lượng
    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number_exact)
 
    # Số lượng riêng theo từng cột nhóm sản phẩm (nguồn chính xác nhất để lọc/tính theo nhóm)
    df['SL_KheRangLuoc'] = df['KheRangLuoc_Raw'].apply(clean_number_exact)
    df['SL_GoiChau'] = df['GoiChau_Raw'].apply(clean_number_exact)
    df['SL_KheRangLuocNhom'] = df['KheRangLuocNhom_Raw'].apply(clean_number_exact)
    df['SL_LoXoNeo'] = df['LoXoNeo_Raw'].apply(clean_number_exact)
    df['SL_ThanhNeo'] = df['ThanhNeo_Raw'].apply(clean_number_exact)
    df['SL_SPKhac'] = df['SPKhac_Raw'].apply(clean_number_exact)
    df['SL_TamDeNeo'] = df['TamDeNeo_Raw'].apply(clean_number_exact)
    df['SL_StelPin'] = df['StelPin_Raw'].apply(clean_number_exact)
    df['SL_VanKhuon'] = df['VanKhuon_Raw'].apply(clean_number_exact)
    df['SL_TamVCO'] = df['TamVCO_Raw'].apply(clean_number_exact)
    df['SL_HeCotPhuKien'] = df['HeCotPhuKien_Raw'].apply(clean_number_exact)
    df['SL_LanCan'] = df['LanCan_Raw'].apply(clean_number_exact)
 
    # Nhóm Khác = gộp các cột nhóm nhỏ lẻ còn lại (không phải Gối Chậu/Khe Răng Lược/Tấm VCO/Hệ Cột)
    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom'] + df['SL_LoXoNeo'] + df['SL_ThanhNeo'] +
        df['SL_SPKhac'] + df['SL_TamDeNeo'] + df['SL_StelPin'] +
        df['SL_VanKhuon'] + df['SL_LanCan']
    )
 
    # Lọc bỏ các dòng không có số lượng (tránh các dòng chú thích trống)
    # Chỉ loại dòng khi TẤT CẢ các cột số lượng đều = 0 — giữ lại các dòng "đợt" nhập kho
    # chỉ có giá trị ở cột nhóm riêng (VD cột P) dù cột N (Số lượng Tổng ĐH) trống/0
    df['SL_TongCacNhom'] = (
        df['SL_KheRangLuoc'] + df['SL_GoiChau'] + df['SL_TamVCO'] +
        df['SL_HeCotPhuKien'] + df['SL_NhomKhac']
    )
    df = df[(df['So_Luong_Tong_DH'] > 0) | (df['SL_TongCacNhom'] > 0)]
 
    # Với các dòng mà cột N trống/0 nhưng có số lượng ở cột nhóm, dùng luôn tổng các nhóm làm số lượng dòng đó
    df.loc[df['So_Luong_Tong_DH'] <= 0, 'So_Luong_Tong_DH'] = df.loc[df['So_Luong_Tong_DH'] <= 0, 'SL_TongCacNhom']
 
    # Trích xuất Năm chuẩn xác
    # Năm ĐẶT HÀNG: ưu tiên theo cột AA (Ngày KD gửi ĐH trên base) — đây là ngày xác định
    # đơn hàng thuộc năm nào trên thực tế, chính xác hơn cột D (có thể ghi cũ/sai)
    df['Nam_AA'] = df['Ngay_KD_Gui_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Duyet'] = df['Ngay_Duyet_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Dat_Hang'] = df['Nam_AA'].fillna(df['Nam_Col_D']).fillna(df['Nam_Duyet']).fillna(df['Nam_Chot']).fillna('Khác')
 
    # Năm NHẬP KHO: theo cột AH (ngày thực tế nhập kho) — vì đặt hàng năm trước nhưng
    # nhập kho sang năm sau thì phải tính sản lượng nhập kho vào đúng năm nhập kho thực tế
    df['Nam_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
 
    # Làm sạch văn bản
    df['Nhom_SP_Clean'] = df['Nhom_SP'].fillna('').astype(str).str.strip()
    df['Quy_Cach_Clean'] = df['Quy_Cach'].fillna('').astype(str).str.strip()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()
 
    # Định dạng Ngày hiển thị
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')
 
    # Tính số lượng đã nhập kho & tồn kho
    # Đã nhập kho = trạng thái cột C là "Done" (không chỉ dựa vào có ngày ở cột AH,
    # vì có thể có ngày nhưng trạng thái thực tế chưa "Done" / nhập một phần)
    df['Trang_Thai_SX_Clean'] = df['Trang_Thai_SX'].fillna('').astype(str).str.strip()
    df['Da_Nhap_Kho'] = df['Trang_Thai_SX_Clean'].str.lower() == 'done'
    df['SL_Nhap_Kho'] = df.apply(lambda row: row['So_Luong_Tong_DH'] if row['Da_Nhap_Kho'] else 0.0, axis=1)
    df['SL_Ton_Kho'] = df['So_Luong_Tong_DH'] - df['SL_Nhap_Kho']
 
    # Phân loại Tháng/Quý
    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month.fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter.fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)
 
    return df
 
try:
    df = load_data()
 
    # 3. BỘ LỌC THỜI GIAN & NHÂN SỰ
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
 
    with col_f1:
        raw_nams = [str(x) for x in df['Nam_Dat_Hang'].unique() if str(x) not in ['', 'nan', 'None', 'Khác']]
        nam_list = ['Tất cả các năm'] + sorted(raw_nams)
        nam_sel = st.selectbox("📅 Chọn Năm (Cột D)", nam_list, index=nam_list.index('2026') if '2026' in nam_list else 0)
 
    with col_f2:
        ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Cả Năm", "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm"])
 
    with col_f3:
        if ky_sel == "Theo Tháng":
            thang_sel = st.selectbox("Tháng", list(range(1, 13)), index=0)
        elif ky_sel == "Theo Quý":
            quy_sel = st.selectbox("Quý", [1, 2, 3, 4], index=0)
        else:
            st.write("")
 
    with col_f4:
        raw_bps = [str(x) for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'None']]
        bp_list = ['Tất cả bộ phận'] + sorted(raw_bps)
        bp_sel = st.selectbox("🏢 Bộ Phận KD", bp_list)
 
    # Lọc dữ liệu
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
 
    # df_nhap: dùng riêng để tính "Nhập kho" — lọc theo Năm dựa trên NĂM NHẬP KHO THỰC TẾ
    # (cột AH), không phải năm đặt hàng (cột AA/D). Vì đặt hàng năm trước nhưng nhập kho
    # sang năm sau thì sản lượng nhập kho phải tính vào đúng năm nhập kho thực tế đó.
    df_nhap = df.copy()
    if nam_sel != 'Tất cả các năm':
        df_nhap = df_nhap[df_nhap['Nam_Nhap_Kho'] == nam_sel]
    if bp_sel != 'Tất cả bộ phận':
        df_nhap = df_nhap[df_nhap['Bo_Phan_KD'] == bp_sel]
 
    st.markdown("---")
 
    # 4. DANH SÁCH THẺ TAB CHÍNH
    nhom_sp_list = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Hệ Cột + Phụ Kiện', '📋 Nhóm Khác']
    tabs = st.tabs(nhom_sp_list)
 
    # Mỗi nhóm sản phẩm có cột số lượng riêng trên sheet (O, P, X, Y...) — dùng thẳng
    # cột đó để lọc & tính tổng, thay vì dò chữ trong cột Nhóm SP (cột M) dễ khớp nhầm.
    tab_qty_col = {
        '📦 Gối Chậu': 'SL_GoiChau',
        '⚙️ Khe Răng Lược': 'SL_KheRangLuoc',
        '🧱 Tấm VCO': 'SL_TamVCO',
        '🏗️ Hệ Cột + Phụ Kiện': 'SL_HeCotPhuKien',
        '📋 Nhóm Khác': 'SL_NhomKhac',
    }
 
    for i, tab_name in enumerate(nhom_sp_list):
        with tabs[i]:
            if tab_name == '📊 Dashboard Tổng':
                df_tab = df_filtered.copy()
                total_so_luong = df_tab['So_Luong_Tong_DH'].sum()
                total_nhap_kho = df_nhap.loc[df_nhap['Da_Nhap_Kho'], 'So_Luong_Tong_DH'].sum()
                total_ton_kho = total_so_luong - total_nhap_kho
            else:
                qty_col = tab_qty_col[tab_name]
                # Dòng thuộc nhóm này khi cột số lượng riêng của nhóm > 0
                df_tab = df_filtered[df_filtered[qty_col] > 0]
                df_tab_nhap = df_nhap[df_nhap[qty_col] > 0]
 
                # 5. HIỂN THỊ METRIC TỔNG SỐ LƯỢNG
                # Đặt hàng: lọc theo Năm dựa trên cột AA (Ngày KD gửi ĐH)
                total_so_luong = df_tab[qty_col].sum()
                # Nhập kho: lọc theo Năm dựa trên cột AH (ngày nhập kho thực tế) + trạng thái Done
                total_nhap_kho = df_tab_nhap.loc[df_tab_nhap['Da_Nhap_Kho'], qty_col].sum()
                total_ton_kho = total_so_luong - total_nhap_kho
 
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Số Dòng/Đơn", f"{len(df_tab)} Dòng")
            m2.metric("📦 Số lượng tổng ĐH", f"{total_so_luong:,.0f}")
            m3.metric("✅ Tổng SL Nhập Kho", f"{total_nhap_kho:,.0f}")
            m4.metric("⏳ SL Tồn Cần Sản Xuất", f"{total_ton_kho:,.0f}")
 
 
            st.markdown("<br>", unsafe_allow_html=True)
 
            # 6. Ô TÌM KIẾM
            search_kw = st.text_input(f"🔍 Tìm kiếm trong tab [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]
 
            # 7. BẢNG HIỂN THỊ CHI TIẾT
            cols_show = [
                'So_DH', 'Nhom_SP', 'Trang_Thai_SX', 'Du_An', 'Quy_Cach', 'So_Luong_Tong_DH', 'DVT',
                'SL_Nhap_Kho', 'SL_Ton_Kho', 'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
            ]
 
            st.dataframe(
                df_tab[cols_show],
                column_config={
                    "So_DH": "Mã ĐH",
                    "Nhom_SP": "Nhóm SP (Cột M)",
                    "Trang_Thai_SX": "Trạng Thái (Cột C)",
                    "Du_An": "Dự Án",
                    "Quy_Cach": "Quy Cách Chủng Loại",
                    "So_Luong_Tong_DH": st.column_config.NumberColumn("Số lượng tổng ĐH", format="%.0f"),
                    "DVT": "ĐVT",
                    "SL_Nhap_Kho": st.column_config.NumberColumn("Đã Nhập Kho", format="%.0f"),
                    "SL_Ton_Kho": st.column_config.NumberColumn("Còn Tồn", format="%.0f"),
                    "Ngay_Duyet_DH": "1. Duyệt ĐH (AB)",
                    "Ngay_YCGH": "2. YCGH (AC)",
                    "Ngay_Chot_Cuoi": "3. Chốt Cuối (AG)",
                    "Ngay_Nhap_Kho": "4. Nhập Kho (AH)"
                },
                use_container_width=True,
                hide_index=True
            )
 
except Exception as e:
    st.error(f"Lỗi tải hoặc xử lý dữ liệu: {e}")
 
