# modules/main_window.py

# Standard library imports
import os
import sys
import logging
import traceback
from datetime import datetime, timedelta

# PyQt5 imports
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QProgressBar, QMessageBox, QPushButton,
    QLabel, QApplication, QMenu, QAction
)
from PyQt5.QtCore import QSettings, QTimer, Qt, QDateTime
from PyQt5.QtGui import QIcon, QFont

# Third-party imports
import qdarkstyle

# Local imports
from .dashboard import DashboardWidget
from .automation_view import AutomationView
from .data_view import DataWidget
from .logs_view import LogsWidget
from .script_manager import ScriptManagerWidget
from .proxy_manager import ProxyManagerWidget
from .task_scheduler import TaskSchedulerWidget

# Constants
APP_NAME = "Selenium Automation Hub"
ORGANIZATION_NAME = "AutomationHub"

# Import các module UI con
try:
    from .splash_screen import SplashScreen
    from .settings_dialog import SettingsDialog
    from .captcha_resolver import CaptchaResolver
    from .script_builder import ScriptBuilderWidget
except ImportError as e:
    logging.error(f"Lỗi import module: {e}")
    raise

# Import config
from .config import (
    APP_VERSION, APP_ICON,
    WINDOW_SIZE, THEMES, DEFAULT_THEME, RESOURCES_DIR
)
from .utils import setup_logging

# Tạo logger
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        try:
            # Initialize settings
            self.settings = QSettings('AutomationHub', 'SeleniumAutomationHub')
            
            # Set window properties
            self.setWindowTitle("Selenium Automation Hub")
            self.setWindowIcon(QIcon("resources/icons/automation.png"))
            
            # Restore window geometry and state
            if self.settings.contains('window_geometry'):
                self.restoreGeometry(self.settings.value('window_geometry'))
            if self.settings.contains('window_state'):
                self.restoreState(self.settings.value('window_state'))
            
            # Initialize UI components
            self.init_ui()
            self.init_menu()
            self.init_statusbar()
            
            # Initialize automation worker
            if not self.init_automation_worker():
                raise Exception("Không thể khởi tạo automation worker")
            
            # Show splash screen
            self.init_splash_screen()
            
            # Apply theme
            current_theme = self.settings.value('theme', 'light')
            if current_theme == 'dark':
                self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
            
            # Restore last page
            if self.settings.contains('current_page'):
                last_page = self.settings.value('current_page', 0, type=int)
                if 0 <= last_page < self.stacked_widget.count():
                    self.stacked_widget.setCurrentIndex(last_page)
            
            self.log_info("🚀 Application initialized successfully")
            
        except Exception as e:
            self.log_error(f"Error initializing main window: {str(e)}")
            traceback.print_exc()

    def init_logging(self):
        setup_logging()

    def init_ui(self):
        """Initialize application user interface"""
        try:
            # Create main container widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # Create stacked widget for pages
            self.stacked_widget = QStackedWidget()
            
            # Initialize page widgets
            self.dashboard_page = DashboardWidget()       # index 0
            self.automation_page = AutomationView()       # index 1
            self.data_page = DataWidget()                # index 2
            self.logs_page = LogsWidget()                # index 3
            self.script_manager_page = ScriptManagerWidget()   # index 4
            self.proxy_manager_page = ProxyManagerWidget()      # index 5
            self.task_scheduler_page = TaskSchedulerWidget()    # index 6
            
            # Add pages to stacked widget
            self.stacked_widget.addWidget(self.dashboard_page)
            self.stacked_widget.addWidget(self.automation_page)
            self.stacked_widget.addWidget(self.data_page)
            self.stacked_widget.addWidget(self.logs_page)
            self.stacked_widget.addWidget(self.script_manager_page)
            self.stacked_widget.addWidget(self.proxy_manager_page)
            self.stacked_widget.addWidget(self.task_scheduler_page)
            
            # Add stacked widget to main layout
            layout.addWidget(self.stacked_widget)
            
            # Create progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)
            
            self.log_info("🎨 User interface initialized")
            
        except Exception as e:
            self.log_error(f"Error initializing user interface: {str(e)}")
            traceback.print_exc()

    def init_menu(self):
        """Initialize application menu bar"""
        try:
            # Create menu bar
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu("File")
            exit_action = QAction(QIcon("resources/icons/exit.png"), "Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # View menu
            view_menu = menubar.addMenu("View")
            
            # Dashboard action
            dashboard_action = QAction(QIcon("resources/icons/dashboard.png"), "Dashboard", self)
            dashboard_action.setObjectName("dashboard_action")
            dashboard_action.triggered.connect(lambda: self.switch_page('dashboard'))
            view_menu.addAction(dashboard_action)
            
            # Automation action
            automation_action = QAction(QIcon("resources/icons/automation.png"), "Automation", self)
            automation_action.setObjectName("automation_action")
            automation_action.triggered.connect(lambda: self.switch_page('automation'))
            view_menu.addAction(automation_action)
            
            # Data action
            data_action = QAction(QIcon("resources/icons/data.png"), "Data", self)
            data_action.setObjectName("data_action")
            data_action.triggered.connect(lambda: self.switch_page('data'))
            view_menu.addAction(data_action)
            
            # Logs action
            logs_action = QAction(QIcon("resources/icons/logs.png"), "Logs", self)
            logs_action.setObjectName("logs_action")
            logs_action.triggered.connect(lambda: self.switch_page('logs'))
            view_menu.addAction(logs_action)
            
            # Script Manager action
            script_manager_action = QAction(QIcon("resources/icons/script.png"), "Script Manager", self)
            script_manager_action.setObjectName("script_manager_action")
            script_manager_action.triggered.connect(lambda: self.switch_page('script_manager'))
            view_menu.addAction(script_manager_action)
            
            # Tools menu
            tools_menu = menubar.addMenu("Tools")
            
            # Proxy Manager action
            proxy_manager_action = QAction(QIcon("resources/icons/proxy.png"), "Proxy Manager", self)
            proxy_manager_action.triggered.connect(self.open_proxy_manager)
            tools_menu.addAction(proxy_manager_action)
            
            # Task Scheduler action
            task_scheduler_action = QAction(QIcon("resources/icons/scheduler.png"), "Task Scheduler", self)
            task_scheduler_action.triggered.connect(self.open_scheduler)
            tools_menu.addAction(task_scheduler_action)
            
            # Script Builder action
            script_builder_action = QAction(QIcon("resources/icons/builder.png"), "Script Builder", self)
            script_builder_action.triggered.connect(self.open_script_builder)
            tools_menu.addAction(script_builder_action)
            
            # Captcha Resolver action
            captcha_resolver_action = QAction(QIcon("resources/icons/captcha.png"), "Captcha Resolver", self)
            captcha_resolver_action.triggered.connect(self.open_captcha_resolver)
            tools_menu.addAction(captcha_resolver_action)
            
            # Settings menu
            settings_menu = menubar.addMenu("Settings")
            
            # Preferences action
            preferences_action = QAction(QIcon("resources/icons/settings.png"), "Preferences", self)
            preferences_action.triggered.connect(self.open_settings_dialog)
            settings_menu.addAction(preferences_action)
            
            # Theme toggle action
            theme_action = QAction(QIcon("resources/icons/theme.png"), "Toggle Theme", self)
            theme_action.triggered.connect(self.toggle_theme)
            settings_menu.addAction(theme_action)
            
            # Help menu
            help_menu = menubar.addMenu("Help")
            
            # About action
            about_action = QAction(QIcon("resources/icons/about.png"), "About", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            
            # Store menu actions as class attributes
            self.menu_actions = {
                'dashboard': dashboard_action,
                'automation': automation_action,
                'data': data_action,
                'logs': logs_action,
                'script_manager': script_manager_action,
                'proxy_manager': proxy_manager_action,
                'task_scheduler': task_scheduler_action,
                'script_builder': script_builder_action,
                'captcha_resolver': captcha_resolver_action,
                'preferences': preferences_action,
                'theme': theme_action,
                'about': about_action,
                'exit': exit_action
            }
            
            self.log_info("📋 Menu bar initialized")
            
        except Exception as e:
            self.log_error(f"Error initializing menu: {str(e)}")
            traceback.print_exc()

    def apply_theme(self, theme_name=None):
        """Áp dụng theme cho toàn bộ ứng dụng"""
        try:
            # Xác định theme hiện tại
            if theme_name:
                self.current_theme = theme_name
            elif not hasattr(self, 'current_theme'):
                self.current_theme = self.settings.value("theme", DEFAULT_THEME)
            
            # Lấy cấu hình theme
            theme = THEMES.get(self.current_theme, THEMES["Light"])
            
            # Style cơ bản cho toàn bộ ứng dụng
            base_style = f"""
                QMainWindow {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                }}
                QWidget {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                }}
                QLabel {{
                    color: {theme["text_primary"]};
                }}
                QPushButton {{
                    background-color: {theme["accent"]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: {theme["accent_hover"]};
                }}
                QMenuBar {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                    border-bottom: 1px solid {theme["border"]};
                }}
                QMenuBar::item:selected {{
                    background-color: {theme["bg_secondary"]};
                }}
                QMenu {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                    border: 1px solid {theme["border"]};
                }}
                QMenu::item:selected {{
                    background-color: {theme["bg_secondary"]};
                }}
                QTabWidget::pane {{
                    border: 1px solid {theme["border"]};
                    background-color: {theme["bg_secondary"]};
                }}
                QTabBar::tab {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                    border: 1px solid {theme["border"]};
                    padding: 5px 10px;
                    margin: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {theme["accent"]};
                    color: white;
                }}
                QStatusBar {{
                    background-color: {theme["bg_primary"]};
                    color: {theme["text_primary"]};
                    border-top: 1px solid {theme["border"]};
                }}
            """
            
            # Áp dụng style cơ bản
            self.setStyleSheet(base_style)
            
            # Cập nhật theme cho các widget con
            if hasattr(self, 'dashboard_page'):
                self.dashboard_page.apply_theme()
            if hasattr(self, 'automation_page'):
                self.automation_page.apply_theme()
            if hasattr(self, 'data_page'):
                self.data_page.apply_theme()
            if hasattr(self, 'logs_page'):
                self.logs_page.apply_theme()
            if hasattr(self, 'script_manager_page'):
                self.script_manager_page.apply_theme()
            if hasattr(self, 'proxy_manager_page'):
                self.proxy_manager_page.apply_theme()
            if hasattr(self, 'task_scheduler_page'):
                self.task_scheduler_page.apply_theme()
            
            # Lưu theme vào settings
            self.settings.setValue("theme", self.current_theme)
            self.settings.sync()
            
            # Log thành công
            logger.info(f"Đã áp dụng theme {self.current_theme}")
            
        except Exception as e:
            logger.error(f"Lỗi khi áp dụng theme: {str(e)}")
            traceback.print_exc()

    def init_splash_screen(self):
        """Initialize and show splash screen"""
        try:
            # Create and show splash screen
            splash = SplashScreen()
            splash.show()
            
            # Process events to ensure splash is displayed
            for _ in range(5):
                QApplication.processEvents()
                
            # Set up timer to close splash after delay
            QTimer.singleShot(1500, splash.close)
            
            self.log_info("🚀 Application splash screen initialized")
            
        except Exception as e:
            self.log_error(f"Error initializing splash screen: {str(e)}")
            traceback.print_exc()

    def log(self, message):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        print(f"[{now}] {message}")

    def open_settings_dialog(self):
        """Open application settings dialog"""
        try:
            dialog = SettingsDialog(self)
            if dialog.exec_() == dialog.Accepted:
                # Apply new settings
                self.load_settings()
                self.log_info("⚙️ Settings updated")
            else:
                self.log_info("Settings dialog cancelled")
                
        except Exception as e:
            self.log_error(f"Error opening Settings dialog: {str(e)}")
            traceback.print_exc()

    def show_about(self):
        """Show application about dialog"""
        try:
            about_text = f"""
            🚀 Selenium Automation Hub
            Version: {APP_VERSION}
            
            A powerful automation tool for web scraping and testing.
            Built with Python, PyQt5, and Selenium.
            
            Features:
            - Google Search Automation
            - Facebook Automation
            - Shopee Scraping
            - Custom Script Support
            - Proxy Management
            - Task Scheduling
            - Captcha Resolution
            
            © 2024 GDU. All rights reserved.
            """
            
            QMessageBox.about(self, "About Selenium Automation Hub", about_text.strip())
            self.log_info("ℹ️ Showed About dialog")
            
        except Exception as e:
            self.log_error(f"Error showing About dialog: {str(e)}")
            traceback.print_exc()

    def switch_page(self, page_name):
        """Switch to specified page in stacked widget"""
        try:
            # Map page names to indices
            page_indices = {
                'dashboard': 0,
                'automation': 1, 
                'data': 2,
                'logs': 3,
                'script_manager': 4,
                'proxy_manager': 5,
                'task_scheduler': 6
            }
            
            # Get page index from name
            if page_name.lower() in page_indices:
                index = page_indices[page_name.lower()]
                if 0 <= index < self.stacked_widget.count():
                    self.stacked_widget.setCurrentIndex(index)
                    self.log_info(f"📄 Switched to {page_name} page")
                else:
                    self.log_warning(f"Invalid page index: {index}")
            else:
                self.log_warning(f"Invalid page name: {page_name}")
                
        except Exception as e:
            self.log_error(f"Error switching page: {str(e)}")
            traceback.print_exc()

    def closeEvent(self, event):
        """Handle application closing event"""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, 
                'Confirm Exit',
                'Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Save window state and geometry
                self.settings.setValue('window_geometry', self.saveGeometry())
                self.settings.setValue('window_state', self.saveState())
                
                # Save current page
                current_index = self.stacked_widget.currentIndex()
                self.settings.setValue('current_page', current_index)
                
                # Clean up resources
                if hasattr(self, 'automation_page'):
                    self.automation_page.cleanup()
                
                self.log_info("👋 Application closed gracefully")
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            self.log_error(f"Error during application closing: {str(e)}")
            traceback.print_exc()
            event.accept()  # Accept the close event even if there's an error

    def open_script_builder(self):
        """Open the script builder dialog"""
        try:
            dialog = ScriptBuilderWidget(self)
            dialog.script_saved.connect(self.on_script_saved)
            dialog.exec_()
            self.log_info("📝 Opened Script Builder")
        except Exception as e:
            self.log_error(f"Error opening Script Builder: {str(e)}")
            traceback.print_exc()
            
    def open_captcha_resolver(self):
        """Open the captcha resolver dialog"""
        try:
            dialog = CaptchaResolver(self)
            dialog.exec_()
            self.log_info("🔑 Opened Captcha Resolver")
        except Exception as e:
            self.log_error(f"Error opening Captcha Resolver: {str(e)}")
            traceback.print_exc()

    def on_script_saved(self, script_name, script_content):
        """Handle saved script from script builder"""
        try:
            if not script_name or not script_content:
                self.log_warning("⚠️ Invalid script data")
                return
                
            # Save script to scripts directory
            script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
            if not os.path.exists(script_dir):
                os.makedirs(script_dir)
                
            script_path = os.path.join(script_dir, f"{script_name}.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
                
            self.log_info(f"💾 Script saved: {script_name}.py")
            
            # Refresh script manager if available
            if hasattr(self, 'script_manager_page'):
                if hasattr(self.script_manager_page, 'refresh_list'):
                    self.script_manager_page.refresh_list()
                    
        except Exception as e:
            self.log_error(f"Error saving script: {str(e)}")
            traceback.print_exc()

    def open_scheduler(self):
        """Open the task scheduler page"""
        try:
            if hasattr(self, 'task_scheduler_page'):
                self.switch_page('task_scheduler')
                self.log_info("📅 Opened Task Scheduler")
            else:
                self.log_warning("⚠️ Task Scheduler not available")
        except Exception as e:
            self.log_error(f"Error opening Task Scheduler: {str(e)}")
            traceback.print_exc()

    def open_proxy_manager(self):
        self.switch_page('proxy_manager')

    def on_proxies_updated(self, proxy_list):
        """Handle updated proxies from proxy manager"""
        try:
            # Update proxies in automation page
            if hasattr(self.automation_page, 'update_proxies'):
                self.automation_page.update_proxies(proxy_list)
                self.log(f"✅ Updated {len(proxy_list)} proxies in automation page")
        except Exception as e:
            self.log(f"❌ Error updating proxies: {str(e)}")

    def on_scheduled_task_ready(self, task_info):
        """Handle scheduled task execution"""
        try:
            if task_info and isinstance(task_info, dict):
                task_type = task_info.get('type', '')
                params = task_info.get('params', {})
                
                self.log_info(f"🕒 Executing scheduled {task_type} task")
                
                # Switch to automation page
                self.switch_page('automation')
                
                # Execute task based on type
                if hasattr(self, 'automation_page'):
                    self.automation_page.start_task(task_type, params)
                else:
                    self.log_warning("⚠️ Automation page not available")
                    
            else:
                self.log_warning("⚠️ Invalid task info format")
                
        except Exception as e:
            self.log_error(f"Error handling scheduled task: {str(e)}")
            traceback.print_exc()

    def connect_signals(self):
        """Connect all UI signals and worker signals"""
        try:
            # Connect automation page signals
            if hasattr(self, 'automation_page'):
                self.automation_page.log_signal.connect(self.log_info)
                self.automation_page.task_completed.connect(self.on_task_completed)
            
            # Connect logs page signals
            if hasattr(self, 'logs_page'):
                self.logs_page.log_signal.connect(self.log_info)
            
            # Connect dashboard signals
            if hasattr(self, 'dashboard_page'):
                self.dashboard_page.navigate_signal.connect(self.switch_page)
                if hasattr(self, 'automation_page'):
                    self.dashboard_page.get_trends_signal.connect(self.automation_page.run_google_trends)
                    self.dashboard_page.create_content_signal.connect(self.automation_page.run_content_creation)
                    self.dashboard_page.post_content_signal.connect(self.automation_page.run_post_content)
            
            # Connect proxy manager signals
            if hasattr(self, 'proxy_manager_page') and hasattr(self, 'automation_page'):
                self.proxy_manager_page.proxies_updated.connect(self.automation_page.update_proxies)
            
            # Connect script manager signals
            if hasattr(self, 'script_manager_page'):
                self.script_manager_page.script_selected.connect(self.on_script_selected)
                self.script_manager_page.run_script.connect(self.run_script)
            
            # Connect task scheduler signals
            if hasattr(self, 'task_scheduler_page'):
                self.task_scheduler_page.task_ready.connect(self.on_scheduled_task_ready)
            
            # Connect menu actions
            for action in self.menu_actions.values():
                action.triggered.connect(lambda: self.switch_page(action.objectName()))
            
            self.log_info("All signals connected successfully")
            
        except Exception as e:
            self.log_error(f"Error connecting signals: {str(e)}")
            traceback.print_exc()

    def init_statusbar(self):
        """Initialize application status bar"""
        try:
            # Create status bar
            self.statusBar().showMessage("Ready")
            
            # Create layout for status widgets
            status_layout = QHBoxLayout()
            status_layout.setContentsMargins(0, 0, 10, 0)
            
            # Create theme toggle button
            self.theme_toggle = QPushButton()
            self.theme_toggle.setToolTip("Toggle Light/Dark mode")
            self.theme_toggle.setFixedSize(24, 24)
            self.theme_toggle.setIcon(QIcon("resources/icons/theme.png"))
            self.theme_toggle.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                }
            """)
            self.theme_toggle.clicked.connect(self.toggle_theme)
            
            # Create version label
            version_label = QLabel(f"v{APP_VERSION}")
            
            # Add widgets to layout
            status_layout.addStretch()
            status_layout.addWidget(self.theme_toggle)
            status_layout.addWidget(version_label)
            
            # Create container widget for status items
            status_widget = QWidget()
            status_widget.setLayout(status_layout)
            
            # Add status widget to status bar
            self.statusBar().addPermanentWidget(status_widget)
            
            self.log_info("📊 Status bar initialized")
            
        except Exception as e:
            self.log_error(f"Error initializing status bar: {str(e)}")
            traceback.print_exc()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        try:
            # Get current theme from settings
            current_theme = self.settings.value('theme', 'light')
            
            # Toggle theme
            new_theme = 'dark' if current_theme == 'light' else 'light'
            
            # Update settings
            self.settings.setValue('theme', new_theme)
            
            # Apply theme
            if new_theme == 'dark':
                self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
                self.log_info("🌙 Switched to dark theme")
            else:
                self.setStyleSheet("")
                self.log_info("☀️ Switched to light theme")
                
            # Update theme toggle button icon
            theme_icon = "resources/icons/moon.png" if new_theme == 'light' else "resources/icons/sun.png"
            self.menu_actions['theme'].setIcon(QIcon(theme_icon))
            
        except Exception as e:
            self.log_error(f"Error toggling theme: {str(e)}")
            traceback.print_exc()

    def load_icons(self):
        theme_suffix = "dark" if self.current_theme == "Light" else "light"
        self.icons = {
            "dashboard": QIcon(f"resources/icons/dashboard_{theme_suffix}.png"),
            "automation": QIcon(f"resources/icons/automation_{theme_suffix}.png"),
            "data": QIcon(f"resources/icons/data_{theme_suffix}.png"),
            "logs": QIcon(f"resources/icons/logs_{theme_suffix}.png"),
            "scripts": QIcon(f"resources/icons/scripts_{theme_suffix}.png"),
            "settings": QIcon(f"resources/icons/settings_{theme_suffix}.png"),
            "theme": QIcon(f"resources/icons/theme_{theme_suffix}.png")
        }
        self.update_ui_icons()

    def update_ui_icons(self):
        # Initialize nav_actions if it doesn't exist
        if not hasattr(self, 'nav_actions'):
            self.nav_actions = []
            # Find all QAction objects in the menu bar
            for menu in self.menuBar().findChildren(QMenu):
                for action in menu.actions():
                    if action.icon() and not action.icon().isNull():
                        self.nav_actions.append(action)
                        # Try to determine the action type from its text
                        for key in self.icons.keys():
                            if key in action.text().lower():
                                action.setData(key)
        
        # Update icons for all actions in nav_actions
        for action in self.nav_actions:
            data = action.data()
            if data and data in self.icons:
                action.setIcon(self.icons[data])
        
        # Update theme toggle button icon
        if hasattr(self, 'theme_toggle'):
            self.theme_toggle.setIcon(self.icons.get("theme", QIcon()))

    def on_script_selected(self, script_info):
        """Handle script selection"""
        try:
            if script_info and isinstance(script_info, dict):
                script_name = script_info.get('name', '')
                script_type = script_info.get('type', '')
                params = script_info.get('params', {})
                
                self.log_info(f"📜 Selected script: {script_name}")
                
                # Switch to automation page
                self.switch_page('automation')
                
                # Run the script if automation page has the capability
                if hasattr(self, 'automation_page'):
                    self.automation_page.run_script(script_type, params)
                else:
                    self.log_warning("⚠️ Automation page not available")
                    
            else:
                self.log_warning("⚠️ Invalid script info format")
                
        except Exception as e:
            self.log_error(f"Error handling script selection: {str(e)}")
            traceback.print_exc()

    def run_script(self, script_type, params=None):
        """Run a script with specified parameters"""
        try:
            self.log_info(f"▶️ Running {script_type} script")
            
            # Switch to automation page
            self.switch_page('automation')
            
            # Run the script if automation page has the capability
            if hasattr(self, 'automation_page'):
                self.automation_page.run_script(script_type, params)
            else:
                self.log_warning("⚠️ Automation page not available")
                
        except Exception as e:
            self.log_error(f"Error running script: {str(e)}")
            traceback.print_exc()

    def refresh_all_data(self):
        """Refresh all data in the application"""
        try:
            self.log_info("🔄 Refreshing all data")
            
            # Refresh dashboard
            self.refresh_dashboard()
            
            # Refresh data page
            if hasattr(self, 'data_page'):
                self.data_page.refresh_data()
                self.log_info("📊 Data page refreshed")
            
            # Refresh script manager
            if hasattr(self, 'script_manager_page'):
                self.script_manager_page.refresh_scripts()
                self.log_info("📜 Script manager refreshed")
            
            # Refresh proxy manager
            if hasattr(self, 'proxy_manager_page'):
                self.proxy_manager_page.refresh_proxies()
                self.log_info("🌐 Proxy manager refreshed")
            
            # Refresh task scheduler
            if hasattr(self, 'task_scheduler_page'):
                self.task_scheduler_page.refresh_tasks()
                self.log_info("📅 Task scheduler refreshed")
                
        except Exception as e:
            self.log_error(f"Error refreshing data: {str(e)}")
            traceback.print_exc()

    def refresh_dashboard(self):
        """Refresh dashboard data and stats"""
        try:
            if hasattr(self, 'dashboard_page'):
                # Update general stats
                self.dashboard_page.update_general_stats()
                
                # Update system stats
                self.dashboard_page.update_system_stats()
                
                self.log_info("📊 Dashboard refreshed")
            else:
                self.log_warning("⚠️ Dashboard not available")
                
        except Exception as e:
            self.log_error(f"Error refreshing dashboard: {str(e)}")
            traceback.print_exc()

    def on_task_completed(self, result):
        """Handle task completion"""
        try:
            if result and isinstance(result, dict):
                task_type = result.get('type', '')
                status = result.get('status', '')
                message = result.get('message', '')
                data = result.get('data', None)
                
                if status == 'success':
                    self.log_info(f"✅ {task_type} task completed: {message}")
                    if data:
                        if hasattr(self, 'data_page'):
                            self.data_page.update_data(task_type, data)
                            self.log_info(f"📊 Data updated for {task_type}")
                else:
                    self.log_error(f"❌ {task_type} task failed: {message}")
                
                # Update progress bar
                self.progress_bar.setValue(100)
                QTimer.singleShot(2000, lambda: self.progress_bar.setValue(0))
                
            else:
                self.log_warning("⚠️ Invalid task result format")
                
        except Exception as e:
            self.log_error(f"Error handling task completion: {str(e)}")
            traceback.print_exc()

    def update_progress(self, value):
        """Update progress bar value"""
        try:
            if isinstance(value, (int, float)) and 0 <= value <= 100:
                self.progress_bar.setValue(int(value))
            else:
                self.log_warning(f"Invalid progress value: {value}")
        except Exception as e:
            self.log_error(f"Error updating progress: {str(e)}")
            traceback.print_exc()

    def on_script_builder_completed(self, script_name, content):
        """Handle script builder completion"""
        try:
            if script_name and content:
                # Create scripts directory if it doesn't exist
                scripts_dir = os.path.join(os.getcwd(), 'scripts')
                os.makedirs(scripts_dir, exist_ok=True)
                
                # Save script file
                script_path = os.path.join(scripts_dir, f"{script_name}.py")
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_info(f"📝 Script saved: {script_name}.py")
                
                # Refresh script manager if available
                if hasattr(self, 'script_manager_page'):
                    self.script_manager_page.refresh_scripts()
                    self.log_info("🔄 Script manager refreshed")
            else:
                self.log_warning("⚠️ Invalid script data")
                
        except Exception as e:
            self.log_error(f"Error handling script builder completion: {str(e)}")
            traceback.print_exc()

    def on_task_scheduled(self, task_info):
        """Handle task scheduling"""
        try:
            if task_info and isinstance(task_info, dict):
                task_type = task_info.get('type', '')
                schedule_time = task_info.get('schedule_time', '')
                params = task_info.get('params', {})
                
                self.log_info(f"📅 Task scheduled: {task_type} at {schedule_time}")
                
                # Refresh task scheduler if available
                if hasattr(self, 'task_scheduler_page'):
                    self.task_scheduler_page.refresh_tasks()
                    self.log_info("🔄 Task scheduler refreshed")
                    
                # Update dashboard if available
                if hasattr(self, 'dashboard_page'):
                    self.dashboard_page.update_scheduled_tasks()
                    self.log_info("📊 Dashboard updated")
            else:
                self.log_warning("⚠️ Invalid task info")
                
        except Exception as e:
            self.log_error(f"Error handling task scheduling: {str(e)}")
            traceback.print_exc()

    def on_get_trends_requested(self, source, params=None):
        """Handle trends request"""
        try:
            self.log_info(f"📊 Getting trends from {source}")
            
            # Switch to automation page
            self.switch_page('automation')
            
            # Start trends task if automation page is available
            if hasattr(self, 'automation_page'):
                task_params = {
                    'source': source,
                    'params': params or {}
                }
                self.automation_page.start_task('get_trends', task_params)
            else:
                self.log_warning("⚠️ Automation page not available")
                
        except Exception as e:
            self.log_error(f"Error handling trends request: {str(e)}")
            traceback.print_exc()

    def on_create_content_requested(self, trend_data, content_type):
        """Handle content creation request"""
        try:
            self.log_info(f"📝 Creating {content_type} content for trend: {trend_data.get('title', '')}")
            
            # Switch to automation page
            self.switch_page('automation')
            
            # Start content creation task if automation page is available
            if hasattr(self, 'automation_page'):
                task_params = {
                    'trend_data': trend_data,
                    'content_type': content_type
                }
                self.automation_page.start_task('create_content', task_params)
            else:
                self.log_warning("⚠️ Automation page not available")
                
        except Exception as e:
            self.log_error(f"Error handling content creation request: {str(e)}")
            traceback.print_exc()

    def on_post_content_requested(self, content_data, post_type):
        """Handle content posting request"""
        try:
            self.log_info(f"📤 Posting {post_type} content: {content_data.get('title', '')}")
            
            # Switch to automation page
            self.switch_page('automation')
            
            # Start content posting task if automation page is available
            if hasattr(self, 'automation_page'):
                task_params = {
                    'content_data': content_data,
                    'post_type': post_type
                }
                self.automation_page.start_task('post_content', task_params)
            else:
                self.log_warning("⚠️ Automation page not available")
                
        except Exception as e:
            self.log_error(f"Error handling content posting request: {str(e)}")
            traceback.print_exc()

    def show_post_result(self, success):
        """Show post result dialog"""
        try:
            if success:
                QMessageBox.information(
                    self,
                    "Post Success",
                    "Content has been posted successfully!",
                    QMessageBox.Ok
                )
                self.log_info("✅ Content posted successfully")
            else:
                QMessageBox.warning(
                    self,
                    "Post Failed",
                    "Failed to post content. Please check logs for details.",
                    QMessageBox.Ok
                )
                self.log_error("❌ Failed to post content")
                
        except Exception as e:
            self.log_error(f"Error showing post result: {str(e)}")
            traceback.print_exc()

    def show_schedule_result(self, success):
        """Show dialog with schedule result"""
        if success:
            QMessageBox.information(self, "Lên lịch thành công", "Đã lên lịch đăng bài thành công!")
        else:
            QMessageBox.warning(self, "Lên lịch thất bại", "Không thể lên lịch đăng bài. Vui lòng thử lại sau.")

    def load_settings(self):
        """Load and apply user settings"""
        # Load theme setting
        theme = self.settings.value("theme", DEFAULT_THEME)
        retry_count = self.settings.value("retry_count", 3, type=int)
        timeout = self.settings.value("timeout", 30, type=int)
        font_size = self.settings.value("font_size", 10, type=int)
        
        # Apply theme
        self.current_theme = theme
        self.apply_theme(theme)
        
        # Apply retry and timeout settings to worker components
        if hasattr(self, 'automation_page') and self.automation_page:
            # Update automation page theme
            if hasattr(self.automation_page, 'setup_styles'):
                self.automation_page.setup_styles()
                
        # Apply font size across components if needed
        font = QFont()
        font.setPointSize(font_size)
        QApplication.setFont(font)
        
        # Log settings loaded
        self.log(f"Settings loaded: Theme={theme}, Retry={retry_count}, Timeout={timeout}, Font={font_size}pt")

    def log_info(self, message):
        """Log an info message"""
        try:
            if hasattr(self, 'logs_page'):
                self.logs_page.log_info(message)
            logging.info(message)
        except Exception as e:
            print(f"Error logging info message: {str(e)}")
            traceback.print_exc()

    def log_warning(self, message):
        """Log a warning message"""
        try:
            if hasattr(self, 'logs_page'):
                self.logs_page.log_warning(message)
            logging.warning(message)
        except Exception as e:
            print(f"Error logging warning message: {str(e)}")
            traceback.print_exc()

    def log_error(self, message):
        """Log an error message"""
        try:
            if hasattr(self, 'logs_page'):
                self.logs_page.log_error(message)
            logging.error(message)
        except Exception as e:
            print(f"Error logging error message: {str(e)}")
            traceback.print_exc()

    def log_debug(self, message):
        """Log a debug message"""
        try:
            if hasattr(self, 'logs_page'):
                self.logs_page.log_debug(message)
            logging.debug(message)
        except Exception as e:
            print(f"Error logging debug message: {str(e)}")
            traceback.print_exc()

    def init_automation_worker(self):
        """Khởi tạo automation worker với cấu hình từ settings"""
        try:
            # Lấy cấu hình từ settings
            chrome_config = {
                "chrome_path": self.settings.value("brave_path", ""),
                "profile_path": self.settings.value("brave_profile", ""),
                "headless": self.settings.value("headless_mode", False, type=bool),
                "proxy": self.settings.value("proxy", ""),
                "delay": self.settings.value("delay", 0.0, type=float)
            }
            
            # Khởi tạo worker
            self.automation_worker = EnhancedAutomationWorker(
                chrome_config=chrome_config,
                headless=chrome_config["headless"],
                proxy=chrome_config["proxy"],
                delay=chrome_config["delay"]
            )
            
            # Kết nối signals
            self.automation_worker.log_signal.connect(self.log_info)
            self.automation_worker.error_signal.connect(self.log_error)
            self.automation_worker.progress_signal.connect(self.update_progress)
            self.automation_worker.result_signal.connect(self.handle_automation_result)
            self.automation_worker.finished_signal.connect(self.handle_automation_finished)
            
            self.log_info("✅ Đã khởi tạo automation worker thành công")
            return True
            
        except Exception as e:
            self.log_error(f"❌ Lỗi khởi tạo automation worker: {str(e)}")
            return False

    def handle_automation_result(self, result):
        """Xử lý kết quả từ automation worker"""
        try:
            if result:
                self.log_info("✅ Automation task completed successfully")
                # TODO: Xử lý kết quả cụ thể tùy theo loại task
            else:
                self.log_error("❌ Automation task failed")
        except Exception as e:
            self.log_error(f"❌ Lỗi xử lý kết quả automation: {str(e)}")

    def handle_automation_finished(self, success):
        """Xử lý khi automation worker hoàn thành"""
        try:
            if success:
                self.log_info("✅ Automation process finished successfully")
            else:
                self.log_error("❌ Automation process failed")
            
            # Reset UI
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Ready")
            
        except Exception as e:
            self.log_error(f"❌ Lỗi xử lý kết thúc automation: {str(e)}")

    def update_progress(self, value):
        """Cập nhật thanh tiến trình"""
        try:
            self.progress_bar.setValue(value)
            self.statusBar().showMessage(f"Progress: {value}%")
        except Exception as e:
            self.log_error(f"❌ Lỗi cập nhật tiến trình: {str(e)}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
