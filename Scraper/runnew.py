from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import sys
import time  # Import the time module for sleep functionality
import subprocess
from .config import keywordcategory, keywordsrejectheading, max_counter  # Importing from config.py
from django.contrib.auth.models import User
from accounts.models import Notification  # Import the Notification model
# Initialize success and failure counters
success_counter = 0
failure_counter = 0

# Function to refresh the page
def refresh_page(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        driver.refresh()

        if driver.current_url == url:
            print("Page refreshed successfully.")
            return driver  # Return the driver on success
        else:
            print("Failed to refresh the page.")
            return None  # Return None on failure
    except WebDriverException as e:
        print(f"An error occurred: {e}")
        return None  # Return None in case of an error

# Function to click the first label element that contains 'India'
def click_india_label(driver):
    try:
        label_element = driver.find_element(By.XPATH, "//label[contains(@class, 'rdo_btn') and contains(text(),'India')]")
        label_element.click()
        print("Label with 'India' clicked successfully.")
        return 0  # Return 0 on success

    except Exception as e:
        print(f"An error occurred while clicking the label: {e}")
        return 1  # Return 1 in case of an error

# Function to read and check the text inside the first <span> element
def check_span_for_keywords(driver,keywordcategory):
    try:
        span_element = driver.find_element(By.XPATH, '//span[contains(@style,"cursor: pointer") and contains(@style,"color: rgb(42, 166, 153);")]')
        span_text = span_element.text
        
        for category in keywordcategory:
            if category.lower() in span_text.lower():  # Case-insensitive check
                print("Keyword found in span text.")
                return 0  # Exit once a category is found (successful match)

        print("No keyword found in span text.")
        return 1  # Return 1 if no keyword matches (unsuccessful)
    
    except Exception as e:
        print(f"An error occurred while checking the span: {e}")
        return 1  # Return 1 in case of an error

# Function to extract and check the first <h2> element for keywords
def extract_first_h2(driver,keywordsrejectheading):
    try:
        h2_element = driver.find_element(By.TAG_NAME, "h2")
        h2_text = h2_element.text
        
        for keyword in keywordsrejectheading:
            if keyword.lower() in h2_text.lower():
                print("Rejections found")
                return 1  # Return 1 if a keyword is found

        print("No rejections found")
        return 0  # Return 0 if no keywords found

    except Exception as e:
        print("1")  # In case of an error
        return 1  # Return 1 on error

# Function to check the first <p><strong> element that contains 'mins ago'
def check_time_and_execute(driver):
    try:
        time_element = driver.find_element(By.XPATH, "//p/strong[contains(text(),'mins ago')]")
        time_text = time_element.text

        minutes = int(time_text.split()[0])  # Get the number part
        
        if minutes < 5:
            
            print("0")
            subprocess.run(["python3", "click.py"])  # Runs another script
            return 1  # Return 1 if script is run

        print("Time is 5 minutes or more, no action taken.")
        return 0  # Return 0 if no action is taken

    except Exception as e:
        print("1")
        return 0  # Return 0 in case of error


from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import time
import subprocess
import sys

# Import user_logs from the views
from accounts.log_store import user_logs
# Main Selenium function to execute the script
def run_selenium_script(port_number, username, category_keywords, rejected_keywords, quantity,stop_event):
    url = "https://seller.indiamart.com/bltxn/?pref=recent"
    
    # Initialize success and failure counters
    success_counter = 0
    failure_counter = 0
    max_counter = quantity  # Or fetch from config if needed

    # Initialize logs for the user
    if username not in user_logs:
        user_logs[username] = []

    def log_message(message):
        user_logs[username].append(message)
        print(message)

    # Rest of your selenium logic, calling log_message at key steps
    log_message("Automation script started...")
    # Function to refresh the page
    def refresh_page(url):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"localhost:{port_number}")
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            driver.refresh()
            # log_message("Page refreshed successfully.")
            
            return driver
        except WebDriverException as e:
            log_message(f"An error occurred while refreshing the page: {e}")
            return None
    
    def open_chrome(port_number):
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust path to your chrome.exe
        user_data_dir = f"C:/Chrome session_{port_number}"  # Use a port-specific user data directory
        
        chrome_command = [
            chrome_path,
            f"--remote-debugging-port={port_number}",
            f"--user-data-dir={user_data_dir}"
        ]
        subprocess.Popen(chrome_command)
        # Main loop
    open_chrome(port_number)

    while success_counter < max_counter:
        if stop_event.is_set():  # Check if the stop event is set
            log_message("Automation stopped by user request.")
            break  # Exit the loop if the stop event is set

        time.sleep(2)
        driver = refresh_page(url)
        
        if driver:
            time.sleep(3)
            try:
                notification_text = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[2]/p').text

                # Save the notification in the database
                user = User.objects.get(username=username)  # Replace with the correct user logic
                Notification.objects.create(user=user, message=notification_text)
            except Exception as e:
                print(e)
            click_result = click_india_label(driver)
            
            if click_result == 0:
                time.sleep(3)
                refresh_result_2 = refresh_page(url)
                
                if refresh_result_2:
                    time.sleep(3)
                    span_result = check_span_for_keywords(driver,category_keywords)
                    
                    if span_result == 0:
                        time.sleep(3)
                        h2_result = extract_first_h2(driver,rejected_keywords)
                        
                        if h2_result == 0:
                            time.sleep(3)
                            time_check_result = check_time_and_execute(driver)
                            
                            # Increment success counter if all functions were successful
                            if time_check_result == 1:
                                log_message("New lead found")
                                success_counter += 1
                                span_element = driver.find_element(By.XPATH, '//span[contains(@style,"cursor: pointer") and contains(@style,"color: rgb(42, 166, 153);")]')
                                span_text = span_element.text
                                log_message(f"Title : {span_text}")
                                h2_element = driver.find_element(By.TAG_NAME, "h2")
                                h2_text = h2_element.text
                                log_message(f"Heading : {h2_text}")

                                print(f"Successful run count: {success_counter}/{max_counter}")
                                log_message(f"Successful run {success_counter}/{max_counter}")
                            else:
                                failure_counter += 1
                                print(f"Unsuccessful run count: {failure_counter}")
                        else:
                            failure_counter += 1
                            print(f"Unsuccessful run count: {failure_counter}")
                            sys.exit(h2_result)  # Exit if the <h2> check fails
                    else:
                        failure_counter += 1
                        print(f"Unsuccessful run count: {failure_counter}")
                        sys.exit(span_result)  # Exit if the span check fails
                else:
                    failure_counter += 1
                    print(f"Unsuccessful run count: {failure_counter}")
                    sys.exit(1)  # Exit if the second refresh fails
            else:
                failure_counter += 1
                print(f"Unsuccessful run count: {failure_counter}")
                sys.exit(click_result)  # Exit if clicking the label fails
        else:
            failure_counter += 1
            print(f"Unsuccessful run count: {failure_counter}")
            sys.exit(1)  # Exit if the first page refresh fails
            # log_message("Failed to refresh the page.")
            break

    log_message(f"Script execution completed. Successes: {success_counter}, Failures: {failure_counter}")
    driver.quit()