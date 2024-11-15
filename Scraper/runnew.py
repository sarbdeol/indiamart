from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys
import time  # Import the time module for sleep functionality
import subprocess
from .config import keywordcategory, keywordsrejectheading, max_counter  # Importing from config.py
from django.contrib.auth.models import User
from accounts.models import Notification  # Import the Notification model
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # Replace with your actual project settings module
django.setup()

from accounts.models import IndiaMartAccount, IndiaMartLead  # Import the models
from django.contrib.auth.models import User
# Initialize success and failure counters
success_counter = 0
failure_counter = 0

# Function to refresh the page

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
        driver.save_screenshot('check.png')
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
def goto_lead(driver,message_prompts):
    # lead=driver.find_element(By.XPATH,'//span[@id="messageCount"]')
    # lead.click()
    import random
    prompt = random.choice(message_prompts)
    driver.get('https://seller.indiamart.com/messagecentre/')
    time.sleep(4)

    first_lead=driver.find_element(By.XPATH,'//*[@id="splitViewContactList"]/div/div/div/div[1]/div/div[1]/div[1]')
    first_lead.click()
    time.sleep(2)
    try:
        cross=driver.find_element(By.XPATH,'/html/body/div[7]/div/div[1]/a')
        cross.click()
        time.sleep(2)
    except:
        pass
    texttype=driver.find_element(By.XPATH,'//*[@title="Type your Message..."]/div')
    texttype.send_keys(prompt)
    time.sleep(2)
    driver.find_element(By.XPATH,'//div[@id="send-reply-span"]').click()
    time.sleep(2)
    return 1
    
# Function to check the first <p><strong> element that contains 'mins ago'
def check_time_and_execute(driver):
    try:
        time_element = driver.find_element(By.XPATH, "//p/strong[contains(text(),'mins ago')]")
        time_text = time_element.text

        minutes = int(time_text.split()[0])  # Get the number part
        
        if minutes < 5:
            
            print("0")
            contact_buyer_button = driver.find_element(By.XPATH, "//span[text()='Contact Buyer Now']")
            contact_buyer_button.click()
            print("Clicked the first 'Contact Buyer Now' button.")
            
            # subprocess.run(["python3", "c:/Users/Administrator/Desktop/myproject/Scraper/click.py"])  # Runs another script
            return 1  # Return 1 if script is run

        print("Time is 5 minutes or more, no action taken.")
        return 0  # Return 0 if no action is taken

    except Exception as e:
        print("mins ago not found")
        return 0  # Return 0 in case of error


from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import time
import subprocess
import sys
from threading import Event
# Import user_logs from the views
from accounts.log_store import user_logs
# Main Selenium function to execute the script
india_click=False
click_result=1
def run_selenium_script(port_number, username, category_keywords, rejected_keywords, quantity,stop_event,message_prompts):
    global india_click,click_result
    url = "https://seller.indiamart.com/bltxn/?pref=recent"
    if stop_event is None:
        stop_event = Event()  # Create an event if none was provided

    # Initialize success and failure counters
    success_counter = quantity
    failure_counter = 0
    max_counter = 0  # Or fetch from config if needed

    # Initialize logs for the user
    if username not in user_logs:
        user_logs[username] = []

    def log_message(message):
        user_logs[username].append(message)
        print(message)

    # Rest of your selenium logic, calling log_message at key steps
    log_message("Process started...")
    print(message_prompts)
    # Function to refresh the page
    def refresh_page(url):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"localhost:{port_number}")
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Edge(options=options)
        try:
            driver.get(url)
            time.sleep(4)
            try:
                driver.find_element(By.XPATH,'/html/body/div[5]/div[2]/div[1]/div[2]/div[2]/button[1]').click()
            except:
                pass
            try:
                driver.find_element(By.XPATH,'//*[@id="blmain_div"]/section/div[1]/div/ul/li[2]/a').click()
            except:
                driver.refresh()
                pass
            
            # log_message("Page refreshed successfully.")
            
            return driver
        except WebDriverException as e:
            log_message(f"An error occurred while refreshing the page: {e}")
            return None
    
    # def open_chrome(port_number):
    #     chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust path to your chrome.exe
    #     user_data_dir = f"C:/Chrome session_{port_number}"  # Use a port-specific user data directory
        
    #     chrome_command = [
    #         chrome_path,
    #         f"--remote-debugging-port={port_number}",
    #         f"--user-data-dir={user_data_dir}"
    #     ]
    #     subprocess.Popen(chrome_command)
    
    def open_chrome(port_number):
        chrome_path = "/usr/bin/google-chrome"  # Path to Chrome on Ubuntu
        user_data_dir = f"/tmp/chrome_session_{port_number}"  # Use a port-specific user data directory

        chrome_command = [
            chrome_path,
            f"--remote-debugging-port={port_number}",
            f"--user-data-dir={user_data_dir}",
            "--no-sandbox",  # Use --no-sandbox if you're running as root
            "--disable-gpu",  # Disable GPU usage (often useful on servers)
            # "--headless"  # Run in headless mode for servers without a display
        ]

        subprocess.Popen(chrome_command)
    #     # Main loop
    open_chrome(port_number)

    while success_counter > max_counter:
        if stop_event.is_set():  # Check if the stop event is set
            log_message("process stopped by user request.")
            break  # Exit the loop if the stop event is set

        time.sleep(2)
        driver = refresh_page(url)
        wait = WebDriverWait(driver, 10)
        if driver:
            time.sleep(3)
            try:
                notification_text = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[2]/p').text

                # Save the notification in the database
                user = User.objects.get(username=username)  # Replace with the correct user logic
                Notification.objects.create(user=user, message=notification_text)
            except Exception as e:
                # print(e)
                pass
            if not india_click:
                click_result = click_india_label(driver)
                india_click=True

            
            if click_result == 0:
                time.sleep(3)
                refresh_result_2 = refresh_page(url)
                
                if refresh_result_2:
                    time.sleep(3)
                    message_sent=goto_lead(driver,message_prompts)
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

                                max_counter += 1
                                try:
                                    span_element = wait.until(
                                        EC.visibility_of_element_located(
                                            (By.XPATH, '//span[contains(@style,"cursor: pointer") and contains(@style,"color: rgb(42, 166, 153);")]')
                                        )
                                    )
                                    span_text = span_element.text
                                    print(span_text)  # Output the text of the span element
                                except :
                                    span_text=''
                                    print("green Element not found within the time limit.")
                                # log_message(f"Title : {span_text}")
                                # h2_element = driver.find_element(By.TAG_NAME, "h2")
                                # h2_text = h2_element.text
                                # log_message(f"Heading : {h2_text}")
                                log_message("Contact Clicked")
                                print(f"Successful run count: {success_counter}/{max_counter}")
                                # log_message(f"Successful run {success_counter}/{max_counter}")

                                message_sent=goto_lead(driver,message_prompts)
                                if message_sent ==1:
                                    log_message("message sent sucessfully")

                                    driver.find_element(By.XPATH, "//div[text()='View More']").click()
                                    time.sleep(3)
                                    try:
                                        product_text = driver.find_element(By.XPATH,'//*[@id="root"]/div[6]/div/div/section/div/div/aside/div[3]/div[1]/li/span[2]').text
                                            
                                        # phone_number_text = driver.find_element(By.XPATH, '//*[@id="contactHeader"]/div[2]/span[2]/span').text
                                        name_text = driver.find_element(By.XPATH, '//*[@id="left-name"]').text
                                        # email_text = driver.find_element(By.XPATH, '//*[@id="contactHeader"]/div[2]/span[3]/span').text
                                        # location_text = driver.find_element(By.XPATH, '//*[@id="contactHeader"]/div[2]/span[4]/span').text

                                        spans=driver.find_elements(By.XPATH,'//*[@id="contactHeader"]/div[2]/span/span')
                                        # Initialize variables for storing contact information
                                        email, phone, location = None, None, None

                                        for span in spans:
                                            text = span.text
                                            if '@' in text:  # Check if it's an email
                                                email = text
                                            elif any(char.isdigit() for char in text):  # Check if it's a phone number
                                                phone = text
                                            elif ',' in text:  # Check if it's a location
                                                location = text
                                        user = User.objects.get(username=username)
                                        account = IndiaMartAccount.objects.get(user=user)
                                        lead = IndiaMartLead(
                                            account=account,
                                            product=product_text,
                                            phone_number=phone,
                                            name=name_text,
                                            email=email,
                                            location=location
                                        )
                                        lead.save()  # Save the lead to the database


                                    except:
                                        print('error in saving lead')
                                        pass
                            else:
                                failure_counter += 1
                                print(f"Unsuccessful run count: {failure_counter}")
                                driver.save_screenshot('Unsuccessful1.png')
                        else:
                            failure_counter += 1
                            print(f"Unsuccessful run count: {failure_counter}")
                            driver.save_screenshot('Unsuccessful2.png')
                            # sys.exit(h2_result)  # Exit if the <h2> check fails
                    else:
                        failure_counter += 1
                        print(f"Unsuccessful run count: {failure_counter}")
                        # sys.exit(span_result)  # Exit if the span check fails
                else:
                    failure_counter += 1
                    print(f"Unsuccessful run count: {failure_counter}")
                    # sys.exit(1)  # Exit if the second refresh fails
            else:
                failure_counter += 1
                print(f"Unsuccessful run count: {failure_counter}")
                # sys.exit(click_result)  # Exit if clicking the label fails
        else:
            failure_counter += 1
            print(f"Unsuccessful run count: {failure_counter}")
            # sys.exit(1)  # Exit if the first page refresh fails
            # log_message("Failed to refresh the page.")
            # break

    # log_message(f"Process execution completed. Successes: {success_counter}, Failures: {failure_counter}")
    driver.quit()
