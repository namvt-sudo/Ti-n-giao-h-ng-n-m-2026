import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bộ Lọc Báo Cáo Tiến Độ (Google Sheets)", page_icon="🎯", layout="wide")

# 🟢 THAY ID GOOGLE SHEET VÀ TÊN SHEET CỦA BẠN VÀO ĐÂY:
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"  # Ví dụ: 1ABC123xyz_ID_CUA_BAN
SHEET_NAME = "Theo dõi ĐH"

# Link xuất dữ liệu dạng CSV từ Google Sheets
GGS_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=60) # Tự động làm mới dữ liệu sau mỗi 60 giây
def load_data_from_ggs(url):
    # Đọc file CSV trực tiếp từ link Google Sheets (bỏ 3 dòng tiêu đề đầu)
    df_raw = pd.read_csv(url, skiprows=3, header=None)
    df = pd.DataFrame()

    df['So_DH']         = df_raw.iloc[:, 1].replace('', None).ffill()
    df['Trang_Thai_SX'] = df_raw.iloc[:, 2].fillna('Chưa SX')
    df['Bo_Phan_KD']    = df_raw.iloc[:, 4].fillna('Chưa phân loại')

    def clean_number(val):
        if pd.isna(val) or val is None: return 0.0
        val_str = str(val).strip().replace('\xa0', '').replace(' ', '').replace(',', '')
        if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']: return 0.0
        try: return float(val_str)
        except: return 0.0

    df['SL_GoiChau'] = df_raw.iloc[:, 15].apply(clean_number)

    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

    # 🟢 CỘT AA (Index 26): Ngày Đặt Hàng
    df['Ngay_DatHang_DT'] = pd.to_datetime(df_raw.iloc[:, 26], dayfirst=True, errors='coerce')
    df['Nam_DatHang']     = df['Ngay_DatHang_DT'].dt.year.fillna(0).astype(int).astype(str)
    df['Thang_DatHang']   = df['Ngay_DatHang_DT'].dt.month.fillna(0).astype(int)

    # 🔵 CỘT AH (Index 33): Ngày Nhập Kho
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[:, 33], dayfirst=True, errors='coerce')
    df['Da_Nhap_Kho']     = df['Trang_Thai_SX'].astype(str).str.strip().str.lower() == 'done'
    df['Nam_NhapKho']     = df['Ngay_NhapKho_DT'].dt.year.fillna(0).astype(int).astype(str)
    df['Thang_NhapKho']   = df['Ngay_NhapKho_DT'].dt.month.fillna(0).astype(int)

    return df

st.title("🎯 Bộ Lọc Báo Cáo Tiến Độ (Dữ Liệu Trực Tiếp Từ Google Sheets)")

try:
    df = load_data_from_ggs(GGS_URL)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: selected_year = st.selectbox("Chọn Năm", options=["2026", "2025"], index=0)
    with col2: selected_ky = st.selectbox("Kỳ Báo Cáo", options=["Theo Tháng", "Theo Quý", "Cả Năm"], index=0)
    with col3: selected_month = st.selectbox("Tháng", options=list(range(1, 13)), index=7) # Tháng 8
    with col4: selected_status = st.selectbox("Tình Trạng SX", options=["Tất cả tình trạng", "Done", "Chưa SX"], index=0)
    with col5: selected_bpkd = st.selectbox("Bộ Phận KD", options=["Tất cả bộ phận"] + list(df['Bo_Phan_KD'].unique()), index=0)

    st.markdown("---")

    df_dat = df[(df['Nam_DatHang'] == str(selected_year)) & (df['Thang_DatHang'] == selected_month)]
    df_nhap = df[(df['Da_Nhap_Kho']) & (df['Nam_NhapKho'] == str(selected_year)) & (df['Thang_NhapKho'] == selected_month)]

    if selected_bpkd != "Tất cả bộ phận":
        df_dat = df_dat[df_dat['Bo_Phan_KD'] == selected_bpkd]
        df_nhap = df_nhap[df_nhap['Bo_Phan_KD'] == selected_bpkd]

    so_don_hang = df_dat['So_DH'].nunique()
    tong_sl_dat = df_dat['SL_GoiChau'].sum()
    tong_sl_nhap = df_nhap['SL_GoiChau'].sum()
    chenh_lech = tong_sl_dat - tong_sl_nhap

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.metric(label="📋 Số Đơn Đặt Hàng", value=f"{so_don_hang} Đơn")
    with m_col2: st.metric(label="📦 Tổng SL Đặt Hàng", value=f"{tong_sl_dat:,.2f}")
    with m_col3: st.metric(label="✅ Tổng SL Nhập Kho", value=f"{tong_sl_nhap:,.2f}")
    with m_col4: st.metric(label="⏳ Chênh Lệch Đặt - Nhập", value=f"{chenh_lech:,.2f}")

except Exception as e:
    st.error(f"❌ Không thể kết nối với Google Sheets: {e}")
    st.info("💡 Hãy kiểm tra xem file Google Sheets đã được bật quyền chia sẻ công khai 'Bất kỳ ai có liên kết đều có thể xem' chưa.")
