"""净值相关 Admin"""
from backend.admin.base import UserScopedModelAdmin, admin
from backend.models import HkdCnyDailyRate, PortfolioNavDaily, StockDailyPrice


@admin.register(PortfolioNavDaily)
class PortfolioNavDailyAdmin(UserScopedModelAdmin):
    list_display = ['user', 'date', 'nav', 'units', 'asset', 'cash']
    list_filter = ['user', 'date']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['user', 'date', 'nav', 'units', 'asset', 'cash']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(StockDailyPrice)
class StockDailyPriceAdmin(admin.ModelAdmin):
    list_display = ['code', 'date', 'close']
    list_filter = ['date']
    search_fields = ['code']
    date_hierarchy = 'date'
    ordering = ['-date', 'code']
    readonly_fields = ['code', 'date', 'close']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(HkdCnyDailyRate)
class HkdCnyDailyRateAdmin(admin.ModelAdmin):
    list_display = ['date', 'close']
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['date', 'close']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
