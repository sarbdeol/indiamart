from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('delete_category_keyword/<int:keyword_id>/', views.delete_category_keyword, name='delete_category_keyword'),
    path('delete_rejected_keyword/<int:keyword_id>/', views.delete_rejected_keyword, name='delete_rejected_keyword'),
    path('delete_message_prompt/<int:keyword_id>/', views.delete_message_prompt, name='delete_message_prompt'),
    path('setting/', views.setting_view, name='setting'),
    path('profile/', views.profile_view, name='profile'), 
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('subscription/', views.subscription_page, name='subscription'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('fetch_logs/', views.fetch_logs, name='fetch_logs'),
    path('contact/', views.contact, name='contact'), 
    path('check_password/', views.check_password, name='check_password'), 
    path('schedules/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('schedules/create/', views.schedule_start_function, name='schedule_start_function'),
    
]