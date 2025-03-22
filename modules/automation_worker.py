import time
import os
import urllib.parse
import random
import subprocess
import shutil
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
# Thêm thư viện cho việc xác định phiên bản Chromium
from packaging import version

# Google URL mặc định
GOOGLE_URL = "https://www.google.com"

# =============== DỮ LIỆU TÀI KHOẢN XÃ HỘI ===============
# Tất cả MXH (facebook, instagram, zalo, twitter, shopee)
# Shopee => phone="aa", password="aa"
SOCIAL_ACCOUNTS = {
    "facebook": {
        "url": "https://www.facebook.com",
        "phone": "0333",
        "password": "123"
    },
    "instagram": {
        "url": "https://www.instagram.com/accounts/login",
        "phone": "0333",
        "password": "123"
    },
    "zalo": {
        "url": "https://chat.zalo.me/",
        "phone": "0333",
        "password": "123"
    },
    "twitter": {
        "url": "https://twitter.com/i/flow/login",
        "phone": "0333",
        "password": "123"
    },
    "shopee": {
        "url": "https://shopee.vn/buyer/login",
        "phone": "0333",
        "password": "123"
    }
}

class EnhancedAutomationWorker(QThread):
    """Enhanced worker class for automation tasks"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    result_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(bool)

    def __init__(self, task=None, keyword="", email="", password="", max_results=10,
                 headless=False, proxy=None, delay=0.0, pages=1, chrome_config=None):
        super().__init__()
        self.task = task
        self.keyword = keyword
        self.email = email
        self.password = password
        self.max_results = max_results
        self.headless = headless
        self.proxy = proxy
        self.delay = delay
        self.pages = pages
        self.chrome_config = chrome_config or {}
        self.running = False
        self.driver = None
        self.service = None

    def setup_driver(self):
        """Setup Brave driver with advanced options"""
        try:
            # Kiểm tra đường dẫn Brave
            brave_path = self.chrome_config.get("chrome_path")
            if not brave_path or not os.path.exists(brave_path):
                raise Exception(f"Không tìm thấy Brave tại: {brave_path}")

            options = Options()
            
            # Thiết lập đường dẫn Brave
            options.binary_location = brave_path
            
            # Thiết lập profile
            if self.chrome_config.get("profile_path"):
                user_data_dir = os.path.dirname(self.chrome_config['profile_path'])
                profile_dir = os.path.basename(self.chrome_config['profile_path'])
                
                if not os.path.exists(user_data_dir):
                    os.makedirs(user_data_dir, exist_ok=True)
                    
                options.add_argument(f"--user-data-dir={user_data_dir}")
                options.add_argument(f"--profile-directory={profile_dir}")

            # Thêm các tham số đặc biệt cho Brave
            for arg in self.chrome_config.get("brave_specific_args", []):
                options.add_argument(arg)

            # Thêm các tùy chọn bổ sung
            if self.headless:
                options.add_argument("--headless=new")
            
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')

            # Thêm các tham số để tránh phát hiện automation
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            # Khởi tạo driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Thiết lập timeout mặc định
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Tối đa hóa cửa sổ
            self.driver.maximize_window()
            
            # Kiểm tra xem driver có hoạt động không
            self.driver.current_window_handle
            
            self.log_signal.emit("✅ Khởi tạo trình duyệt thành công")
            return True
            
        except Exception as e:
            self.log_signal.emit(f"❌ Lỗi khởi tạo trình duyệt: {str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return False

    def stop(self):
        """Stop the worker thread"""
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        if self.service:
            try:
                self.service.stop()
            except:
                pass

    def run(self):
        """Main execution method"""
        try:
            # Kiểm tra xem có task và keyword không
            if not self.task:
                self.error_signal.emit("Chưa chọn task để thực hiện")
                return
                
            if self.task == "google" and not self.keyword:
                self.error_signal.emit("Chưa nhập từ khóa tìm kiếm")
                return
                
            # Bắt đầu chạy
            self.running = True
            self.progress_signal.emit(0)

            if self.task == "google":
                self.google_search()
            elif self.task == "facebook":
                self.facebook_login()
            elif self.task == "shopee":
                self.shopee_scrape()
            else:
                raise ValueError(f"Unknown task: {self.task}")
                
        except Exception as e:
            self.log_signal.emit(f"❌ Lỗi: {str(e)}")
            self.error_signal.emit(str(e))
        finally:
            self.running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.finished_signal.emit(True)

    def google_search(self):
        """Perform a Google search using Brave"""
        if not self.setup_driver():
            self.error_signal.emit("Không thể khởi tạo driver")
            return

        try:
            self.log_signal.emit("🔍 Bắt đầu tìm kiếm...")
            self.progress_signal.emit(10)

            # Truy cập Google
            self.driver.get(GOOGLE_URL)
            self.progress_signal.emit(30)
            self.log_signal.emit("Đã mở Google")

            # Chờ và nhập từ khóa tìm kiếm
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(self.keyword)
            self.log_signal.emit(f"Đã nhập từ khóa: {self.keyword}")
            self.progress_signal.emit(50)

            # Submit tìm kiếm
            search_box.submit()
            self.log_signal.emit("Đã gửi yêu cầu tìm kiếm")
            self.progress_signal.emit(70)

            # Chờ kết quả và thu thập
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            self.log_signal.emit("Đã nhận được kết quả")

            results = []
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            # Nếu không tìm thấy kết quả với CSS selector cũ, thử selector mới
            if not elements:
                elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'g')]")

            # Thu thập kết quả
            count = 0
            for element in elements:
                if count >= self.max_results:
                    break
                    
                try:
                    # Tìm tiêu đề và link
                    title_element = element.find_element(By.CSS_SELECTOR, "h3")
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    
                    title = title_element.text
                    url = link_element.get_attribute("href")
                    
                    if title and url:
                        results.append((title, url))
                        count += 1
                        self.log_signal.emit(f"✅ Đã tìm thấy: {title}")
                except:
                    continue

            self.progress_signal.emit(90)
            self.log_signal.emit(f"✅ Đã tìm thấy {len(results)} kết quả")
            
            # Gửi kết quả
            self.result_signal.emit(results)
            self.progress_signal.emit(100)
            return True

        except Exception as e:
            self.error_signal.emit(f"Lỗi khi tìm kiếm: {str(e)}")
            return False

    def facebook_login(self):
        """Login to Facebook using Brave"""
        if not self.setup_driver():
            self.error_signal.emit("Không thể khởi tạo driver")
            return False

        try:
            self.log_signal.emit("🌐 Đang truy cập Facebook...")
            self.progress_signal.emit(10)
            
            # Truy cập Facebook
            self.driver.get(SOCIAL_ACCOUNTS["facebook"]["url"])
            self.progress_signal.emit(30)
            
            # Chờ form đăng nhập
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Nhập thông tin đăng nhập
            email_field = self.driver.find_element(By.ID, "email")
            pass_field = self.driver.find_element(By.ID, "pass")
            
            email_field.clear()
            email_field.send_keys(self.email)
            self.log_signal.emit("📧 Đã nhập email")
            
            pass_field.clear()
            pass_field.send_keys(self.password)
            self.log_signal.emit("🔑 Đã nhập mật khẩu")
            
            self.progress_signal.emit(50)
            
            # Click nút đăng nhập
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            self.log_signal.emit("🔄 Đang đăng nhập...")
            
            # Chờ đăng nhập thành công
            time.sleep(5)  # Chờ cho quá trình đăng nhập hoàn tất
            
            # Kiểm tra đăng nhập thành công
            if "checkpoint" in self.driver.current_url:
                self.error_signal.emit("Tài khoản yêu cầu xác minh bảo mật")
                return False
                
            if "login" in self.driver.current_url:
                self.error_signal.emit("Đăng nhập thất bại - Kiểm tra lại thông tin")
                return False
                
            self.progress_signal.emit(80)
            self.log_signal.emit("✅ Đăng nhập thành công!")
            
            # Lưu thông tin phiên đăng nhập
            result = {
                "status": "success",
                "message": "Đăng nhập thành công",
                "url": self.driver.current_url
            }
            
            self.result_signal.emit(result)
            self.progress_signal.emit(100)
            return True
            
        except Exception as e:
            self.error_signal.emit(f"Lỗi đăng nhập: {str(e)}")
            return False

    def facebook_post(self, content, images=None):
        """Post content to Facebook"""
        if not self.driver:
            self.error_signal.emit("Chưa đăng nhập Facebook")
            return False
            
        try:
            self.log_signal.emit("📝 Chuẩn bị đăng bài...")
            self.progress_signal.emit(10)
            
            # Truy cập trang chủ Facebook
            self.driver.get(SOCIAL_ACCOUNTS["facebook"]["url"])
            self.progress_signal.emit(20)
            
            # Chờ và click vào ô "Bạn đang nghĩ gì?"
            create_post_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Tạo bài viết'], [aria-label='Create post']"))
            )
            create_post_button.click()
            
            self.log_signal.emit("✍️ Đang mở form đăng bài...")
            self.progress_signal.emit(40)
            
            # Chờ form đăng bài xuất hiện
            post_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Bạn đang nghĩ gì?'], [aria-label='What\\'s on your mind?'], [contenteditable='true']"))
            )
            
            # Nhập nội dung bài viết
            self.driver.execute_script("arguments[0].innerHTML = arguments[1]", post_box, content)
            self.log_signal.emit("📝 Đã nhập nội dung bài viết")
            self.progress_signal.emit(60)
            
            # Thêm ảnh nếu có
            if images:
                try:
                    # Click nút thêm ảnh
                    photo_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Photo/video']")
                    photo_button.click()
                    
                    # Chờ input file xuất hiện
                    file_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                    )
                    
                    # Upload từng ảnh
                    for image in images:
                        if os.path.exists(image):
                            file_input.send_keys(image)
                            time.sleep(2)  # Chờ upload
                            
                    self.log_signal.emit("🖼️ Đã thêm ảnh vào bài viết")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Không thể thêm ảnh: {str(e)}")
            
            self.progress_signal.emit(80)
            
            # Click nút Đăng
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Đăng'], [aria-label='Post']"))
            )
            post_button.click()
            
            self.log_signal.emit("🔄 Đang đăng bài...")
            
            # Chờ đăng bài thành công
            time.sleep(5)
            
            # Kiểm tra đăng bài thành công
            success = False
            try:
                success_msg = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'đã được đăng') or contains(text(), 'was posted')]"))
                )
                if success_msg:
                    success = True
            except:
                pass
                
            if success:
                self.log_signal.emit("✅ Đăng bài thành công!")
                result = {
                    "status": "success",
                    "message": "Đăng bài thành công",
                    "url": self.driver.current_url
                }
                self.result_signal.emit(result)
                self.progress_signal.emit(100)
                return True
            else:
                self.error_signal.emit("Không thể xác nhận đăng bài thành công")
                return False
                
        except Exception as e:
            self.error_signal.emit(f"Lỗi khi đăng bài: {str(e)}")
            return False

    def shopee_scrape(self):
        """Scrape products from Shopee"""
        if not self.setup_driver():
            self.error_signal.emit("Không thể khởi tạo driver")
            return False
            
        try:
            self.log_signal.emit("🔍 Bắt đầu tìm kiếm trên Shopee...")
            self.progress_signal.emit(10)
            
            # Truy cập Shopee
            self.driver.get(SOCIAL_ACCOUNTS["shopee"]["url"])
            self.progress_signal.emit(20)
            
            # Đợi và đóng popup nếu có
            try:
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".shopee-popup__close-btn"))
                )
                close_button.click()
            except:
                pass
                
            # Chờ ô tìm kiếm
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".shopee-searchbar-input__input"))
            )
            
            # Nhập từ khóa tìm kiếm
            search_box.clear()
            search_box.send_keys(self.keyword)
            self.log_signal.emit(f"🔍 Đã nhập từ khóa: {self.keyword}")
            
            # Nhấn Enter để tìm kiếm
            search_box.send_keys(Keys.RETURN)
            self.progress_signal.emit(40)
            
            # Chờ kết quả tìm kiếm
            time.sleep(5)  # Chờ trang load
            
            results = []
            current_page = 1
            
            while current_page <= self.pages and len(results) < self.max_results:
                self.log_signal.emit(f"📄 Đang xử lý trang {current_page}/{self.pages}")
                
                # Chờ danh sách sản phẩm
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".shopee-search-item-result__items"))
                )
                
                # Thu thập sản phẩm
                items = self.driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
                
                for item in items:
                    if len(results) >= self.max_results:
                        break
                        
                    try:
                        # Lấy thông tin sản phẩm
                        name = item.find_element(By.CSS_SELECTOR, "._3GAFiR").text
                        price = item.find_element(By.CSS_SELECTOR, "._1xk7ak").text
                        url = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        
                        if name and price and url:
                            results.append((name, price, url))
                            self.log_signal.emit(f"✅ Đã tìm thấy: {name}")
                    except:
                        continue
                        
                self.progress_signal.emit(40 + (50 * current_page // self.pages))
                
                # Chuyển trang nếu cần
                if current_page < self.pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".shopee-mini-page-controller__next-btn")
                        if "disabled" not in next_button.get_attribute("class"):
                            next_button.click()
                            time.sleep(3)  # Chờ trang mới load
                            current_page += 1
                        else:
                            break
                    except:
                        break
                else:
                    break
                    
            self.log_signal.emit(f"✅ Đã tìm thấy {len(results)} sản phẩm")
            
            # Gửi kết quả
            self.result_signal.emit(results)
            self.progress_signal.emit(100)
            return True
            
        except Exception as e:
            self.error_signal.emit(f"Lỗi khi tìm kiếm trên Shopee: {str(e)}")
            return False
