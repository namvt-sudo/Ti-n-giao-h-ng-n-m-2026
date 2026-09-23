import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

# 1. CẤU HÌNH TRANG WEB & CSS
st.set_page_config(
    page_title="VHIP - Quản Lý Tiến Độ & Sản Lượng",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
