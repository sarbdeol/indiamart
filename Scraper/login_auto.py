from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess
def open_chrome():
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust the path to your chrome.exe
    user_data_dir = "C:/Chrome dev session"
    
    # Command to open Chrome with remote debugging
    chrome_command = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}"
    ]
    
    # Launch Chrome
    subprocess.Popen(chrome_command)
    
# Step 1: Automatically open Chrome in remote debugging mode
open_chrome()
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start browser maximized
chrome_options.add_argument("--disable-notifications")  # Disable notifications

# Set path to your WebDriver
chrome_service = Service("/path/to/chromedriver")  # Replace with your WebDriver path
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the IndiaMart Seller Login page

driver.get("https://seller.indiamart.com/bltxn/?pref=recent")

# Give time for the page to load
time.sleep(3)

# Find the login elements and interact with them
try:
    # Click on the "Login via OTP" button
    try:
        otp_login_button = driver.find_element(By.XPATH, "//input[@placeholder='Enter 10 digit mobile number']")
        otp_login_button.send_keys("9579797269") 

        time.sleep(2)
        btn = driver.find_element(By.XPATH, "//button[@class='login_btn']")
        btn.click() # Replace with your phone number
    except:
        pass
    # Wait for the login page to load
   
    time.sleep(2)
    # Enter the phone number (replace with your valid phone number)
    phone_input = driver.find_element(By.ID, "passwordbtn1")
    phone_input.click() # Replace with your phone number
    time.sleep(2)
    # Submit the form
    password=driver.find_element(By.XPATH, "//input[@placeholder='Enter Password']")
    password.clear()
    password.send_keys('Focusengg@5477')
    time.sleep(2)
    submit_button = driver.find_element(By.ID, "signWP")
    submit_button.click()

    # Wait for OTP input
    time.sleep(5)


    # After successful login, you can now proceed with other actions like navigating, scraping, or interacting further
    print("Logged in successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Optionally close the driver after the process
    time.sleep(10)
    driver.quit()
