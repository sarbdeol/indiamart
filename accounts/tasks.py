import logging
from datetime import datetime
from django.contrib.auth.models import User
from .models import IndiaMartAccount, CategoryKeyword, RejectedKeyword
from Scraper.runnew import run_selenium_script  # Assuming your Selenium function is here

# Configure logging
logging.basicConfig(
    filename='/home/ubuntu/schedule_logs/selenium_task.log',  # Specify the path to the log file
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Define the log format
)

# Dictionary to track running instances
running_tasks = {}

def start_selenium_at_scheduled_time(user_id, start_time, end_time, days,stop_event):
    now = datetime.now()
    day_name = now.strftime('%A').lower()
    logging.info(f"Task triggered for user {user_id} at {now}")

    # Check if today is one of the scheduled days
    if day_name in days:
        current_time = now.time()
        logging.info(f"Today ({day_name}) is in scheduled days {days} for user {user_id}.")

        # Check if current time is within the scheduled range
        if start_time <= current_time <= end_time:
            # Check if the task is already running for this user
            if running_tasks.get(user_id, False):
                logging.info(f"Selenium script is already running for user {user_id}. Skipping this run.")
                return

            # Mark the task as running
            running_tasks[user_id] = True
            try:
                user = User.objects.get(id=user_id)
                logging.info(f"User {user.username} found with ID {user_id}.")
                
                try:
                    indiamart_account = IndiaMartAccount.objects.get(user=user)
                    logging.info(f"IndiaMart account found for user {user.username}.")
                except IndiaMartAccount.DoesNotExist:
                    indiamart_account = None
                    logging.warning(f"No IndiaMart account found for user {user.username}.")

                # Fetch category keywords and rejected keywords for the user
                category_keywords = list(CategoryKeyword.objects.filter(user=user).values_list('keyword', flat=True))
                rejected_keywords = list(RejectedKeyword.objects.filter(user=user).values_list('keyword', flat=True))

                quantity = indiamart_account.quantity if indiamart_account else 0
                
                # Log the keywords and other details
                logging.info(f"Category keywords: {category_keywords}")
                logging.info(f"Rejected keywords: {rejected_keywords}")
                logging.info(f"Quantity: {quantity}")

                # Call your Selenium script
                logging.info(f"Starting Selenium script for user {user.username} on port {user.profile.port_number}.")
                run_selenium_script(
                    user.profile.port_number, 
                    user.username, 
                    category_keywords, 
                    rejected_keywords, 
                    quantity,
                    stop_event=stop_event  # Assuming you may use a stop event if needed
                )
                logging.info(f"Selenium script completed for user {user.username}.")

            except User.DoesNotExist:
                logging.error(f"User with ID {user_id} does not exist.")
            finally:
                # Mark the task as not running
                running_tasks[user_id] = False
        else:
            time_to_start = datetime.combine(datetime.today(), start_time) - now
            logging.info(f"Time left to start for user {user_id}: {time_to_start}")
    else:
        logging.info(f"Today ({day_name}) is not in the scheduled days {days} for user {user_id}.")
