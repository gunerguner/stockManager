# 数据迁移脚本模板
# 将此文件内容复制到: backend/migrations/0003_migrate_existing_data_to_user.py

from django.db import migrations
from django.contrib.auth.models import User


def migrate_data_to_user(apps, schema_editor):
    """将现有数据迁移到默认用户"""
    Operation = apps.get_model('backend', 'Operation')
    Info = apps.get_model('backend', 'Info')
    
    # 1. 获取或创建默认用户
    try:
        # 优先使用第一个超级用户
        default_user = User.objects.filter(is_superuser=True).first()
        
        if not default_user:
            # 如果没有超级用户，创建一个默认管理员
            default_user = User.objects.create_user(
                username='admin',
                password='admin123456',  # 记得登录后修改密码
                is_superuser=True,
                is_staff=True,
                first_name='管理员'
            )
            print(f"✅ 已创建默认用户: {default_user.username}")
            print(f"⚠️  默认密码: admin123456（请登录后立即修改）")
        else:
            print(f"✅ 使用现有超级用户: {default_user.username}")
    except Exception as e:
        print(f"❌ 获取默认用户失败: {e}")
        return
    
    # 2. 迁移 Operation 数据
    operation_count = Operation.objects.filter(user__isnull=True).count()
    if operation_count > 0:
        Operation.objects.filter(user__isnull=True).update(user=default_user)
        print(f"✅ 已迁移 {operation_count} 条 Operation 记录到用户 {default_user.username}")
    else:
        print(f"ℹ️  没有需要迁移的 Operation 记录")
    
    # 3. 迁移 Info 数据
    info_count = Info.objects.filter(user__isnull=True).count()
    if info_count > 0:
        Info.objects.filter(user__isnull=True).update(user=default_user)
        print(f"✅ 已迁移 {info_count} 条 Info 记录到用户 {default_user.username}")
    else:
        print(f"ℹ️  没有需要迁移的 Info 记录")
    
    # 4. 验证迁移结果
    total_operations = Operation.objects.count()
    total_infos = Info.objects.count()
    print(f"ℹ️  当前 Operation 总记录数: {total_operations}")
    print(f"ℹ️  当前 Info 总记录数: {total_infos}")


def reverse_migration(apps, schema_editor):
    """回滚操作（可选）"""
    print("⚠️  回滚操作：将用户字段设为 NULL")
    # 注意：实际回滚时可能需要更复杂的逻辑


class Migration(migrations.Migration):
    
    dependencies = [
        ('backend', '0002_alter_info_options_alter_operation_options_and_more'),  # ⚠️ 替换为实际的上一个迁移文件名
    ]

    operations = [
        migrations.RunPython(migrate_data_to_user, reverse_migration),
    ]

