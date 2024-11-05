from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from datetime import timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone
# Profile model to extend the built-in User model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    port_number = models.IntegerField(unique=True, blank=True, null=True)  # Field for storing port number
    stop_selenium = models.BooleanField(default=False)  # Field to control stopping the Selenium task
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def assign_port(self):
        """Assign a unique port number to each user"""
        # Generate a port number in the range of 8000 to 9000
        while True:
            port = random.randint(8000, 9000)
            if not Profile.objects.filter(port_number=port).exists():
                self.port_number = port
                break

# Signal to create a Profile object and assign a port number when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)  # Create Profile for the new user
        profile.assign_port()  # Assign a port number
        profile.save()  # Save the profile with the port number

# Signal to save the Profile object when the User object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()  # Ensure the profile is saved when user is updated




class IndiaMartAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    indiamart_username = models.CharField(max_length=255)
    indiamart_password = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)  # New Quantity field with default value

    def __str__(self):
        return f"{self.user.username}'s IndiaMart Account"


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)  # Indicates if the user is subscribed
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)  # Expiry of subscription

    def activate_subscription(self):
        self.is_active = True
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=30)  # Example: 30-day subscription
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Subscription"
    


class CategoryKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword

class RejectedKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who received the notification
    message = models.TextField()  # The notification message
    timestamp = models.DateTimeField(auto_now_add=True)  # When the notification was saved

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"


class ScheduleSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    run_24_7 = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    chrome_port = models.IntegerField(null=True, blank=True)
    days_of_week = models.CharField(max_length=200, blank=True)  # Store days as a comma-separated list

    def __str__(self):
        return f"Schedule for {self.user.username}"

    @property
    def status(self):
        """Determine if the schedule is 'running', has 'time_left' to start, or is 'finished'."""
        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%A').lower()

        # Check if today is within the scheduled days
        days = self.days_of_week.lower().split(',') if self.days_of_week else []
        if self.run_24_7 or current_day in days:
            start_datetime = timezone.make_aware(datetime.combine(now.date(), self.start_time))
            end_datetime = timezone.make_aware(datetime.combine(now.date(), self.end_time))
            
            if start_datetime <= now <= end_datetime:
                return 'running'
            elif now < start_datetime:
                return 'time_left'
            else:
                return 'finished'
        return 'finished'

    @property
    def time_left(self):
        """Calculate the time left to start or finish, depending on the status."""
        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%A').lower()
        
        # Check if today is within the scheduled days
        days = self.days_of_week.lower().split(',') if self.days_of_week else []
        if self.run_24_7 or current_day in days:
            start_datetime = timezone.make_aware(datetime.combine(now.date(), self.start_time))
            end_datetime = timezone.make_aware(datetime.combine(now.date(), self.end_time))
            
            if now < start_datetime:
                # Time left until the task starts
                time_remaining = start_datetime - now
                return f"Time left to start: {self.format_time_remaining(time_remaining)}"
            elif start_datetime <= now <= end_datetime:
                # Time left until the task finishes
                time_remaining = end_datetime - now
                return f"Time left to finish: {self.format_time_remaining(time_remaining)}"
        
        return "Task has finished for today."

    def format_time_remaining(self, delta):
        """Format the time delta in hours and minutes."""
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours} hours, {minutes} minutes"