from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'
    
    def ready(self):
        """应用启动时执行，确保信号监听器被注册"""
        import backend.services.cache.user.store  # noqa: F401
        import backend.services.cache.user.watchlist  # noqa: F401
        import backend.services.cache.market.meta  # noqa: F401
        import backend.common.domain.calendar  # noqa: F401 触发交易日历预加载
        # 导入 admin 模块，确保所有 admin 配置类被注册
        import backend.admin  # noqa: F401
        