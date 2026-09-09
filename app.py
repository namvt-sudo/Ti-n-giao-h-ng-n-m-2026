import streamlit as st
import pandas as pd

st.set_page_config(page_title="Chẩn Đoán Dữ Liệu Gối Chậu 2026", layout="wide")
st.title("🔍 CÔNG CỤ CHẨN ĐOÁN CHI TIẾT SỐ LƯỢNG GỐI CHẬU 2026")

# Link CSV xuất từ Google Sheet
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/export?format=csv&gid=984933238"

@st.cache_data(ttl=5)
def inspect_sheet():
    # Đọc thô toàn bộ bảng
    df_raw = pd.read_csv(GGS_URL, header=None, dtype=str)
    return df_raw

try:
    df_raw = inspect_sheet()
    
    st.info(f"Tổng số dòng tải về từ Google Sheet: **{len(df_raw)} dòng**")
    
    # 1. Cho phép xem tiêu đề các cột từ dòng 1 đến dòng 10
    with st.expander("👀 Xem 10 dòng đầu tiên của Google Sheet để xác định chính xác Cột"):
        st.dataframe(df_raw.head(10))
    
    # 2. Lấy dữ liệu từ dòng 5 (index 4)
    df = pd.DataFrame({
        'Index_Dong': list(range(5, len(df_raw) + 1)),
        'Cot_B_SoDH': df_raw.iloc[4:, 1],
        'Cot_D_Nam': df_raw.iloc[4:, 3],
        'Cot_J_QuyCach': df_raw.iloc[4:, 9],
        'Cot_M_NhomSP': df_raw.iloc[4:, 12],
        'Cot_N_SoLuong': df_raw.iloc[4:, 13],
        'Cot_AB_NgayDuyet': df_raw.iloc[4:, 27],
        'Cot_AG_NgayChot': df_raw.iloc[4:, 32]
    })
    
    # Hàm ép kiểu số an toàn
    def parse_num(val):
        if pd.isna(val) or val is None: return 0.0
        s = str(val).strip().replace('\xa0', '').replace(' ', '')
        if not s or s.lower() in ['nan', 'none', 'null', '-']: return 0.0
        if ',' in s and '.' in s:
            s = s.replace('.', '').replace(',', '.') if s.rfind(',') > s.rfind('.') else s.replace(',', '')
        elif ',' in s:
            s = s.replace(',', '.')
        try: return float(s)
        except: return 0.0

    df['So_Luong_Num'] = df['Cot_N_SoLuong'].apply(parse_num)
    
    st.markdown("---")
    st.subheader("📊 THỐNG KÊ KẾT QUẢ THEO CÁC TIÊU CHÍ KHÁC NHAU")
    
    # Kịch bản 1: Lọc Năm 2026 chính xác theo Cột D
    df_2026_colD = df[df['Cot_D_Nam'].fillna('').astype(str).str.contains('2026', na=False)]
    
    # Kịch bản 2: Lọc Năm 2026 theo Ngày Duyệt (AB) hoặc Ngày Chốt (AG)
    cond_ab = df['Cot_AB_NgayDuyet'].fillna('').astype(str).str.contains('2026', na=False)
    cond_ag = df['Cot_AG_NgayChot'].fillna('').astype(str).str.contains('2026', na=False)
    df_2026_dates = df[cond_ab | cond_ag]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("1. Tổng SL toàn bộ Sheet (Không lọc)", f"{df['So_Luong_Num'].sum():,.0f}")
    col2.metric("2. Tổng SL có Cột D = 2026", f"{df_2026_colD['So_Luong_Num'].sum():,.0f}")
    col3.metric("3. Tổng SL có Ngày 2026 (AB/AG)", f"{df_2026_dates['So_Luong_Num'].sum():,.0f}")
    
    st.markdown("---")
    st.subheader("🔎 SOI CHI TIẾT TỪ NGỮ TRONG CỘT M (NHÓM SP) VÀ CỘT J (QUY CÁCH)")
    
    # Liệt kê tất cả các giá trị duy nhất trong Cột M
    unique_m = df_2026_colD['Cot_M_NhomSP'].fillna('TRỐNG').unique()
    st.write("Các Nhóm SP (Cột M) xuất hiện trong năm 2026:", list(unique_m))
    
    kw_search = st.text_input("Nhập từ khóa nhóm/quy cách cần kiểm tra (ví dụ: Gối, Chậu, Thép, Pot,...):", value="Gối")
    
    if kw_search:
        df_match = df_2026_colD[
            df_2026_colD['Cot_M_NhomSP'].fillna('').astype(str).str.contains(kw_search, case=False) |
            df_2026_colD['Cot_J_QuyCach'].fillna('').astype(str).str.contains(kw_search, case=False)
        ]
        st.write(f"Tìm thấy **{len(df_match)} dòng** khớp từ khóa '{kw_search}' | **Tổng Số Lượng: {df_match['So_Luong_Num'].sum():,.0f}**")
        st.dataframe(df_match[['Index_Dong', 'Cot_B_SoDH', 'Cot_M_NhomSP', 'Cot_J_QuyCach', 'Cot_N_SoLuong', 'So_Luong_Num']])

except Exception as e:
    st.error(f"Lỗi: {e}")
