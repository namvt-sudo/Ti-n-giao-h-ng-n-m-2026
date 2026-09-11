import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# 1. CẤU HÌNH TRANG WEB & TỐI ƯU CSS CHO THANH TAB NỔI BẬT
st.set_page_config(page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Bố cục chung */
    .main { padding: 1rem; }
    
    .main-title {
        color: #0d47a1;
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }

    /* TIÊU ĐỀ BỘ LỌC ĐẸP & CHUYÊN NGHIỆP */
    .sub-title-clean {
        color: #0d47a1;
        font-size: 20px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    /* NHÃN TIÊU ĐỀ BỘ LỌC ĐẬM VÀ RÕ NÉT */
    div[data-testid="stWidgetLabel"] label, 
    div[data-testid="stWidgetLabel"] p {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        opacity: 1 !important;
    }

    /* VIỀN VÀ KHUNG Ô CHỌN SELECTBOX */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1.5px solid #94a3b8 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* ========================================================= */
    /* NỔI BẬT KHUNG VÀ CHỮ CHO DÃY TAB (GỐI CHẬU, KHE RĂNG LƯỢC...) */
    /* CẬP NHẬT SELECTOR CHUẨN MỚI NHẤT CHO STREAMLIT               */
    /* ========================================================= */
    
    /* 1. Khoảng cách khung chứa danh sách Tab */
    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 10px !important;
        border-bottom: 2px solid #cbd5e1 !important;
        padding-bottom: 8px !important;
    }

    /* 2. Trạng thái Tab THƯỜNG (Chưa chọn): TẠO KHUNG ĐẬM, NỀN TRẮNG, CHỮ ĐEN ĐẬM */
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] {
        background-color: #f8fafc !important;
        border: 2px solid #64748b !important; /* Khung viền xám đậm rõ ràng */
        border-radius: 8px !important;         /* Bo góc tròn đẹp mắt */
        padding: 8px 18px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Định dạng chữ bên trong Tab thường */
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] p,
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] span {
        color: #0f172a !important;            /* Màu chữ đen đậm nét */
        font-weight: 800 !important;          /* Ép kiểu chữ In Đậm */
        font-size: 15px !important;
    }

    /* 3. Hiệu ứng RÊ CHUỘT (Hover) vào Tab */
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"]:hover {
        border-color: #1d4ed8 !important;
        background-color: #eff6ff !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"]:hover p {
        color: #1d4ed8 !important;
    }

    /* 4. Trạng thái TAB ĐƯỢC CHỌN (Active): NỀN XANH NỔI BẬT, CHỮ TRẮNG IN ĐẬM */
    div[data-testid="stTabs"] div[role="tablist"] button[aria-selected="true"] {
        background-color: #1d4ed8 !important;  /* Nền xanh lam đậm nổi bật */
        border: 2px solid #1e40af !important;  /* Viền xanh đậm */
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.4) !important;
    }

    /* Định dạng chữ màu trắng khi Tab được chọn */
    div[data-testid="stTabs"] div[role="tablist"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] div[role="tablist"] button[aria-selected="true"] span {
        color: #ffffff !important;            /* Chữ trắng nổi bật trên nền xanh */
        font-weight: 900 !important;
    }

    /* Tắt vạch đỏ nhấp nháy mặc định bên dưới tab của Streamlit */
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }

    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 12px 16px;
        border-radius: 10px;
        border-left: 5px solid #1976d2;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #0d47a1 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1565c0 !important;
        font-weight: 800 !important;
    }

    /* BẢNG DỮ LIỆU */
    div[data-testid="stDataFrame"] th {
        background-color: #0d47a1 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. HÀM XỬ LÝ DỮ LIỆU
GGS_URL = "https://docs.google.com/spreadsheets/d/1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw/edit?usp=sharing"

def get_ggs_export_url(url):
    sheet_id = "1Wewl_WwSYLR0ydq71vtHJC82ndk4EjqcNMqSVNvsByw"
    gid = "984933238"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

def clean_number(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip().replace('\xa0', '').replace(' ', '')
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
    if '.' in val_str and ',' in val_str:
        val_str = val_str.replace('.', '').replace(',', '.')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')
    elif '.' in val_str:
        parts = val_str.split('.')
        if len(parts) > 1 and len(parts[-1]) == 3:
            val_str = val_str.replace('.', '')
    try:
        return float(val_str)
    except:
        return 0.0

def clean_status(val):
    if pd.isna(val) or val is None:
        return 'Chưa SX'
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'none', 'null', '']:
        return 'Chưa SX'
    return val_str

def tinh_canh_bao_tien_do(row):
    if row['Da_Nhap_Kho']:
        return "✅ Đã Hoàn Thành"
    if pd.isna(row['Ngay_Duyet_AB']):
        return "⚪ Chưa Duyệt SX (AB trống)"
    if pd.isna(row['Ngay_Chot_AG']):
        return "⚠️ Thiếu Ngày Chốt AG"
    
    ngay_hien_tai = pd.to_datetime('today').normalize()
    songay_con_lai = (row['Ngay_Chot_AG'] - ngay_hien_tai).days
    
    if songay_con_lai <= 5:
        return "🔴 Rất Nguy Hiểm (≤ 5 Ngày)"
    elif songay_con_lai <= 7:
        return "🟠 Cấp Bách / Ưu Tiên (6-7 Ngày)"
    elif songay_con_lai <= 15:
        return "🟡 Tiến Độ Bình Thường (8-15 Ngày)"
    elif songay_con_lai <= 30:
        return "🟢 An Toàn (16-30 Ngày)"
    else:
        return "🔵 Rất An Toàn (> 30 Ngày)"

def style_canh_bao(val):
    if '🔴' in str(val):
        return 'background-color: #ffc9c9; color: #900C3F; font-weight: bold;'
    elif '🟠' in str(val):
        return 'background-color: #ffe5b4; color: #d35400; font-weight: bold;'
    elif '🟡' in str(val):
        return 'background-color: #fff9c4; color: #856404;'
    elif '🟢' in str(val):
        return 'background-color: #d4edda; color: #155724;'
    elif '⚪' in str(val):
        return 'background-color: #e9ecef; color: #6c757d;'
    return ''

def apply_style_safe(styler, func, subset):
    if hasattr(styler, 'map'):
        return styler.map(func, subset=subset)
    else:
        return styler.applymap(func, subset=subset)

def convert_df_to_excel(df_moi, df_ton, df_done, cols, label_ky):
    output = io.BytesIO()
    clean_label = re.sub(r'[\/\\\?\*\:\[\]]', '-', str(label_ky))
    sheet_moi = f"Đặt Mới {clean_label}"[:31]
    sheet_ton = f"Tồn Trước {clean_label}"[:31]
    sheet_done = f"Đã Nhập Kho {clean_label}"[:31]
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_moi[cols].to_excel(writer, index=False, sheet_name=sheet_moi)
        df_ton[cols].to_excel(writer, index=False, sheet_name=sheet_ton)
        df_done[cols].to_excel(writer, index=False, sheet_name=sheet_done)
    return output.getvalue()

def load_data():
    csv_url = get_ggs_export_url(GGS_URL)
    df_raw = pd.read_csv(csv_url, header=None, dtype=str)

    df = pd.DataFrame()
    df['So_DH'] = df_raw.iloc[3:, 1].replace('', None).ffill()
    df['Trang_Thai_SX'] = df_raw.iloc[3:, 2].apply(clean_status)
    df['Nam_DatHang_Raw'] = df_raw.iloc[3:, 3].fillna('2026').astype(str).str.strip()
    df['Bo_Phan_KD'] = df_raw.iloc[3:, 4].astype(str).str.strip().fillna('Chưa phân loại')
    df['NV_KD'] = df_raw.iloc[3:, 6].astype(str).str.strip().fillna('Chưa phân loại')
    df['Du_An'] = df_raw.iloc[3:, 7].fillna('')
    df['Quy_Cach'] = df_raw.iloc[3:, 9].fillna('')
    df['DVT'] = df_raw.iloc[3:, 10].fillna('cái')
    df['So_Luong_Tong_DH_Raw'] = df_raw.iloc[3:, 13]

    df['SL_KheRangLuoc'] = df_raw.iloc[3:, 14].apply(clean_number)
    df['SL_GoiChau'] = df_raw.iloc[3:, 15].apply(clean_number)
    df['SL_TamVCO'] = df_raw.iloc[3:, 23].apply(clean_number)
    df['SL_HeCotPhuKien'] = df_raw.iloc[3:, 24].apply(clean_number)

    df['SL_KheRangLuocNhom'] = df_raw.iloc[3:, 16].apply(clean_number)
    df['SL_LoXoNeo'] = df_raw.iloc[3:, 17].apply(clean_number)
    df['SL_ThanhNeo'] = df_raw.iloc[3:, 18].apply(clean_number)
    df['SL_SPKhac'] = df_raw.iloc[3:, 19].apply(clean_number)
    df['SL_TamDeNeo'] = df_raw.iloc[3:, 20].apply(clean_number)
    df['SL_StelPin'] = df_raw.iloc[3:, 21].apply(clean_number)
    df['SL_VanKhuon'] = df_raw.iloc[3:, 22].apply(clean_number)
    df['SL_LanCan'] = df_raw.iloc[3:, 25].apply(clean_number)

    df['Ngay_GuiDH_DT'] = pd.to_datetime(df_raw.iloc[3:, 26], dayfirst=True, errors='coerce')
    df['Ngay_Duyet_AB'] = pd.to_datetime(df_raw.iloc[3:, 27], dayfirst=True, errors='coerce')
    df['Ngay_KD_Can_AC'] = pd.to_datetime(df_raw.iloc[3:, 28], dayfirst=True, errors='coerce')
    df['Ngay_Chot_AG'] = pd.to_datetime(df_raw.iloc[3:, 32], dayfirst=True, errors='coerce')
    df['Ngay_NhapKho_DT'] = pd.to_datetime(df_raw.iloc[3:, 33], dayfirst=True, errors='coerce')

    df = df[df['So_DH'].notna()]
    df = df[~df['So_DH'].astype(str).str.contains('Tổng|Tong|STT|Số ĐH', case=False, na=False)]

    df['So_Luong_Tong_DH'] = df['So_Luong_Tong_DH_Raw'].apply(clean_number)
    df['SL_NhomKhac'] = (
        df['SL_KheRangLuocNhom'] + df['SL_LoXoNeo'] + df['SL_ThanhNeo'] +
        df['SL_SPKhac'] + df['SL_TamDeNeo'] + df['SL_StelPin'] +
        df['SL_VanKhuon'] + df['SL_LanCan']
    )
    df['SL_TongCalculated'] = df['SL_KheRangLuoc'] + df['SL_GoiChau'] + df['SL_TamVCO'] + df['SL_HeCotPhuKien'] + df['SL_NhomKhac']
    df.loc[df['So_Luong_Tong_DH'] <= 0, 'So_Luong_Tong_DH'] = df.loc[df['So_Luong_Tong_DH'] <= 0, 'SL_TongCalculated']

    df['Ngay_DatHang_DT'] = df['Ngay_GuiDH_DT'].fillna(df['Ngay_Chot_AG']).fillna(df['Ngay_Duyet_AB'])
    
    df['Nam_DatHang'] = df['Ngay_DatHang_DT'].dt.year.fillna(
        pd.to_numeric(df['Nam_DatHang_Raw'], errors='coerce')
    ).fillna(2026).astype(int)
    df['Thang_DatHang'] = df['Ngay_DatHang_DT'].dt.month.fillna(1).astype(int)

    df['Da_Nhap_Kho'] = (df['Trang_Thai_SX'].str.lower() == 'done') | (df['Ngay_NhapKho_DT'].notna())
    df['Ngay_NK_Check'] = df['Ngay_NhapKho_DT']

    df['Canh_Bao_Tien_Do'] = df.apply(tinh_canh_bao_tien_do, axis=1)

    return df


# 3. DASHBOARD MAIN RENDER
@st.fragment(run_every=10)
def render_dashboard():
    thoi_gian_cap_nhat = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    st.markdown(f'<div style="font-size: 14px; color: #1e88e5; font-weight: 700; margin-bottom: 2px;">🔄 Cập nhật lúc: {thoi_gian_cap_nhat}</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">🛡️ VHIP - QUẢN LÝ TIẾN ĐỘ & SẢN LƯỢNG NĂM 2026</div>', unsafe_allow_html=True)

    try:
        df = load_data()

        st.markdown('<div class="sub-title-clean">🎯 Bộ Lọc Tiến Độ Sản Xuất & Sản Lượng</div>', unsafe_allow_html=True)

        f1, f2, f3, f4, f5 = st.columns(5)

        with f1:
            nam_list = ['Tất cả các năm'] + sorted(list(df['Nam_DatHang'].unique()))
            nam_sel = st.selectbox("📅 Chọn Năm Báo Cáo", nam_list, index=nam_list.index(2026) if 2026 in nam_list else 0)

        with f2:
            ky_sel = st.selectbox("⏱️ Kỳ Báo Cáo", ["Theo Tháng", "Theo Quý", "Cả Năm"])

        with f3:
            thang_sel, quy_sel = None, None
            if ky_sel == "Theo Tháng":
                danh_sach_thang = [f"Tháng {m}" for m in range(1, 13)]
                thang_chon_str = st.selectbox("🗓️ Chọn Tháng", danh_sach_thang, index=7)
                thang_sel = int(thang_chon_str.replace("Tháng ", ""))
            elif ky_sel == "Theo Quý":
                quy_chon_str = st.selectbox("📊 Chọn Quý", ["Quý 1", "Quý 2", "Quý 3", "Quý 4"], index=2)
                quy_sel = int(quy_chon_str.replace("Quý ", ""))
            else:
                st.selectbox("🗓️ Chi Tiết Kỳ", ["Tất cả (Cả năm)"], disabled=True)

        with f4:
            tt_list = ['Tất cả tình trạng'] + sorted(list(df['Trang_Thai_SX'].unique()))
            tt_sel = st.selectbox("🏭 Tình Trạng SX", tt_list)

        with f5:
            bp_list = ['Tất cả bộ phận'] + sorted([x for x in df['Bo_Phan_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
            bp_sel = st.selectbox("🏢 Bộ Phận KD", bp_list)

        col_nv, _ = st.columns([2, 3])
        with col_nv:
            df_nv_scope = df if bp_sel == 'Tất cả bộ phận' else df[df['Bo_Phan_KD'] == bp_sel]
            nv_list = ['Tất cả NVKD'] + sorted([x for x in df_nv_scope['NV_KD'].unique() if str(x) not in ['', 'nan', 'Chưa phân loại']])
            nv_sel = st.selectbox("👤 Nhân Viên KD", nv_list)

        df_base = df.copy()

        if bp_sel != 'Tất cả bộ phận':
            df_base = df_base[df_base['Bo_Phan_KD'] == bp_sel]
        if nv_sel != 'Tất cả NVKD':
            df_base = df_base[df_base['NV_KD'] == nv_sel]

        nam_eff = 2026 if nam_sel == 'Tất cả các năm' else int(nam_sel)
        
        if ky_sel == "Theo Tháng" and thang_sel:
            start_date = pd.Timestamp(year=nam_eff, month=thang_sel, day=1)
            end_date = start_date + pd.offsets.MonthEnd(1)
            ten_ky_hien_thi = f"Tháng {thang_sel}/{nam_eff}"
        elif ky_sel == "Theo Quý" and quy_sel:
            start_month = (quy_sel - 1) * 3 + 1
            start_date = pd.Timestamp(year=nam_eff, month=start_month, day=1)
            end_date = start_date + pd.DateOffset(months=3) - pd.Timedelta(days=1)
            ten_ky_hien_thi = f"Quý {quy_sel}/{nam_eff}"
        else:
            start_date = pd.Timestamp(year=nam_eff, month=1, day=1)
            end_date = pd.Timestamp(year=nam_eff, month=12, day=31)
            ten_ky_hien_thi = f"Năm {nam_eff}"

        # LỌC DỮ LIỆU
        cond_dat_moi = (df_base['Ngay_DatHang_DT'] >= start_date) & (df_base['Ngay_DatHang_DT'] <= end_date)
        df_moi = df_base[cond_dat_moi].copy()

        cond_dat_truoc = (df_base['Ngay_DatHang_DT'] < start_date)
        cond_chua_nk_truoc_ky = (~df_base['Da_Nhap_Kho']) | (df_base['Ngay_NK_Check'] >= start_date)
        df_ton = df_base[cond_dat_truoc & cond_chua_nk_truoc_ky].copy()

        cond_nhap_kho_trong_ky = (df_base['Ngay_NK_Check'] >= start_date) & (df_base['Ngay_NK_Check'] <= end_date)
        df_done = df_base[cond_nhap_kho_trong_ky].copy()

        if tt_sel != 'Tất cả tình trạng':
            df_moi = df_moi[df_moi['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
            df_ton = df_ton[df_ton['Trang_Thai_SX'].str.lower() == tt_sel.lower()]
            df_done = df_done[df_done['Trang_Thai_SX'].str.lower() == tt_sel.lower()]

        st.markdown("<br>", unsafe_allow_html=True)

        # TAB DANH MỤC CÓ KHUNG KHUNG BAO VÀ CHỮ IN ĐẬM RÕ NÉT
        tab_names = ['📊 Dashboard Tổng', '📦 Gối Chậu', '⚙️ Khe Răng Lược', '🧱 Tấm VCO', '🏗️ Cột H (Phụ Kiện)', '📋 Sản Phẩm Khác']
        tabs = st.tabs(tab_names)

        qty_mapping = {
            '📦 Gối Chậu': 'SL_GoiChau',
            '⚙️ Khe Răng Lược': 'SL_KheRangLuoc',
            '🧱 Tấm VCO': 'SL_TamVCO',
            '🏗️ Cột H (Phụ Kiện)': 'SL_HeCotPhuKien',
            '📋 Sản Phẩm Khác': 'SL_NhomKhac'
        }

        for i, tname in enumerate(tab_names):
            with tabs[i]:
                if tname == '📊 Dashboard Tổng':
                    q_col = 'So_Luong_Tong_DH'
                    sub_moi, sub_ton, sub_done = df_moi.copy(), df_ton.copy(), df_done.copy()
                else:
                    q_col = qty_mapping[tname]
                    sub_moi = df_moi[df_moi[q_col] > 0].copy()
                    sub_ton = df_ton[df_ton[q_col] > 0].copy()
                    sub_done = df_done[df_done[q_col] > 0].copy()

                cols_display = [
                    'Bo_Phan_KD', 'NV_KD', 'Du_An', 'So_DH', 'Quy_Cach', 'DVT', q_col,
                    'Canh_Bao_Tien_Do', 'Trang_Thai_SX', 'Ngay_Duyet_AB', 'Ngay_KD_Can_AC', 'Ngay_Chot_AG'
                ]

                sl_dat_moi = sub_moi[q_col].sum()
                sl_ton_chuyen_sang = sub_ton[q_col].sum()
                sl_tong_can_sx = sl_dat_moi + sl_ton_chuyen_sang
                sl_da_nhap_kho = sub_done[q_col].sum()
                sl_con_lai = sl_tong_can_sx - sl_da_nhap_kho

                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric(f"📦 Đặt Mới {ten_ky_hien_thi}", f"{sl_dat_moi:,.2f}")
                m2.metric(f"⏳ Tồn Lũy Kế Chuyển Sang", f"{sl_ton_chuyen_sang:,.2f}")
                m3.metric("🎯 Tổng Cần Sản Xuất", f"{sl_tong_can_sx:,.2f}")
                m4.metric(f"✅ Nhập Kho {ten_ky_hien_thi}", f"{sl_da_nhap_kho:,.2f}")
                m5.metric("⚠️ Còn Phải SX", f"{sl_con_lai:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)
                
                col_search, col_export = st.columns([3, 1])
                with col_search:
                    search_kw = st.text_input(f"🔍 Tìm kiếm nhanh (Mã ĐH, Dự án, Quy cách...):", key=f"s_{i}")
                
                if search_kw:
                    sub_moi = sub_moi[sub_moi['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]
                    sub_ton = sub_ton[sub_ton['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]
                    sub_done = sub_done[sub_done['So_DH'].astype(str).str.contains(search_kw, case=False, na=False)]

                with col_export:
                    st.write("")
                    st.write("")
                    excel_data = convert_df_to_excel(sub_moi, sub_ton, sub_done, cols_display, ten_ky_hien_thi)
                    tab_clean = tname.replace('📊 ', '').replace('📦 ', '').replace('⚙️ ', '').replace('🧱 ', '').replace('🏗️ ', '').replace('📋 ', '')
                    st.download_button(
                        label=f"📥 Trích Excel ({tab_clean})",
                        data=excel_data,
                        file_name=f"Bao_Cao_{tab_clean}_{re.sub(r'[\/\\\?\*\:\[\]]', '-', ten_ky_hien_thi)}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"btn_ex_{i}"
                    )

                sub_tab1, sub_tab2, sub_tab3 = st.tabs([
                    f"🆕 Đơn Đặt Mới ({len(sub_moi)} dòng)", 
                    f"⌛ Đơn Tồn Quá Khứ Chuyển Sang ({len(sub_ton)} dòng)",
                    f"✅ Đơn Đã Nhập Kho Trong Kỳ ({len(sub_done)} dòng)"
                ])

                column_cfg = {
                    "Bo_Phan_KD": "Bộ Phận", 
                    "NV_KD": "NVKD", 
                    "Du_An": "Dự Án", 
                    "So_DH": "Mã ĐH",
                    "Quy_Cach": "Quy Cách", 
                    "DVT": "ĐVT",
                    q_col: st.column_config.NumberColumn("Số Lượng", format="%.2f"),
                    "Canh_Bao_Tien_Do": st.column_config.TextColumn("🚨 Cảnh Báo Tiến Độ", width="medium"),
                    "Trang_Thai_SX": "Trạng Thái",
                    "Ngay_Duyet_AB": st.column_config.DateColumn("Duyệt SX (AB)", format="DD/MM/YYYY"),
                    "Ngay_KD_Can_AC": st.column_config.DateColumn("KD Cần (AC)", format="DD/MM/YYYY"),
                    "Ngay_Chot_AG": st.column_config.DateColumn("Chốt SX (AG)", format="DD/MM/YYYY")
                }

                with sub_tab1:
                    st.dataframe(apply_style_safe(sub_moi[cols_display].style, style_canh_bao, subset=['Canh_Bao_Tien_Do']), column_config=column_cfg, use_container_width=True, hide_index=True)

                with sub_tab2:
                    st.dataframe(apply_style_safe(sub_ton[cols_display].style, style_canh_bao, subset=['Canh_Bao_Tien_Do']), column_config=column_cfg, use_container_width=True, hide_index=True)

                with sub_tab3:
                    st.dataframe(apply_style_safe(sub_done[cols_display].style, style_canh_bao, subset=['Canh_Bao_Tien_Do']), column_config=column_cfg, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Lỗi kết nối hoặc xử lý dữ liệu: {e}")

# CHẠY HÀM DASHBOARD
render_dashboard()
