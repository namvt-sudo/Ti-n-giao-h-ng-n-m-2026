import streamlit as st
import streamlit_authenticator as stauth
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 1. KẾT NỐI GOOGLE SHEET AN TOÀN QUA SERVICE ACCOUNT (KHÔNG CÔNG KHAI LINK)
@st.cache_data(ttl=180)
def load_data_secure():
    # Lấy thông tin xác thực từ secrets.toml
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Mở sheet bằng Key (Lưu ý: Sheet để chế độ RIÊNG TƯ, chỉ share cho email của service account)
    sheet = client.open_by_key(st.secrets["sheet_id"]).worksheet("DATA")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[3:], columns=data[2]) # Lấy từ dòng header
    return df

# 2. CẤU HÌNH DANH SÁCH ĐĂNG NHẬP (Lấy từ secrets.toml hoặc sheet bảo mật)
# Mỗi nhân viên có tài khoản riêng, mật khẩu đã được BĂM (hash)
credentials = {
    "usernames": {
        "nv_bien": {
            "name": "Nguyễn Văn Biên",
            "password": st.secrets["passwords"]["nv_bien"], # Chuỗi $2b$12$...
            "email": "bien@vinhhung.com.vn",
            "role": "kinh_doanh"
        },
        "giam_doc": {
            "name": "Ban Giám Đốc",
            "password": st.secrets["passwords"]["giam_doc"],
            "email": "gd@vinhhung.com.vn",
            "role": "admin"
        }
    }
}

# Khởi tạo bộ xác thực bảo mật
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=st.secrets["auth"]["cookie_name"],
    key=st.secrets["auth"]["cookie_key"], # Khóa bí mật dùng để mã hóa cookie phiên làm việc
    cookie_expiry_days=1 # Hết hạn đăng nhập sau 1 ngày
)

# 3. HIỂN THỊ MÀN HÌNH ĐĂNG NHẬP
authenticator.login()

if st.session_state["authentication_status"]:
    # Đã đăng nhập thành công
    user_name = st.session_state["name"]
    user_role = credentials["usernames"][st.session_state["username"]]["role"]
    
    col_info, col_out = st.columns([5, 1])
    with col_info:
        st.write(f"Xin chào: **{user_name}** | Quyền hạn: `{user_role}`")
    with col_out:
        authenticator.logout('Đăng Xuất', 'main')

    # ================= KHÔNG GIAN DỮ LIỆU ĐƯỢC PHÂN QUYỀN =================
    df = load_data_secure()

    # Phân quyền dòng: Nếu là NVKD thì chỉ lọc ra các đơn của chính mình
    if user_role == "kinh_doanh":
        df_hien_thi = df[df['NV_KD_ChuanHoa'] == user_name]
    else:
        df_hien_thi = df # Giám đốc / Quản lý xem toàn bộ

    # Gọi hàm vẽ Dashboard...
    # render_dashboard(df_hien_thi)

elif st.session_state["authentication_status"] is False:
    st.error('Tên đăng nhập hoặc mật khẩu không chính xác.')
elif st.session_state["authentication_status"] is None:
    st.warning('Vui lòng đăng nhập để tiếp tục.')
