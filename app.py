import streamlit as st
import pandas as pd

# Thiết lập trang Streamlit
st.set_page_config(page_title="Theo Dõi Đơn Hàng Nội Bộ", layout="wide")

st.title("BẢNG THEO DÕI CÁC ĐƠN HÀNG NỘI BỘ")

# 1. HÀM ĐỌC VÀ TẢI DỮ LIỆU (Thay đổi theo đường dẫn/nguồn dữ liệu thực tế của bạn)
@st.cache_data
def load_data():
    # Ví dụ: Giả định bạn load dữ liệu từ các sheet hoặc ghép dữ liệu các năm
    # Bạn có thể thay bằng pd.read_excel() hoặc kết nối Google Sheets tại đây
    
    # Giả định dữ liệu mẫu để chạy mã:
    data = {
        'Số ĐH': ['1', '2', '3', '40', '252', '31'],
        'Năm': [2026, 2026, 2026, 2025, 2025, 2026],
        'TÌNH TRẠNG SẢN XUẤT': ['Done', 'Done', 'Done', 'Tạm dừng SX', 'Chưa SX', 'Đang SX'],
        'Nhân viên kỹ thuật': ['Nguyễn Văn Thành', 'Nguyễn Văn Thành', 'Lê Văn Phong', 'PXNK', 'VTTB', 'Lê Văn Phong'],
        'Mục đích phục vụ / Dự án': ['Nắp bịt tấm đan', 'Tấm ép máy QC', 'Gối chỏm cầu', 'Malolos Clark Package', 'Cầu Sông Rạng', 'Sản xuất BTP'],
        'Số / Trọng lượng': [5, 1, 1, 1, 60, 30]
    }
    df = pd.DataFrame(data)
    
    # Chuẩn hóa cột TÌNH TRẠNG SẢN XUẤT (xóa khoảng trắng thừa)
    if 'TÌNH TRẠNG SẢN XUẤT' in df.columns:
        df['TÌNH TRẠNG SẢN XUẤT'] = df['TÌNH TRẠNG SẢN XUẤT'].astype(str).str.strip()
        
    return df

# Tải dữ liệu
df = load_data()

# 2. XÂY DỰNG BỘ LỌC Ở SIDEBAR
st.sidebar.header("BỘ LỌC DỮ LIỆU")

# --- Bộ lọc Năm ---
danh_sach_nam = sorted(df['Năm'].dropna().astype(int).unique(), reverse=True)
selected_nam = st.sidebar.selectbox("Chọn Năm:", options=["Tất cả"] + list(danh_sach_nam))

# --- Bộ lọc Tình trạng sản xuất ---
danh_sach_tinh_trang = sorted(df['TÌNH TRẠNG SẢN XUẤT'].dropna().unique())
selected_tinh_trang = st.sidebar.multiselect(
    "Tình trạng SX:", 
    options=danh_sach_tinh_trang,
    help="Khi chọn Tình trạng cụ thể, hệ thống sẽ hiển thị các đơn trên TẤT CẢ CÁC NĂM."
)

# 3. XỬ LÝ LOGIC LỌC DỮ LIỆU HOÀN CHỈNH
df_filtered = df.copy()

if selected_tinh_trang:
    # TRƯỜNG HỢP 1: Có chọn Tình trạng SX (vd: "Tạm dừng SX", "Chưa SX"...)
    # -> BỎ QUA điều kiện Năm, lọc lấy dữ liệu ở tất cả các năm (2024, 2025, 2026...)
    df_filtered = df_filtered[df_filtered['TÌNH TRẠNG SẢN XUẤT'].isin(selected_tinh_trang)]
    st.info(f"💡 Đang hiển thị Tình trạng **{', '.join(selected_tinh_trang)}** trên **TẤT CẢ CÁC NĂM**.")
else:
    # TRƯỜNG HỢP 2: Không chọn Tình trạng SX cụ thể (hoặc để trống)
    # -> Áp dụng bộ lọc Năm bình thường
    if selected_nam != "Tất cả":
        df_filtered = df_filtered[df_filtered['Năm'] == selected_nam]

# 4. HIỂN THỊ KẾT QUẢ VÀ THỐNG KÊ
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Tổng số đơn hàng tìm thấy", value=len(df_filtered))

st.dataframe(df_filtered, use_container_width=True)
