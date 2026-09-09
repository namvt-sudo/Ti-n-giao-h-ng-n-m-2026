import streamlit as st
import pandas as pd

# 1. Cấu hình giao diện di động
st.set_page_config(page_title="Kế Hoạch Giao Hàng", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { padding: 0.5rem; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Kế Hoạch Giao Hàng")

# 2. ĐƯỜNG LINK GOOGLE SHEETS CỦA BẠN (Đã cập nhật chuẩn)
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

# Hàm chuyển đổi link GGS sang dạng dữ liệu trực tiếp theo GID tab 'Theo dõi ĐH'
def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238" # GID tab Theo dõi ĐH
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

# 3. Đọc dữ liệu tự động từ Google Sheets
@st.cache_data(ttl=30)  # Tự động cập nhật dữ liệu mới sau 30 giây
def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None)
    
    df = pd.DataFrame({
        'So_DH': df_raw.iloc[3:, 1],
        'Bo_Phan_KD': df_raw.iloc[3:, 4],
        'NV_KD': df_raw.iloc[3:, 5],
        'Du_An': df_raw.iloc[3:, 7],
        'Quy_Cach': df_raw.iloc[3:, 9],
        'DVT': df_raw.iloc[3:, 10],
        'Nhom_SP': df_raw.iloc[3:, 12],
        'So_Luong': df_raw.iloc[3:, 13]
    })
    
    df['Ngay_Xuong_DH_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], format='mixed', errors='coerce')
    df['Ngay_Can_Giao_DT'] = pd.to_datetime(df_raw.iloc[3:, 28], format='mixed', errors='coerce')
    
    today = pd.to_datetime('today').normalize()
    df['So_Ngay_Con_Lai'] = (df['Ngay_Can_Giao_DT'] - today).dt.days
    
    def canh_bao(days):
        if pd.isna(days): return '⚪ Chưa hạn'
        days = int(days)
        if days < 0: return f'🔴 Chậm {abs(days)}d'
        elif days <= 3: return f'🟠 Khẩn cấp ({days}d)'
        elif days <= 7: return f'🟡 Sắp hạn ({days}d)'
        else: return f'🟢 Đảm bảo ({days}d)'
        
    df['Canh_Bao'] = df['So_Ngay_Con_Lai'].apply(canh_bao)
    df['Ngay_Xuong_DH'] = df['Ngay_Xuong_DH_DT'].dt.strftime('%d/%m/%Y')
    df['Ngay_Can_Giao'] = df['Ngay_Can_Giao_DT'].dt.strftime('%d/%m/%Y')
    df['Thang'] = df['Ngay_Can_Giao_DT'].dt.month
    df['So_Luong'] = pd.to_numeric(df['So_Luong'], errors='coerce').fillna(0)
    df['NV_KD'] = df['NV_KD'].fillna('N/A')
    
    return df

try:
    df = load_data()

    # 4. Bộ lọc trên điện thoại
    col1, col2 = st.columns(2)
    with col1:
        thang_list = sorted([int(x) for x in df['Thang'].dropna().unique()])
        thang_selected = st.selectbox("📅 Chọn Tháng", options=thang_list, index=0 if thang_list else 0)
    with col2:
        nhom_list = ['Tất cả'] + list(df['Nhom_SP'].dropna().unique())
        nhom_selected = st.selectbox("📦 Nhóm SP", options=nhom_list)

    # Lọc Dữ Liệu
    df_filtered = df[df['Thang'] == thang_selected]
    if nhom_selected != 'Tất cả':
        df_filtered = df_filtered[df_filtered['Nhom_SP'] == nhom_selected]

    # 5. Thẻ thống kê
    m1, m2 = st.columns(2)
    m1.metric("Tổng đơn trong tháng", f"{len(df_filtered)} đơn")
    don_gap = len(df_filtered[df_filtered['So_Ngay_Con_Lai'] <= 3])
    m2.metric("Đơn Cần Chú Ý (<=3d)", f"{don_gap} đơn")

    # 6. Bảng danh sách chi tiết
    st.subheader("📋 Danh Sách Đơn Hàng")
    cols_display = ['So_DH', 'Du_An', 'Quy_Cach', 'So_Luong', 'DVT', 'Ngay_Xuong_DH', 'Ngay_Can_Giao', 'Canh_Bao']
    st.dataframe(df_filtered[cols_display], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Lỗi tải dữ liệu. Vui lòng kiểm tra lại quyền Chia sẻ trên Google Sheets! Lỗi: {e}")