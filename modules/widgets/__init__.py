"""
Selenium Automation Hub - Widgets Module
Chứa các widget cho giao diện người dùng
"""

from .dashboard import DashboardWidget
from .automation_view import AutomationView
from .data_view import DataWidget
from .logs_view import LogsWidget
from .script_manager import ScriptManagerWidget
from .proxy_manager import ProxyManagerWidget
from .task_scheduler import TaskSchedulerWidget

__all__ = [
    'DashboardWidget',
    'AutomationView',
    'DataWidget',
    'LogsWidget',
    'ScriptManagerWidget',
    'ProxyManagerWidget',
    'TaskSchedulerWidget'
] 