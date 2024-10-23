from django.contrib import admin

# Register your models here.
from .models import Profile, IndiaMartAccount, Subscription, CategoryKeyword, RejectedKeyword, Notification

# Register Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'port_number']
    search_fields = ['user__username', 'port_number']

# Register IndiaMartAccount model
@admin.register(IndiaMartAccount)
class IndiaMartAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'indiamart_username', 'quantity']
    search_fields = ['user__username', 'indiamart_username']

# Register Subscription model
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'start_date', 'end_date']
    search_fields = ['user__username', 'is_active']

# Register CategoryKeyword model
@admin.register(CategoryKeyword)
class CategoryKeywordAdmin(admin.ModelAdmin):
    list_display = ['user', 'keyword']
    search_fields = ['user__username', 'keyword']

# Register RejectedKeyword model
@admin.register(RejectedKeyword)
class RejectedKeywordAdmin(admin.ModelAdmin):
    list_display = ['user', 'keyword']
    search_fields = ['user__username', 'keyword']

# Register Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'timestamp']
    search_fields = ['user__username', 'message']
    readonly_fields = ['timestamp']
