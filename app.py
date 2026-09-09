import streamlit as st
import pandas as pd

# 1. Cấu hình giao diện di động
st.set_page_config(page_title="Báo Cáo Tiến Độ & Sản Lượng", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { padding: 0.5rem; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Quản Lý Tiến Độ & Sản Lượng")

# 2. Link Google Sheets
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238" # Tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

# 3. Đọc dữ liệu từ Google Sheets
@st.cache_data(ttl=10)
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None)
    
    # Bắt đầu lấy dữ liệu từ dòng index 4 (dòng 5 trong Excel)
    df = pd.DataFrame({
        'So_DH': df_raw.iloc[4:, 1],          # Cột B: Số ĐH
        'Bo_Phan_KD': df_raw.iloc[4:, 4],     # Cột E: BPKD
        'NV_KD': df_raw.iloc[4:, 6],         # Cột G: Nhân viên KD
        'Du_An': df_raw.iloc[4:, 7],         # Cột H: Dự án
        'Quy_Cach': df_raw.iloc[4:, 9],      # Cột J: Quy cách chủng loại
        'DVT': df_raw.iloc[4:, 10],          # Cột K: ĐVT
        'Nhom_SP': df_raw.iloc[4:, 12],      # Cột M: Tên nhóm SP
        'So_Luong_Raw': df_raw.iloc[4:, 13]  # Cột N: SỐ or TRỌNG LƯỢNG
    })
    
    # Lấy 4 mốc thời gian quan trọng
    df['Ngay_Duyet_DH_DT'] = pd.to_datetime(df_raw.iloc[4:, 27], dayfirst=True, errors='coerce')    # Cột AB
    df['Ngay_YCGH_DT'] = pd.to_datetime(df_raw.iloc[4:, 28], dayfirst=True, errors='coerce')        # Cột AC
    df['Ngay_Chot_Cuoi_DT'] = pd.to_datetime(df_raw.iloc[4:, 32], dayfirst=True, errors='coerce')   # Cột AG
    df['Ngay_Nhap_Kho_DT'] = pd.to_datetime(df_raw.iloc[4:, 33], dayfirst=True, errors='coerce')    # Cột AH
    
    # Xử lý Số Lượng chuẩn xác
    df['So_Luong'] = df['So_Luong_Raw'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['So_Luong'] = pd.to_numeric(df['So_Luong'], errors='coerce').fillna(0)
    
    # Lọc bỏ dòng trống Số ĐH
    df = df[df['So_DH'].notna() & (df['So_DH'] != '')]
    
    # Định dạng hiển thị Ngày
    df['Ngay_Duyet_DH'] = df['Ngay_Duyet_DH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_YCGH'] = df['Ngay_YCGH_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Chot_Cuoi'] = df['Ngay_Chot_Cuoi_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    df['Ngay_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].dt.strftime('%d/%m/%Y').fillna('-')
    
    # Trạng thái Nhập kho
    df['Da_Nhap_Kho'] = df['Ngay_Nhap_Kho_DT'].notna()
    df['SL_Nhap_Kho'] = df.apply(lambda row: row['So_Luong'] if row['Da_Nhap_Kho'] else 0, axis=1)
    df['SL_Ton_Khos'] = df['So_Luong'] - df['SL_Nhap_Kho']
    
    # Phân loại Tháng/Quý theo Ngày Duyệt ĐH
    df['Thang'] = df['Ngay_Duyet_DH_DT'].dt.month
    df['Quy'] = df['Ngay_Duyet_DH_DT'].dt.quarter
    
    return df

try:
    df = load_data()

    # 4. BỘ LỌC THỜI GIAN FLEXIBLE
    st.subheader("🎯 Bộ Lọc Báo Cáo")
    c1, c2 = st.columns(2)
    
    with c1:
        ky_lay_so = st.selectbox("Chọn Kỳ Báo Cáo", [
            "Theo Tháng", "Theo Quý", "6 Tháng Đầu Năm", "6 Tháng Cuối Năm", "Cả Năm"
        ])
    
    with c2:
        if ky_lay_so == "Theo Tháng":
            thang_sel = st.selectbox("Chọn Tháng", list(range(1, 13)), index=0)
            df_filtered = df[df['Thang'] == thang_sel]
        elif ky_lay_so == "Theo Quý":
            quy_sel = st.selectbox("Chọn Quý", [1, 2, 3, 4], index=0)
            df_filtered = df[df['Quy'] == quy_sel]
        elif ky_lay_so == "6 Tháng Đầu Năm":
            df_filtered = df[df['Thang'].isin([1, 2, 3, 4, 5, 6])]
        elif ky_lay_so == "6 Tháng Cuối Năm":
            df_filtered = df[df['Thang'].isin([7, 8, 9, 10, 11, 12])]
        else:
            df_filtered = df.copy()

    # 5. THỐNG KÊ TỔNG QUAN
    total_dat = df_filtered['So_Luong'].sum()
    total_nhap = df_filtered['SL_Nhap_Kho'].sum()
    total_ton = df_filtered['SL_Ton_Khos'].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng SL Đặt Hàng", f"{int(total_dat):,}")
    m2.metric("Tổng SL Nhập Kho", f"{int(total_nhap):,}")
    m3.metric("Tổng SL Còn Tồn", f"{int(total_ton):,}")

    st.markdown("---")

    # 6. BẢNG TỔNG HỢP SẢN LƯỢNG THEO NHÓM SẢN PHẨM
    st.subheader("📊 Báo Cáo Tổng Hợp Theo Nhóm Sản Phẩm")
    
    df_nhom = df_filtered.groupby('Nhom_SP').agg(
        SL_Dat=('So_Luong', 'sum'),
        SL_Nhap=('SL_Nhap_Kho', 'sum'),
        SL_Ton=('SL_Ton_Khos', 'sum')
    ).reset_index()
    
    df_nhom['Ty_Le_Hoan_Thanh'] = (df_nhom['SL_Nhap'] / df_nhom['SL_Dat'] * 100).fillna(0).round(1).astype(str) + '%'
    
    st.dataframe(
        df_nhom,
        column_config={
            "Nhom_SP": "Nhóm Sản Phẩm",
            "SL_Dat": st.column_config.NumberColumn("SL Đặt Hàng", format="%d"),
            "SL_Nhap": st.column_config.NumberColumn("SL Nhập Kho", format="%d"),
            "SL_Ton": st.column_config.NumberColumn("SL Còn Tồn", format="%d"),
            "Ty_Le_Hoan_Thanh": "Tỷ Lệ Hoàn Thành"
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # 7. BẢNG CHI TIẾT TỪNG ĐƠN HÀNG (CÓ 4 CỘT NGÀY)
    st.subheader("📋 Chi Tiết Từng Đơn Hàng")
    
    cols_display = [
        'So_DH', 'Du_An', 'Quy_Cach', 'So_Luong', 'DVT', 
        'Ngay_Duyet_DH', 'Ngay_YCGH', 'Ngay_Chot_Cuoi', 'Ngay_Nhap_Kho'
    ]
    
    st.dataframe(
        df_filtered[cols_display],
        column_config={
            "So_DH": "Số ĐH",
            "Du_An": "Dự Án",
            "Quy_Cach": "Quy Cách",
            "So_Luong": st.column_config.NumberColumn("Số Lượng", format="%d"),
            "DVT": "ĐVT",
            "Ngay_Duyet_DH": "1. Ngày Duyệt ĐH (AB)",
            "Ngay_YCGH": "2. Ngày YCGH (AC)",
            "Ngay_Chot_Cuoi": "3. Ngày Chốt Cuối (AG)",
            "Ngay_Nhap_Kho": "4. Ngày Nhập Kho (AH)"
        },
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
