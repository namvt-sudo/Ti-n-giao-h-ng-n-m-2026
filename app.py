# 1. CẤU HÌNH TRANG WEB & CSS
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# THÊM ĐOẠN JAVASCRIPT ĐỂ TÌM VÀ XÓA NÚT MANAGE APP & AVATAR
import streamlit.components.v1 as components
components.html("""
<script>
function removeManageApp() {
    try {
        const doc = window.parent.document;
        // Quét và xóa nút Manage app, avatar và các container ở góc dưới
        const selectors = [
            '[data-testid="manage-app-button"]',
            'div[class*="viewerBadge"]',
            'div[class*="manageApp"]',
            'div[class*="ProfileButton"]',
            'footer',
            'header[data-testid="stHeader"]'
        ];
        selectors.forEach(sel => {
            const elements = doc.querySelectorAll(sel);
            elements.forEach(el => el.remove());
        });
    } catch (e) {}
}
// Chạy lặp lại trong vài giây đầu khi trang tải để đảm bảo xóa sạch
setInterval(removeManageApp, 300);
</script>
""", height=0, width=0)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ẨN HEADER VÀ NÚT MANAGE APP / AVATAR Ở MỌI CẤP ĐỘ */
    header[data-testid="stHeader"],
    #MainMenu,
    .stAppDeployButton,
    footer,
    [data-testid="manage-app-button"],
    div[class*="viewerBadge"],
    div[class*="manageApp"],
    div[class*="ProfileButton"],
    div[data-testid="stStatusWidget"],
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_ {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Đẩy nội dung lên trên để che khuất hoàn toàn thanh viền nếu có */
    .stApp {
        background: linear-gradient(180deg, #eef4ff 0%, #f7faff 35%, #ffffff 100%);
    }
    /* ... (giữ nguyên các phần CSS còn lại) */
""", unsafe_allow_html=True)
