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
DON_VI_LIEN_TUC = {'mét', 'met', 'm', 'kg', 'tấn', 'tan', 'm2', 'm3'}
 
def clean_number_exact(val, dvt=None):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
 
    val_str = val_str.replace('\xa0', '').replace(' ', '')
 
    is_lien_tuc = str(dvt).strip().lower() in DON_VI_LIEN_TUC if dvt is not None else False
 
    has_comma = ',' in val_str
    has_dot = '.' in val_str
 
    if has_comma and has_dot:
        if val_str.rfind(',') > val_str.rfind('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif has_comma:
        parts = val_str.split(',')
        if not is_lien_tuc and len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace(',', '')
        else:
            val_str = val_str.replace(',', '.')
    elif has_dot:
        if not is_lien_tuc:
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
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)
 
    header_main = df_raw.iloc[1]
    header_sub = df_raw.iloc[2]
 
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
 
    df['Ngay_KD_Gui_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_kd_gui], dayfirst=True, errors='coerce')
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_duyet], dayfirst=True, errors='coerce')
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_ycgh], dayfirst=True, errors='coerce')
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_chot], dayfirst=True, errors='coerce')
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, idx_ngay_nhapkho], dayfirst=True, errors='coerce')
 
    df['So_DH'] = df['So_DH_Raw'].replace('', None).ffill()
    df['Nam_Col_D'] = df['Nam_Dat_Hang_Raw'].replace('', None).ffill().astype(str).str.extract(r'(\d{4})')[0]

    # QUAN TRỌNG: Cột "TÌNH TRẠNG SẢN XUẤT" (C) và "Ngày thực tế nhập kho" (AH) cũng
    # nằm trong vùng ô gộp theo từng Mã ĐH (giống cột Số ĐH/Năm ở trên). Với các đơn có
    # nhiều dòng "đợt" giao hàng riêng theo từng nhóm SP (VD: Gối Chậu ở cột P, Hệ Cột +
    # Phụ Kiện ở cột Y), chỉ dòng đầu của đơn mới có giá trị, các dòng đợt phía dưới bị
    # trống -> nếu không ffill sẽ bị hiểu nhầm là "chưa Done" / "không có ngày nhập kho"
    # và bị loại khỏi tổng Nhập Kho, làm sai lệch số liệu Gối Chậu & Hệ Cột (lỗi đã gặp).
    df['Trang_Thai_SX'] = df['Trang_Thai_SX'].replace('', None).ffill()
    df['Ngay_Nhap_Kho_DT'] = df['Ngay_Nhap_Kho_DT'].ffill()
 
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|TỔNG|STT|Số ĐH', case=False, na=False)]
 
    df['So_Luong_Tong_DH'] = df.apply(lambda r: clean_number_exact(r['So_Luong_Tong_DH_Raw'], r['DVT']), axis=1)
 
    df['SL_KheRangLuoc'] = df.apply(lambda r: clean_number_exact(r['KheRangLuoc_Raw'], r['DVT']), axis=1)
    df['SL_GoiChau'] = df.apply(lambda r: clean_number_exact(r['GoiChau_Raw'], r['DVT']), axis=1)
    df['SL_KheRangLuocNhom'] = df.apply(lambda r: clean_number_exact(r['KheRangLuocNhom_Raw'], r['DVT']), axis=1)
    df['SL_LoXoNeo'] = df.apply(lambda r: clean_number_exact(r['LoXoNeo_Raw'], r['DVT']), axis=1)
df['SL_ThanhNeo'] = df.apply(lambda r: clean_number_exact(r['ThanhNeo_Raw'], r['DVT']), axis=1)
    df['SL_SPKhac'] = df.apply(lambda r: clean_number_exact(r['SPKhac_Raw'], r['DVT']), axis=1)
    df['SL_TamDeNeo'] = df.apply(lambda r: clean_number_exact(r['TamDeNeo_Raw'], r['DVT']), axis=1)
    df['SL_StelPin'] = df.apply(lambda r: clean_number_exact(r['StelPin_Raw'], r['DVT']), axis=1)
    df['SL_VanKhuon'] = df.apply(lambda r: clean_number_exact(r['VanKhuon_Raw'], r['DVT']), axis=1)
    df['SL_TamVCO'] = df.apply(lambda r: clean_number_exact(r['TamVCO_Raw'], r['DVT']), axis=1)
    df['SL_HeCotPhuKien'] = df.apply(lambda r: clean_number_exact(r['HeCotPhuKien_Raw'], r['DVT']), axis=1)
    df['SL_LanCan'] = df.apply(lambda r: clean_number_exact(r['LanCan_Raw'], r['DVT']), axis=1)
 
    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom'] + df['SL_LoXoNeo'] + df['SL_ThanhNeo'] +
        df['SL_SPKhac'] + df['SL_TamDeNeo'] + df['SL_StelPin'] +
        df['SL_VanKhuon'] + df['SL_LanCan']
    )
 
    df['SL_TongCacNhom'] = (
        df['SL_KheRangLuoc'] + df['SL_GoiChau'] + df['SL_TamVCO'] +
        df['SL_HeCotPhuKien'] + df['SL_NhomKhac']
    )
    df = df[(df['So_Luong_Tong_DH'] > 0) | (df['SL_TongCacNhom'] > 0)]
 
    df.loc[df['So_Luong_Tong_DH'] <= 0, 'So_Luong_Tong_DH'] = df.loc[df['So_Luong_Tong_DH'] <= 0, 'SL_TongCacNhom']
 
    df['Nam_AA'] = df['Ngay_KD_Gui_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Duyet'] = df['Ngay_Duyet_DH_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Nam_Dat_Hang'] = df['Nam_AA'].fillna(df['Nam_Col_D']).fillna(df['Nam_Duyet']).fillna(df['Nam_Chot']).fillna('Khác')
 
    df['Nam_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
 
    df['Nhom_SP_Clean'] = df['Nhom_SP'].fillna('').astype(str).str.strip()
    df['Quy_Cach_Clean'] = df['Quy_Cach'].fillna('').astype(str).str.strip()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()
 
    nhom_sp_upper = df['Nhom_SP_Clean'].str.upper()
    canh_bao_list = []
    for cot_ten, cot_qty, tu_khoa in [
        ('GỐI CHẬU', 'SL_GoiChau', 'GỐI CHẬU'),
        ('KHE RĂNG LƯỢC', 'SL_KheRangLuoc', 'KHE RĂNG LƯỢC'),
        ('TẤM VCO', 'SL_TamVCO', 'TẤM VCO'),
        ('HỆ CỘT + PHỤ KIỆN VCO', 'SL_HeCotPhuKien', 'HỆ CỘT'),
    ]:
        sai = (df[cot_qty] > 0) & (~nhom_sp_upper.str.contains(tu_khoa, na=False)) & (nhom_sp_upper != '')
        if sai.any():
            tmp = df.loc[sai, ['So_DH', 'Quy_Cach_Clean', 'Nhom_SP_Clean', cot_qty]].copy()
            tmp['Cột số lượng bị nhầm'] = cot_ten
            tmp = tmp.rename(columns={cot_qty: 'Số lượng'})
            canh_bao_list.append(tmp)
df_canh_bao = pd.concat(canh_bao_list, ignore_index=True) if canh_bao_list else pd.DataFrame()
 
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')

    df['Trang_Thai_SX_Clean'] = df['Trang_Thai_SX'].fillna('').astype(str).str.strip()
    df['Da_Nhap_Kho'] = df['Trang_Thai_SX_Clean'].str.lower() == 'done'
    df['SL_Nhap_Kho'] = df.apply(lambda row: row['So_Luong_Tong_DH'] if row['Da_Nhap_Kho'] else 0.0, axis=1)
    df['SL_Ton_Kho'] = df['So_Luong_Tong_DH'] - df['SL_Nhap_Kho']
 
    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month.fillna(df['Ngay_Duyet_DH_DT'].dt.month)
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter.fillna(df['Ngay_Duyet_DH_DT'].dt.quarter)
 
    return df, df_canh_bao
 
try:
    df, df_canh_bao = load_data()
 
    if not df_canh_bao.empty:
        with st.expander(f"⚠️ Phát hiện {len(df_canh_bao)} dòng có thể bị nhập NHẦM CỘT số lượng (bấm để xem)"):
            st.caption("Số lượng đang nằm ở 1 cột nhóm, nhưng cột 'TÊN NHÓM SẢN PHẨM' lại ghi tên nhóm khác — kiểm tra và sửa lại trên Google Sheet.")
            st.dataframe(
                df_canh_bao.rename(columns={
                    'So_DH': 'Mã ĐH', 'Quy_Cach_Clean': 'Quy Cách', 'Nhom_SP_Clean': 'Cột M ghi là'
                }),
                use_container_width=True, hide_index=True
            )
 
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
 
    df_nhap = df.copy()
    if nam_sel != 'Tất cả các năm':
        df_nhap = df_nhap[df_nhap['Nam_Nhap_Kho'] == nam_sel]
    if bp_sel != 'Tất cả bộ phận':
        df_nhap = df_nhap[df_nhap['Bo_Phan_KD'] == bp_sel]
 
    st.markdown("---")
 
    nhom_sp_list = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Hệ Cột + Phụ Kiện', '📋 Nhóm Khác']
    tabs = st.tabs(nhom_sp_list)
 
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
                df_tab = df_filtered[df_filtered[qty_col] > 0]
                df_tab_nhap = df_nhap[df_nhap[qty_col] > 0]
 
                total_so_luong = df_tab[qty_col].sum()
                total_nhap_kho = df_tab_nhap.loc[df_tab_nhap['Da_Nhap_Kho'], qty_col].sum()
                total_ton_kho = total_so_luong - total_nhap_kho
 
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Số Dòng/Đơn", f"{len(df_tab)} Dòng")
            m2.metric("📦 Số lượng tổng ĐH", f"{total_so_luong:,.0f}")
            m3.metric("✅ Tổng SL Nhập Kho", f"{total_nhap_kho:,.0f}")
            m4.metric("⏳ SL Tồn Cần Sản Xuất", f"{total_ton_kho:,.0f}")
 
            st.markdown("<br>", unsafe_allow_html=True)
 
            search_kw = st.text_input(f"🔍 Tìm kiếm trong tab [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]
 
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
