import sys
import os
import logging
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings
import datetime

# Thiết lập đường dẫn cơ sở
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import cấu hình
from modules.config import (
    APP_NAME, APP_VERSION, ORGANIZATION_NAME, 
    LOGS_DIR, APP_ICON, LOG_FORMAT, LOG_DATE_FORMAT,
    BRAVE_PATH, BRAVE_PROFILE_PATH, BRAVE_OPTIONS
)

def setup_logging():
    """Thiết lập logging cho ứng dụng"""
    try:
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
            
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(LOGS_DIR, f'app_{today}.log')
        
        # Cấu hình logging
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Điều chỉnh level cho các logger cụ thể
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('webdriver_manager').setLevel(logging.INFO)
        
        return logging.getLogger()
    except Exception as e:
        print(f"Lỗi khi thiết lập logging: {e}")
        return None

def main():
    """Hàm chính khởi chạy ứng dụng"""
    try:
        # Thiết lập logging
        logger = setup_logging()
        if not logger:
            print("Không thể thiết lập logging, thoát ứng dụng")
            return
            
        logger.info("=== KHỞI ĐỘNG ỨNG DỤNG SELENIUM AUTOMATION HUB ===")
        
        # Import các module cần thiết
        try:
            from modules.main_window import MainWindow
            from modules.automation_worker import EnhancedAutomationWorker
            logger.info("Đã import thành công các module cần thiết")
        except ImportError as e:
            logger.error(f"Lỗi khi import module: {e}")
            traceback.print_exc()
            return
            
        # Khởi tạo ứng dụng Qt
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName(ORGANIZATION_NAME)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        app.setStyle("Fusion")
        
        # Thiết lập icon cho ứng dụng
        if os.path.exists(APP_ICON):
            from PyQt5.QtGui import QIcon
            app.setWindowIcon(QIcon(APP_ICON))
            logger.info(f"Đã thiết lập icon ứng dụng từ: {APP_ICON}")  
        else:
            logger.warning(f"Không tìm thấy icon tại: {APP_ICON}")
            
        # Khởi tạo và hiển thị cửa sổ chính
        main_window = MainWindow()
        main_window.show()
        logger.info("Giao diện ứng dụng đã được khởi động thành công")
        
        # Chạy event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
    
    