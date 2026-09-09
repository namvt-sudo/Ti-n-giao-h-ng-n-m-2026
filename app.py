import re
import numpy as np
import pandas as pd
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Hệ Thống Theo Dõi Đơn Hàng & Kế Hoạch Sản Xuất VHIP 2026",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 HỆ THỐNG THEO DÕI ĐƠN HÀNG & KẾ HOẠCH SẢN XUẤT VHIP 2026")
st.markdown("---")


# =========================================================
# 2. HÀM XỬ LÝ LÀM SẠCH DỮ LIỆU SỐ
# =========================================================
def clean_number(val):
    """Làm sạch dữ liệu số từ Excel / Google Sheets"""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    val_str = str(val).strip()
    if not val_str or val_str in ["-", "None", "nan", "NaN"]:
        return 0.0

    val_str = re.sub(r"[^0-9.-]", "", val_str)
    try:
        return float(val_str)
    except ValueError:
        return 0.0


# =========================================================
# 3. ĐỌC DỮ LIỆU ĐẦY ĐỦ TIÊU ĐỀ TỪ EXCEL / GOOGLE SHEETS
# =========================================================
@st.cache_data(ttl=300)
def load_vhip_data(file_path_or_url=None):
    """Đọc dữ liệu và duy trì đầy đủ cấu trúc các tiêu đề cột."""
    if file_path_or_url:
        try:
            df_raw = pd.read_excel(file_path_or_url)
            # Giữ nguyên cấu trúc các cột tiêu đề gốc
            df = pd.DataFrame()
            df["STT"] = df_raw.iloc[:, 0]
            df["Bộ phận"] = df_raw.iloc[:, 1]
            df["NVKD"] = df_raw.iloc[:, 2]
            df["Dự án"] = df_raw.iloc[:, 3]
            df["Nhóm hàng hoá"] = df_raw.iloc[:, 4]
            df["Chi tiết chủng loại"] = df_raw.iloc[:, 5]
            df["Số YCBG gửi VHIP"] = df_raw.iloc[:, 6]
            df["Bản vẽ duyệt sản xuất"] = df_raw.iloc[:, 7]
            df["Tháng dự kiến đặt hàng VHIP"] = df_raw.iloc[:, 9]
            df["Đơn vị"] = df_raw.iloc[:, 10]
            df["Khối lượng VHIP dự kiến cấp (ĐH)"] = df_raw.iloc[:, 11].apply(
                clean_number
            )
            df["Thời gian cần giao hàng"] = df_raw.iloc[:, 12]
            df["Ghi chú"] = df_raw.iloc[:, 14]
            return df
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu từ file: {e}")

    # Nếu không truyền file, khởi tạo dữ liệu mẫu chuẩn đầy đủ cột tiêu đề
    sample_data = [
        {
            "STT": 1,
            "Bộ phận": "PKD miền Bắc",
            "NVKD": "Mr. Thành",
            "Dự án": "Mở rộng Nội Bài - Lào Cai",
            "Nhóm hàng hoá": "Tấm VCO",
            "Chi tiết chủng loại": "Tường chống ồn hấp thụ âm",
            "Số YCBG gửi VHIP": "051/PKDMB/YCBGTC/2025",
            "Bản vẽ duyệt sản xuất": "Đang trình",
            "Tháng dự kiến đặt hàng VHIP": "Tháng 8",
            "Đơn vị": "M2",
            "Khối lượng VHIP dự kiến cấp (ĐH)": 5200,
            "SL Nhập kho thực tế": 4800,
            "Thời gian cần giao hàng": "Tháng 10",
            "Ghi chú": "Lô 1",
        },
        {
            "STT": 2,
            "Bộ phận": "PKD miền Bắc",
            "NVKD": "Mr. Đạt",
            "Dự án": "Đảo Ngọc",
            "Nhóm hàng hoá": "Khe co giãn",
            "Chi tiết chủng loại": "VHF-C100",
            "Số YCBG gửi VHIP": "0100/KDMB/YCBGTN/2026",
            "Bản vẽ duyệt sản xuất": "Đã duyệt",
            "Tháng dự kiến đặt hàng VHIP": "Tháng 11",
            "Đơn vị": "Mét",
            "Khối lượng VHIP dự kiến cấp (ĐH)": 22,
            "SL Nhập kho thực tế": 22,
            "Thời gian cần giao hàng": "Tháng 12",
            "Ghi chú": "Licogi 18",
        },
        {
            "STT": 3,
            "Bộ phận": "PKD miền Bắc",
            "NVKD": "Mr. Đạt",
            "Dự án": "Vành đai 4 HN",
            "Nhóm hàng hoá": "Gối chậu",
            "Chi tiết chủng loại": "VHB-1.2 FS, VH-1.2FX, VHB-1.2GS",
            "Số YCBG gửi VHIP": "0066/KDMB/YCBGTN/2026",
            "Bản vẽ duyệt sản xuất": "Đã duyệt",
            "Tháng dự kiến đặt hàng VHIP": "Tháng 11",
            "Đơn vị": "Mét",
            "Khối lượng VHIP dự kiến cấp (ĐH)": 70,
            "SL Nhập kho thực tế": 65,
            "Thời gian cần giao hàng": "Tháng 12",
            "Ghi chú": "Licogi 18",
        },
        {
            "STT": 4,
            "Bộ phận": "PKD miền Bắc",
            "NVKD": "Mr. Chiến",
            "Dự án": "Cầu Tứ Liên",
            "Nhóm hàng hoá": "Gối chậu",
            "Chi tiết chủng loại": "VHB - 1.3GS, VHB 1.3FS",
            "Số YCBG gửi VHIP": "119/PKDMB/YCBGTN/2026 - Lần 1",
            "Bản vẽ duyệt sản xuất": "Đang trình chấp thuận bản vẽ",
            "Tháng dự kiến đặt hàng VHIP": "Tháng 10",
            "Đơn vị": "Chiếc",
            "Khối lượng VHIP dự kiến cấp (ĐH)": 432,
            "SL Nhập kho thực tế": 400,
            "Thời gian cần giao hàng": "Tháng 11",
            "Ghi chú": "Hòa Phú",
        },
    ]
    df = pd.DataFrame(sample_data)
    df["Chênh lệch (Tồn/Thiếu)"] = (
        df["SL Nhập kho thực tế"] - df["Khối lượng VHIP dự kiến cấp (ĐH)"]
    )
    return df


# =========================================================
# 4. TỔNG HỢP CHUẨN XÁC NĂM 2026 THEO NHÓM SẢN PHẨM
# =========================================================
def get_vhip_summary_2026():
    summary_data = [
        {
            "STT": 1,
            "Nhóm Sản Phẩm": "Gối chậu",
            "ĐVT": "Cái",
            "SL Đặt Hàng (ĐH)": 11781,
            "SL Nhập Kho Thành Phẩm": 10426,
            "Chênh Lệch (Tồn/Thiếu)": 10426 - 11781,  # -1,355
            "Tỷ Lệ Hoàn Thành (%)": round((10426 / 11781) * 100, 2),
        },
        {
            "STT": 2,
            "Nhóm Sản Phẩm": "Khe răng lược",
            "ĐVT": "Mét",
            "SL Đặt Hàng (ĐH)": 3752,
            "SL Nhập Kho Thành Phẩm": 3556,
            "Chênh Lệch (Tồn/Thiếu)": 3556 - 3752,  # -196
            "Tỷ Lệ Hoàn Thành (%)": round((3556 / 3752) * 100, 2),
        },
        {
            "STT": 3,
            "Nhóm Sản Phẩm": "Tấm VCO",
            "ĐVT": "Tấm",
            "SL Đặt Hàng (ĐH)": 12863,
            "SL Nhập Kho Thành Phẩm": 11154,
            "Chênh Lệch (Tồn/Thiếu)": 11154 - 12863,  # -1,709
            "Tỷ Lệ Hoàn Thành (%)": round((11154 / 12863) * 100, 2),
        },
        {
            "STT": 4,
            "Nhóm Sản Phẩm": "Cột H",
            "ĐVT": "Cột",
            "SL Đặt Hàng (ĐH)": 1996,
            "SL Nhập Kho Thành Phẩm": 2317,
            "Chênh Lệch (Tồn/Thiếu)": 2317 - 1996,  # +321
            "Tỷ Lệ Hoàn Thành (%)": round((2317 / 1996) * 100, 2),
        },
    ]
    return pd.DataFrame(summary_data)


# =========================================================
# 5. HIỂN THỊ TRÊN GIAO DIỆN STREAMLIT
# =========================================================
df_summary = get_vhip_summary_2026()
df_details = load_vhip_data()

# --- TAB 1: BÁO CÁO TỔNG HỢP ---
tab1, tab2 = st.tabs(
    ["📊 Báo Cáo Tổng hợp 2026", "📋 Chi Tiết Kế Hoạch Sản Xuất VHIP"]
)

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="🔴 Gối Chậu (Cái)",
            value=f"{df_summary.loc[0, 'SL Nhập Kho Thành Phẩm']:,} / {df_summary.loc[0, 'SL Đặt Hàng (ĐH)']:,}",
            delta=f"{df_summary.loc[0, 'Chênh Lệch (Tồn/Thiếu)']:,} Cái",
        )
    with col2:
        st.metric(
            label="🔵 Khe Răng Lược (m)",
            value=f"{df_summary.loc[1, 'SL Nhập Kho Thành Phẩm']:,} / {df_summary.loc[1, 'SL Đặt Hàng (ĐH)']:,}",
            delta=f"{df_summary.loc[1, 'Chênh Lệch (Tồn/Thiếu)']:,} m",
        )
    with col3:
        st.metric(
            label="🟢 Tấm VCO (Tấm)",
            value=f"{df_summary.loc[2, 'SL Nhập Kho Thành Phẩm']:,} / {df_summary.loc[2, 'SL Đặt Hàng (ĐH)']:,}",
            delta=f"{df_summary.loc[2, 'Chênh Lệch (Tồn/Thiếu)']:,} Tấm",
        )
    with col4:
        st.metric(
            label="🟡 Cột H (Cột)",
            value=f"{df_summary.loc[3, 'SL Nhập Kho Thành Phẩm']:,} / {df_summary.loc[3, 'SL Đặt Hàng (ĐH)']:,}",
            delta=f"+{df_summary.loc[3, 'Chênh Lệch (Tồn/Thiếu)']:,} Cột",
        )

    st.markdown("### 📋 BẢNG TỔNG HỢP CHỈ TIÊU KẾ HOẠCH VHIP NĂM 2026")
    st.dataframe(
        df_summary.style.format({
            "SL Đặt Hàng (ĐH)": "{:,.0f}",
            "SL Nhập Kho Thành Phẩm": "{:,.0f}",
            "Chênh Lệch (Tồn/Thiếu)": "{:+,.0f}",
            "Tỷ Lệ Hoàn Thành (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 📈 BIỂU ĐỒ HOÀN THÀNH KẾ HOẠCH SẢN XUẤT")
    chart_data = df_summary.melt(
        id_vars=["Nhóm Sản Phẩm"],
        value_vars=["SL Đặt Hàng (ĐH)", "SL Nhập Kho Thành Phẩm"],
        var_name="Chỉ Tiêu",
        value_name="Số Lượng",
    )
    st.bar_chart(
        data=chart_data,
        x="Nhóm Sản Phẩm",
        y="Số Lượng",
        color="Chỉ Tiêu",
        stack=False,
    )

# --- TAB 2: CHI TIẾT THEO TIÊU ĐỀ BẢNG DỰ KIẾN SẢN LƯỢNG ---
with tab2:
    st.markdown("### 🔍 CHI TIẾT ĐƠN HÀNG VÀ KẾ HOẠCH VHIP THEO DỰ ÁN")

    # Bộ lọc dự án & nhân viên kinh doanh
    nv_filter = st.multiselect(
        "Lọc theo NVKD:",
        options=df_details["NVKD"].dropna().unique(),
        default=[],
    )
    if nv_filter:
        df_filtered = df_details[df_details["NVKD"].isin(nv_filter)]
    else:
        df_filtered = df_details

    # Hiển thị bảng dữ liệu đầy đủ tất cả các tiêu đề cột gốc
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
    )
