from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'
    
    def ready(self):
        """应用启动时执行，确保信号监听器被注册"""
        import backend.stockMeta  # noqa: F401
