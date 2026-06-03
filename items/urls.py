from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('',                          views.home,               name='home'),
    path('post/',                     views.post_item,          name='post_item'),
    path('item/<int:pk>/',            views.item_detail,        name='detail'),
    path('item/<int:pk>/claim/',      views.claim_item,         name='claim'),
    path('item/<int:pk>/found-response/', views.found_response, name='found_response'),
    path('dashboard/',                views.dashboard,          name='dashboard'),
    path('admin-panel/',              views.admin_dashboard,    name='admin_dashboard'),
    path('admin-panel/claim/<int:pk>/', views.admin_claim_detail, name='admin_claim_detail'),
    path('response/<int:pk>/read/', views.mark_response_read, name='mark_response_read'),
    path('item/<int:pk>/resolve/', views.mark_item_resolved, name='resolve_item'),
    path('notification/<int:pk>/read/',  views.mark_notification_read,      name='mark_notification_read'),
path('notifications/read-all/',      views.mark_all_notifications_read,  name='mark_all_notifications_read'),
]