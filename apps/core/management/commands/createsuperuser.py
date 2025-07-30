"""
创建超级用户的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = '创建超级用户'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='用户名')
        parser.add_argument('--email', type=str, default='admin@example.com', help='邮箱')
        parser.add_argument('--password', type=str, default='admin123', help='密码')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # 检查用户是否已存在
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'用户 {username} 已存在')
                )
                return

            # 创建超级用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
                is_staff=True,
                is_superuser=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'成功创建超级用户:\n'
                    f'用户名: {username}\n'
                    f'邮箱: {email}\n'
                    f'密码: {password}\n'
                    f'角色: 管理员'
                )
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'创建用户失败: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'发生错误: {e}')
            ) 