from django.db import models


class SwIndustry(models.Model):
    """申万行业目录（全局共享）"""

    code = models.CharField(max_length=16, verbose_name="行业代码")
    name = models.CharField(max_length=64, verbose_name="行业名称")

    class Meta:
        verbose_name = "申万行业"
        verbose_name_plural = "申万行业"
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                name="uniq_swindustry_code",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
