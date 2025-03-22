# config.py

import os
import sys
from pathlib import Path
from PyQt5.QtCore import QSettings

# Đường dẫn cơ sở
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Các thư mục quan trọng
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
BROWSER_PROFILES_DIR = os.path.join(BASE_DIR, "browser_profiles")

# Tạo các thư mục nếu chưa tồn tại
for directory in [RESOURCES_DIR, ICONS_DIR, LOGS_DIR, DATA_DIR, SCRIPTS_DIR, DOWNLOADS_DIR, BROWSER_PROFILES_DIR]:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Đã tạo/kiểm tra thư mục: {directory}")
    except Exception as e:
        print(f"✗ Lỗi khi tạo thư mục {directory}: {e}")

# Icon ứng dụng - thử dùng app_icon.png, nếu không có thì dùng automation.png
APP_ICON = os.path.join(ICONS_DIR, "app_icon.png")
if not os.path.exists(APP_ICON):
    APP_ICON = os.path.join(ICONS_DIR, "automation.png")
    print(f"! Không tìm thấy app_icon.png, sử dụng automation.png")

# Brave configuration
BRAVE_PATHS = {
    'win32': {
        'browser': r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        'profile': os.path.join(BROWSER_PROFILES_DIR, "brave_profile")
    },
    'linux': {
        'browser': '/usr/bin/brave-browser',
        'profile': os.path.join(BROWSER_PROFILES_DIR, "brave_profile")
    },
    'darwin': {
        'browser': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
        'profile': os.path.join(BROWSER_PROFILES_DIR, "brave_profile")
    }
}

# Lấy đường dẫn Brave theo hệ điều hành
BRAVE_PATH = os.path.normpath(BRAVE_PATHS.get(sys.platform, BRAVE_PATHS['win32'])['browser'])
BRAVE_PROFILE_PATH = os.path.normpath(BRAVE_PATHS.get(sys.platform, BRAVE_PATHS['win32'])['profile'])

# Tạo thư mục profile nếu chưa tồn tại
os.makedirs(BRAVE_PROFILE_PATH, exist_ok=True)

# Kiểm tra và log đường dẫn
print(f"Brave path: {BRAVE_PATH}")
print(f"Profile path: {BRAVE_PROFILE_PATH}")

# Validate Brave installation
if not os.path.exists(BRAVE_PATH):
    print(f"WARNING: Brave not found at {BRAVE_PATH}")
    # Try to find Brave in Program Files
    program_files = os.environ.get("ProgramFiles")
    if program_files:
        alt_path = os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")
        if os.path.exists(alt_path):
            BRAVE_PATH = alt_path
            print(f"Found Brave at alternate location: {BRAVE_PATH}")

# Brave options
BRAVE_OPTIONS = {
    "start_maximized": True,
    "disable_gpu": False,
    "no_sandbox": False,
    "disable_dev_shm_usage": True,
    "disable_extensions": False,
    "disable_notifications": True,
    "disable_infobars": True,
    "ignore_certificate_errors": True,
    "user_data_dir": BRAVE_PROFILE_PATH,
    "profile_directory": "Default",
    "brave_specific_args": [
        "--disable-domain-reliability",
        "--enable-dom-distiller",
        "--enable-distillability-service",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-notifications",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-sync",
        "--metrics-recording-only",
        "--no-default-browser-check",
        "--no-first-run",
        "--password-store=basic",
        "--use-mock-keychain"
    ]
}

# Save paths to settings
settings = QSettings("MyApp", "AutomationWidget")
settings.setValue("brave_path", BRAVE_PATH)
settings.setValue("brave_profile", BRAVE_PROFILE_PATH)

# Theme configuration
THEMES = {
    'Light': {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'text_primary': '#000000',
        'text_secondary': '#666666',
        'accent': '#1a73e8',
        'accent_hover': '#1557b0',
        'border': '#e0e0e0',
        'success': '#0f9d58',
        'warning': '#f4b400',
        'error': '#db4437'
    },
    'Dark': {
        'bg_primary': '#202124',
        'bg_secondary': '#292a2d',
        'text_primary': '#e8eaed',
        'text_secondary': '#9aa0a6',
        'accent': '#8ab4f8',
        'accent_hover': '#93c5fd',
        'border': '#3c4043',
        'success': '#81c995',
        'warning': '#fdd663',
        'error': '#f28b82'
    }
}

DEFAULT_THEME = 'Light'

# Application settings
APP_NAME = "Selenium Automation Hub"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "GDU"
WINDOW_SIZE = (1200, 800)  # Default window size

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'

# Cấu hình ứng dụng
APP_TITLE = "Selenium Automation Hub"
APP_WIDTH = 1200
APP_HEIGHT = 800
APP_VERSION = "2.0.0"

# Theme mặc định
DEFAULT_RETRY = 3
DEFAULT_TIMEOUT = 30

# Định nghĩa màu sắc chung cho giao diện
COLORS = {
    "primary": "#0d6efd",
    "primary_hover": "#0b5ed7",
    "primary_active": "#0a58ca",
    "dark_bg": "#2b2b2b",
    "dark_bg_secondary": "#363636",
    "light_bg": "#f8f9fa",
    "light_bg_secondary": "#e9ecef",
    "dark_text": "#212529",
    "light_text": "#ffffff",
    "border_dark": "#555555",
    "border_light": "#ced4da",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
}

# URL của các trang web
GOOGLE_URL = "https://www.google.com"
FACEBOOK_URL = "https://www.facebook.com"
SHOPEE_SEARCH_URL = "https://shopee.vn/search?keyword=your_search_keyword"

# Thông tin đăng nhập (nên sử dụng biến môi trường cho bảo mật thực tế)
FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL", "your_email@example.com")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD", "your_password")

# Cài đặt nâng cao
ENABLE_HEADLESS = os.getenv("ENABLE_HEADLESS", "True").lower() == "true"
ENABLE_STEALTH_MODE = os.getenv("ENABLE_STEALTH_MODE", "True").lower() == "true"
ENABLE_PROXY_ROTATION = os.getenv("ENABLE_PROXY_ROTATION", "False").lower() == "true"
CAPTCHA_SERVICE = os.getenv("CAPTCHA_SERVICE", "manual")  # 'manual', '2captcha', 'anticaptcha', 'auto'
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY", "")

# Tạo các thư mục cần thiết
for directory in [DATA_DIR, SCRIPTS_DIR, LOGS_DIR, DOWNLOADS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Danh sách User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

# Thêm cấu hình cho chế độ headless
HEADLESS_OPTIONS = {
    "headless": True,
    "disable_gpu": True,
    "no_sandbox": True,
    "disable_dev_shm_usage": True,
    "window-size": "1920,1080"
}
