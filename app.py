import streamlit as st
import pandas as pd
import os

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Bộ Lọc Báo Cáo Tiến Độ",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------------------------------
# HÀM ĐỌC VÀ XỬ LÝ DỮ LIỆU AN TOÀN
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ Không tìm thấy file Excel tại đường dẫn: {file_path}")
        return None

    try:
        # Đọc dữ liệu thô từ sheet 'Theo dõi ĐH'
        df_raw = pd.read_excel(file_path, sheet_name='Theo dõi ĐH', header=None)
        
        df = pd.DataFrame()
        
        # 1. Trích xuất thông tin cơ bản
        df['So_DH']         = df_raw.iloc[3:, 1].replace('', None).ffill()
        df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].fillna('Chưa SX')
        df['Bo_Phan_KD']    = df_raw.iloc[3:, 4].fillna('Chưa phân loại')
        df['NV_KD']         = df_raw.iloc[3:, 6].fillna('Chưa phân loại')

        # Hàm ép kiểu số an toàn
        def clean_number(val):
            if pd.isna(val) or val is None:
                return 0.0
            val_str = str(val).strip().replace('\xa0', '').replace(' ', '')
            if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
                return 0.0
            try:
                return float(val_str)
            except:
                return 0.0

        # 2. Số lượng Gối Chậu (Cột P - Index 15)
        df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)

        # Lọc bỏ dòng tiêu đề rác
        df = df[df['So_DH'].notna()]
        df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

        # ---------------------------------------------------------
        # 3. XỬ LÝ NGÀY THÁNG (CỘT AA LÀM NGÀY ĐẶT HÀNG CHUẨN)
        # ---------------------------------------------------------
        # 🟢 Ngày Đặt Hàng: CHỈ LẤY CỘT AA (Index 26 - Ngày BPKD gửi ĐH)
        df['Ngay_DatHang_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')
        df['Nam_DatHang']     = df['Ngay_DatHang_DT'].dt.year.fillna(0).astype(int).astype(str)
        df['Thang_DatHang']   = df['Ngay_DatHang_DT'].dt.month.fillna(0).astype(int)

        # 🔵 Ngày Nhập Kho: LẤY CỘT AH (Index 33 - Ngày thực tế nhập kho)
        df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce')
        df['Da_Nhap_Kho']     = df['Trang_Thai_SX'].astype(str).str.strip().str.lower() == 'done'
        df['Nam_NhapKho']     = df['Ngay_NhapKho_DT'].dt.year.fillna(0).astype(int).astype(str)
        df['Thang_NhapKho']   = df['Ngay_NhapKho_DT'].dt.month.fillna(0).astype(int)

        return df

    except Exception as e:
        st.error(f"❌ Lỗi khi đọc dữ liệu Excel: {e}")
        return None

# ---------------------------------------------------------
# GIAO DIỆN CHÍNH STREAMLIT
# ---------------------------------------------------------
st.title("🎯 Bộ Lọc Báo Cáo Tiến Độ")

# Đường dẫn file Excel (Đảm bảo file nằm cùng thư mục hoặc chỉnh lại đường dẫn)
EXCEL_FILE = "_NĂM 2026 BẢNG THEO DÕI ĐƠN ĐẶT HÀNG.xlsx"

# Load dữ liệu
df = load_data(EXCEL_FILE)

if df is not None:
    # --- BỘ LỌC TẬP TRUNG (FILTERS) ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        selected_year = st.selectbox("Chọn Năm", options=["2026", "2025"], index=0)
    with col2:
        selected_ky = st.selectbox("Kỳ Báo Cáo", options=["Theo Tháng", "Theo Quý", "Cả Năm"], index=0)
    with col3:
        selected_month = st.selectbox("Tháng", options=list(range(1, 13)), index=7) # Default tháng 8
    with col4:
        selected_status = st.selectbox("Tình Trạng SX", options=["Tất cả tình trạng", "Done", "Chưa SX"], index=0)
    with col5:
        selected_bpkd = st.selectbox("Bộ Phận KD", options=["Tất cả bộ phận"] + list(df['Bo_Phan_KD'].unique()), index=0)

    st.markdown("---")

    # --- LỌC DỮ LIỆU THEO ĐIỀU KIỆN ---
    # Filter Đặt Hàng (Cột AA)
    df_dat = df[(df['Nam_DatHang'] == str(selected_year)) & (df['Thang_DatHang'] == selected_month)]
    
    # Filter Nhập Kho (Cột AH)
    df_nhap = df[(df['Da_Nhap_Kho']) & (df['Nam_NhapKho'] == str(selected_year)) & (df['Thang_NhapKho'] == selected_month)]

    if selected_bpkd != "Tất cả bộ phận":
        df_dat = df_dat[df_dat['Bo_Phan_KD'] == selected_bpkd]
        df_nhap = df_nhap[df_nhap['Bo_Phan_KD'] == selected_bpkd]

    # --- TÍNH TOÁN METRICS ---
    so_don_hang = df_dat['So_DH'].nunique()
    tong_sl_dat = df_dat['SL_GoiChau'].sum()
    tong_sl_nhap = df_nhap['SL_GoiChau'].sum()
    chenh_lech = tong_sl_dat - tong_sl_nhap

    # --- HIỂN THỊ METRICS (4 Ô KPI MÀU TRẮNG GIỐNG ẢNH MẪU) ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.metric(label="📋 Số Đơn Đặt Hàng", value=f"{so_don_hang} Đơn")
    with m_col2:
        st.metric(label="📦 Tổng SL Đặt Hàng", value=f"{tong_sl_dat:,.2f}")
    with m_col3:
        st.metric(label="✅ Tổng SL Nhập Kho", value=f"{tong_sl_nhap:,.2f}")
    with m_col4:
        st.metric(label="⏳ Chênh Lệch Đặt - Nhập", value=f"{chenh_lech:,.2f}")
