from datetime import datetime, time
from django.contrib.auth.models import User
from accounts.models import IndiaMartAccount, CategoryKeyword, RejectedKeyword
from Scraper.runnew import run_selenium_script  # Assuming your Selenium function is here
import os
import django
from django.core.management.base import BaseCommand

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # Replace with your settings path
django.setup()

def start_selenium_at_scheduled_time(user_id, start_time, end_time, days):
    now = datetime.now()
    day_name = now.strftime('%A').lower()
    print(f"Task triggered for user {user_id} at {now}")

    # Check if today is one of the scheduled days
    if day_name in days:
        current_time = now.time()

        # Check if current time is within the scheduled range
        if start_time <= current_time <= end_time:
            user = User.objects.get(id=user_id)
            try:
                indiamart_account = IndiaMartAccount.objects.get(user=user)
            except IndiaMartAccount.DoesNotExist:
                indiamart_account = None

            # Fetch category keywords and rejected keywords for the user
            category_keywords = list(CategoryKeyword.objects.filter(user=user).values_list('keyword', flat=True))
            rejected_keywords = list(RejectedKeyword.objects.filter(user=user).values_list('keyword', flat=True))

            quantity = indiamart_account.quantity if indiamart_account else 0

            # Call your Selenium script
            run_selenium_script(
                user.profile.port_number,
                user.username,
                category_keywords,
                rejected_keywords,
                quantity,
                None
            )

class Command(BaseCommand):
    help = 'Runs the scheduled Selenium task'

    def handle(self, *args, **kwargs):
        # Define the parameters
        user_id = 4  # Replace with the appropriate user ID
        start_time = time(10, 0)
        end_time = time(12, 0)
        days = ['monday', 'tuesday', 'sunday']

        # Run the task
        start_selenium_at_scheduled_time(user_id, start_time, end_time, days)
        print("Selenium task executed.")
