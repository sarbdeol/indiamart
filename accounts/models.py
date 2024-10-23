from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from datetime import timedelta
from django.utils import timezone
# Profile model to extend the built-in User model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    port_number = models.IntegerField(unique=True, blank=True, null=True)  # Field for storing port number

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
    days_of_week = models.CharField(max_length=200, blank=True)  # Store days as a comma-separated list

    def __str__(self):
        return f"Schedule for {self.user.username}"