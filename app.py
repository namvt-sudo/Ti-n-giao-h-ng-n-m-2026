import os
import glob
import pandas as pd
import streamlit as st

# ... (Các phần code định nghĩa hàm load_data giữ nguyên) ...

st.title("🎯 Bộ Lọc Báo Cáo Tiến Độ")

# 🔍 TỰ ĐỘNG TÌM FILE EXCEL TRONG THƯ MỤC CÙNG CODE
def find_excel_file():
    # Tìm tất cả các file có đuôi .xlsx hoặc .xls trong thư mục hiện tại
    excel_files = glob.glob("*.xlsx") + glob.glob("*.xls")
    
    # Loại bỏ các file tạm của Excel (bắt đầu bằng ~$ )
    excel_files = [f for f in excel_files if not os.path.basename(f).startswith("~$")]
    
    if excel_files:
        # Lấy file Excel đầu tiên tìm thấy
        return excel_files[0]
    return None

EXCEL_FILE = find_excel_file()

if EXCEL_FILE is None:
    st.error("❌ Không tìm thấy bất kỳ file Excel (.xlsx / .xls) nào trong thư mục làm việc!")
    st.info("💡 BẠN HÃY KIỂM TRA:")
    st.markdown("""
    1. Đảm bảo file Excel theo dõi đơn hàng nằm **cùng thư mục** với file code Python này (`app.py` / `main.py`).
    2. Nếu file nằm ở thư mục khác, hãy copy file Excel vào cùng thư mục với code.
    """)
else:
    # Hiển thị thông báo file đã tìm thấy thành công (có thể ẩn đi sau)
    st.caption(f"📁 Đang đọc dữ liệu từ file: `{EXCEL_FILE}`")
    
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

        # --- HIỂN THỊ METRICS ---
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)

        with m_col1:
            st.metric(label="📋 Số Đơn Đặt Hàng", value=f"{so_don_hang} Đơn")
        with m_col2:
            st.metric(label="📦 Tổng SL Đặt Hàng", value=f"{tong_sl_dat:,.2f}")
        with m_col3:
            st.metric(label="✅ Tổng SL Nhập Kho", value=f"{tong_sl_nhap:,.2f}")
        with m_col4:
            st.metric(label="⏳ Chênh Lệch Đặt - Nhập", value=f"{chenh_lech:,.2f}")
