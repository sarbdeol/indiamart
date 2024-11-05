import os
import subprocess
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import ScheduleSettings
from accounts.tasks import start_selenium_at_scheduled_time
import django
import threading
# Set the Django settings environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # Replace with your settings path
django.setup()

def is_chrome_running_on_port(port):
    """Check if Chrome is running on the specified port."""
    result = subprocess.run(
        ["lsof", "-i", f":{port}", "-a", "-c", "chrome"], capture_output=True, text=True
    )
    return result.returncode == 0  # Returns True if Chrome is running on the port

class Command(BaseCommand):
    help = "Check and run scheduled Selenium tasks"

    def handle(self, *args, **kwargs):
        # Get the current time and day
        stop_events = {}
        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%A')  # e.g., 'Sunday'
        print(f"Current time: {now}, Current day: {current_day}")

        # Retrieve all schedule settings
        schedules = ScheduleSettings.objects.all()
        print(f"Found {len(schedules)} schedules")

        for schedule in schedules:
            user = schedule.user
            print(f"Processing schedule for user: {user.username}")

            # Get the schedule times and the user's Chrome debugging port
            start_time = schedule.start_time
            end_time = schedule.end_time
            port_number = user.profile.port_number  # Assume the port number is stored here
            print(f"User's scheduled start time: {start_time}, end time: {end_time}, port number: {port_number}")

            # Convert start and end times to timezone-aware datetime objects
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(now.date(), start_time), timezone.get_current_timezone()
            )
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(now.date(), end_time), timezone.get_current_timezone()
            )

            print(f"Start datetime: {start_datetime}, End datetime: {end_datetime}")

            # Check if the current time is within the schedule range and if today is allowed
            if start_datetime <= now <= end_datetime:
                print(f"Current time is within the schedule time range for {user.username}.")
                if schedule.run_24_7 or current_day.lower() in schedule.days_of_week:
                    if is_chrome_running_on_port(port_number):
                        print(f"Chrome is running on port {port_number} for user {user.username}. Proceeding with task.")
                        
                        # Create a stop event for this user if not already created
                        if user.id not in stop_events:
                            stop_events[user.id] = threading.Event()

                        # Start the Selenium task using the already open Chrome instance
                        start_selenium_at_scheduled_time(user.id, start_time, end_time, schedule.days_of_week, stop_events[user.id])
                        self.stdout.write(f"Started Selenium for {user.username} as per schedule.")
                    else:
                        print(f"Chrome is not running on port {port_number} for user {user.username}. Please ensure Chrome is open on the correct port.")
                else:
                    print(f"Today ({current_day}) is not in the allowed days for {user.username}.")
            else:
                if now < start_datetime:
                    time_to_start = start_datetime - now
                    print(f"Time left to start for {user.username}: {time_to_start}")
                elif now > end_datetime:
                    # Set the stop event to stop the task if it is running
                    if user.id in stop_events and not stop_events[user.id].is_set():
                        stop_events[user.id].set()
                        print(f"Stopping Selenium task for {user.username} as the scheduled time has ended.")