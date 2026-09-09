import streamlit as st
import pandas as pd

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

# Hàm xử lý số lượng an toàn tuyệt đối
def clean_number(val):
    if pd.isna(val) or val == '':
        return 0.0
    val_str = str(val).strip()
    if ',' in val_str and '.' in val_str:
        val_str = val_str.replace('.', '').replace(',', '.')
    elif ',' in val_str:
        if len(val_str.split(',')[-1]) == 3:
            val_str = val_str.replace(',', '')
        else:
            val_str = val_str.replace(',', '.')
    elif '.' in val_str:
        if len(val_str.split('.')[-1]) == 3:
            val_str = val_str.replace('.', '')
            
    try:
        return float(val_str)
    except:
        return 0.0

@st.cache_data(ttl=10)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None)
    
    # Đọc dữ liệu từ dòng index 4 (dòng 5 Excel)
    df = pd.DataFrame({
        'So_DH': df_raw.iloc[4:, 1],          # Cột B
        'Trang_Thai_SX': df_raw.iloc[4:, 2],  # Cột C
        'Nam_Dat_Hang': df_raw.iloc[4:, 3],   # Cột D
        'Bo_Phan_KD': df_raw.iloc[4:, 4],     # Cột E
        'NV_KD': df_raw.iloc[4:, 6],         # Cột G
        'Du_An': df_raw.iloc[4:, 7],         # Cột H
        'Quy_Cach': df_raw.iloc[4:, 9],      # Cột J
        'DVT': df_raw.iloc[4:, 10],          # Cột K
        'Nhom_SP': df_raw.iloc[4:, 12],      # Cột M
        'So_Luong_Raw': df_raw.iloc[4:, 13]  # Cột N
    })
    
    # Lấy 4 mốc thời gian
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, 27], dayfirst=True, errors='coerce')    # AB
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, 28], dayfirst=True, errors='coerce')        # AC
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, 32], dayfirst=True, errors='coerce')   # AG
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, 33], dayfirst=True, errors='coerce')    # AH
    
    # Làm sạch văn bản & Ép kiểu chuỗi an toàn
    df['Nhom_SP'] = df['Nhom_SP'].fillna('').astype(str).str.strip().str.title()
    df['Bo_Phan_KD'] = df['Bo_Phan_KD'].fillna('').astype(str).str.strip()
    df['Nam_Dat_Hang'] = df['Nam_Dat_Hang'].fillna('').astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Chuẩn hóa Số Lượng
    df['So_Luong'] = df['So_Luong_Raw'].apply(clean_number)
    
    # Lọc đơn hợp lệ (có Số ĐH)
    df = df[df['So_DH'].notna() & (df['So_DH'].astype(str).str.strip() != '') & (df['So_DH'].astype(str) != 'nan')]
    
    # Định dạng Ngày hiển thị
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    
    # Tính số lượng đã nhập kho & tồn
    df['Da_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].notna()
    df['SL_Nhap_Kho'] = df.apply(lambda row: row['So_Luong'] if row['Da_Nhap_Kho'] else 0.0, axis=1)
    df['SL_Ton_Kho'] = df['So_Luong'] - df['SL_Nhap_Kho']
    
    # Phân loại Tháng/Quý
    df['Thang_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.month
    df['Quy_Chot'] = df['Ngay_Chot_Cuoi_DT'].dt.quarter
    
    return df

try:
    df = load_data()

    # 3. BỘ LỌC THỜI GIAN & NHÂN SỰ
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        raw_nams = [str(x) for x in df['Nam_Dat_Hang'].unique() if str(x) not in ['', 'nan', 'None']]
        nam_list = ['Tất cả các năm'] + sorted(raw_nams)
        nam_sel = st.selectbox("📅 Chọn Năm (Cột D)", nam_list, index=0)
        
    with col_f2:
        ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Cả Năm", "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm"])
        
    with col_f3:
        if ky_sel == "Theo Tháng":
            thang_sel = st.selectbox("Tháng", list(range(1, 13)), index=8)
        elif ky_sel == "Theo Quý":
            quy_sel = st.selectbox("Quý", [1, 2, 3, 4], index=2)
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

    st.markdown("---")

    # 4. DANH SÁCH THẺ TAB SẢN PHẨM
    raw_nhoms = [str(x) for x in df_filtered['Nhom_SP'].unique() if str(x) not in ['', 'nan', 'None']]
    nhom_sp_list = ['📊 Dashboard Tổng'] + sorted(raw_nhoms)
    tabs = st.tabs(nhom_sp_list)

    for i, tab_name in enumerate(nhom_sp_list):
        with tabs[i]:
            if tab_name == '📊 Dashboard Tổng':
                df_tab = df_filtered.copy()
            else:
                df_tab = df_filtered[df_filtered['Nhom_SP'] == tab_name]

            # 5. CÁC THẺ CON SỐ TỔNG QUAN (SỬA LỖI ĐỊNH DẠNG SỐ)
            total_so_luong = df_tab['So_Luong'].sum()
            total_nhap_kho = df_tab['SL_Nhap_Kho'].sum()
            total_ton_kho = df_tab['SL_Ton_Kho'].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📋 Tổng Số Đơn", f"{len(df_tab)} Đơn")
            m2.metric("📦 Tổng SL Đặt Hàng", f"{total_so_luong:,.0f}")
            m3.metric("✅ Tổng SL Nhập Kho", f"{total_nhap_kho:,.0f}")
            m4.metric("⏳ SL Tồn Cần Sản Xuất", f"{total_ton_kho:,.0f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # 6. Ô TÌM KIẾM NHANH
            search_kw = st.text_input(f"🔍 Tìm kiếm trong tab [{tab_name}]:", key=f"search_{i}")
            if search_kw:
                df_tab = df_tab[
                    df_tab['So_DH'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Du_An'].astype(str).str.contains(search_kw, case=False, na=False) |
                    df_tab['Quy_Cach'].astype(str).str.contains(search_kw, case=False, na=False)
                ]

            # 7. BẢNG CHI TIẾT
            cols_show = [
                'So_DH', 'Trang_Thai_SX', 'Du_An', 'Quy_Cach', 'So_Luong', 'DVT',
                'SL_Nhap_Kho', 'SL_Ton_Kho', 'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
            ]
            
            st.dataframe(
                df_tab[cols_show],
                column_config={
                    "So_DH": "Mã ĐH",
                    "Trang_Thai_SX": "Trạng Thái (Cột C)",
                    "Du_An": "Dự Án",
                    "Quy_Cach": "Quy Cách Chủng Loại",
                    "So_Luong": st.column_config.NumberColumn("SL Đặt", format="%.0f"),
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
