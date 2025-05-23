# index/dashboard.py
from admin_tools.dashboard import Dashboard, modules
from django.urls import reverse

class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        self.children.append(
            modules.LinkList(
                title='快捷操作',
                children=[
                    {
                        'title': 'ES查询',
                        'url': reverse('custom_admin:es_questions'),
                        'external': False,  # 内部链接
                    },
                ]
            )
        )
