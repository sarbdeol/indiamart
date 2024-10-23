from celery import shared_task
from datetime import datetime
from django.contrib.auth.models import User
from .models import IndiaMartAccount, CategoryKeyword, RejectedKeyword
from Scraper.runnew import run_selenium_script  # Assuming your Selenium function is here

@shared_task
def start_selenium_at_scheduled_time(user_id, start_time, end_time, days):
    now = datetime.now()
    day_name = now.strftime('%A').lower()
    print(f"Task triggered for user {user_id} at {now}")
    # Check if today is one of the scheduled days
    if day_name in days:
        current_time = now.time()

        # Convert start_time and end_time to `time` objects
        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

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
            run_selenium_script(user.profile.port_number, user.username, category_keywords, rejected_keywords, quantity)
