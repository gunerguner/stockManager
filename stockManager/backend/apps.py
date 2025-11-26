from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'
    
    def ready(self):
        """应用启动时执行，确保信号监听器被注册"""
        import backend.services.stockMeta  # noqa: F401
        import backend.services.integrate  # noqa: F401 确保信号监听器被注册
        import backend.common.tradingCalendar  # noqa: F401 触发交易日历预加载
        # 导入 admin 模块，确保所有 admin 配置类被注册
        import backend.admin  # noqa: F401
        