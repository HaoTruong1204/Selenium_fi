"""
Selenium Automation Hub - Module Initialization
Quản lý các import và khởi tạo cho toàn bộ ứng dụng
"""

from .main_window import MainWindow
from .automation_worker import EnhancedAutomationWorker
from .dashboard import DashboardWidget
from .automation_view import AutomationView
from .data_view import DataWidget
from .logs_view import LogsWidget
from .script_manager import ScriptManagerWidget
from .proxy_manager import ProxyManagerWidget
from .task_scheduler import TaskSchedulerWidget
from .settings_dialog import SettingsDialog
from .splash_screen import SplashScreen
from .captcha_resolver import CaptchaResolver
from .script_builder import ScriptBuilderWidget

__all__ = [
    'MainWindow',
    'EnhancedAutomationWorker',
    'DashboardWidget',
    'AutomationView',
    'DataWidget',
    'LogsWidget',
    'ScriptManagerWidget',
    'ProxyManagerWidget',
    'TaskSchedulerWidget',
    'SettingsDialog',
    'SplashScreen',
    'CaptchaResolver',
    'ScriptBuilderWidget'
] 