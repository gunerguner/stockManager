"""申万行业目录管理"""
from backend.admin.base import BaseModelAdmin, admin
from backend.models import SwIndustry


@admin.register(SwIndustry)
class SwIndustryAdmin(BaseModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["code", "name"]
    ordering = ["code"]
