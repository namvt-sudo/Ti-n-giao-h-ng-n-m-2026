import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# HÀM XỬ LÝ VÀ CHUẨN HÓA DỮ LIỆU CẮT/RÚT TỪ GOOGLE SHEETS
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def load_data(file_path):
    # Đọc dữ liệu thô từ sheet 'Theo dõi ĐH'
    df_raw = pd.read_excel(file_path, sheet_name='Theo dõi ĐH', header=None)
    
    df = pd.DataFrame()
    
    # 1. Các thông tin cơ bản của Đơn hàng
    df['So_DH']         = df_raw.iloc[3:, 1].replace('', None).ffill()
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].fillna('Chưa SX')
    df['Bo_Phan_KD']    = df_raw.iloc[3:, 4].fillna('Chưa phân loại')
    df['NV_KD']         = df_raw.iloc[3:, 6].fillna('Chưa phân loại')
    df['Du_An']         = df_raw.iloc[3:, 7].fillna('')
    df['Quy_Cach']      = df_raw.iloc[3:, 9].fillna('')
    df['DVT']           = df_raw.iloc[3:, 10].fillna('cái')
    df['Nhom_SP']       = df_raw.iloc[3:, 12].fillna('')

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

    # 2. Số lượng từng nhóm sản phẩm (Ví dụ: Gối Chậu - Cột P / Index 15)
    df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)
    # (Thêm các cột Số Lượng nhóm SP khác nếu có...)

    # Lọc bỏ các dòng tiêu đề rác hoặc dòng trống
    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

    # ---------------------------------------------------------
    # 3. XỬ LÝ MỐC THỜI GIAN (CHUẨN CHỐT)
    # ---------------------------------------------------------
    
    # 🟢 NGÀY ĐẶT HÀNG: LẤY DUY NHẤT CỘT AA (Index 26 - Ngày BPKD gửi ĐH)
    df['Ngay_DatHang_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')
    
    df['Nam_DatHang']   = df['Ngay_DatHang_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month
    df['Quy_DatHang']   = df['Ngay_DatHang_DT'].dt.quarter

    # 🔵 NGÀY NHẬP KHO: GIỮ NGUYÊN CỘT AH (Index 33 - Ngày thực tế nhập kho)
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce')
    df['Da_Nhap_Kho']     = df['Trang_Thai_SX'].astype(str).str.strip().str.lower() == 'done'
    
    df['Nam_NhapKho']   = df['Ngay_NhapKho_DT'].dt.year.astype(str).str.replace('.0', '', regex=False)
    df['Thang_NhapKho'] = df['Ngay_NhapKho_DT'].dt.month
    df['Quy_NhapKho']   = df['Ngay_NhapKho_DT'].dt.quarter

    return df

# ---------------------------------------------------------
# HÀM BÁO CÁO / FILTER STREAMLIT (VÍ DỤ TÍNH BÁO CÁO THÁNG)
# ---------------------------------------------------------
def get_dashboard_metrics(df, selected_year, selected_month):
    # Lọc ĐẶT HÀNG theo Cột AA (Năm & Tháng Đặt Hàng)
    df_dat_hang = df[
        (df['Nam_DatHang'] == str(selected_year)) & 
        (df['Thang_DatHang'] == selected_month)
    ]
    
    # Lọc NHẬP KHO theo Cột AH (Năm & Tháng Nhập Kho)
    df_nhap_kho = df[
        (df['Da_Nhap_Kho']) & 
        (df['Nam_NhapKho'] == str(selected_year)) & 
        (df['Thang_NhapKho'] == selected_month)
    ]
    
    # Tính tổng SL Gối Chậu
    tong_sl_dat_hang = df_dat_hang['SL_GoiChau'].sum()
    tong_sl_nhap_kho = df_nhap_kho['SL_GoiChau'].sum()
    chenh_lech = tong_sl_dat_hang - tong_sl_nhap_kho
    
    return tong_sl_dat_hang, tong_sl_nhap_kho, chenh_lech
