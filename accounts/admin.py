from django.contrib import admin

# Register your models here.
from .models import Profile, IndiaMartAccount, Subscription, CategoryKeyword, RejectedKeyword, Notification, IndiaMartLead,ReviewCheck

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


from .models import ScheduleSettings
from django.contrib import messages

@admin.register(ScheduleSettings)
class ScheduleSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'chrome_port', 'status', 'start_time', 'end_time', 'days_of_week')
    actions = ['start_selenium_task', 'stop_selenium_task']

    def start_selenium_task(self, request, queryset):
        """Admin action to start the Selenium task."""
        for schedule in queryset:
            if schedule.status == 'running':
                self.message_user(request, f"Task for {schedule.user.username} is already running.", level=messages.WARNING)
            else:
                # Example: Set a fixed or available port for demonstration
                schedule.chrome_port = schedule.user.profile.port_number  # Example: Retrieve user's port
                schedule.status = 'running'
                schedule.save()
                # Start Selenium task (you could integrate with your function here)
                self.message_user(request, f"Started Selenium task for {schedule.user.username} on port {schedule.chrome_port}.", level=messages.SUCCESS)

    start_selenium_task.short_description = "Start selected Selenium tasks"

    def stop_selenium_task(self, request, queryset):
        """Admin action to stop the Selenium task."""
        for schedule in queryset:
            if schedule.status == 'stopped':
                self.message_user(request, f"Task for {schedule.user.username} is already stopped.", level=messages.WARNING)
            else:
                # Here you would add code to stop the actual running Selenium task
                # For example, setting stop_event for your Selenium function to halt the process
                schedule.status = 'stopped'
                schedule.chrome_port = None  # Clear the port if desired
                schedule.save()
                self.message_user(request, f"Stopped Selenium task for {schedule.user.username}.", level=messages.SUCCESS)

    stop_selenium_task.short_description = "Stop selected Selenium tasks"


@admin.register(IndiaMartLead)
class IndiaMartLeadAdmin(admin.ModelAdmin):
    list_display = ('account', 'product', 'name', 'phone_number', 'email', 'location')
    search_fields = ('name', 'product', 'location')



@admin.register(ReviewCheck)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'ask_for_review']
    search_fields = ['user__username', 'ask_for_review']