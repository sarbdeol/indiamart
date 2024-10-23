from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess

def open_chrome(port_number):
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust path to your chrome.exe
    user_data_dir = f"C:/Chrome session_{port_number}"  # Use a port-specific user data directory
    
    chrome_command = [
        chrome_path,
        f"--remote-debugging-port={port_number}",
        f"--user-data-dir={user_data_dir}"
    ]
    subprocess.Popen(chrome_command)
# open_chrome('9200')
def login_to_indiamart(username, password, port_number):
    try:
        # Step 1: Automatically open Chrome with the user's port number
        open_chrome(port_number)
        
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{port_number}")

        chrome_service = Service("/path/to/chromedriver")  # Update path to chromedriver
        driver = webdriver.Chrome(options=chrome_options)

        # Step 2: Navigate to the IndiaMart Seller Login page
        driver.get("https://seller.indiamart.com/bltxn/?pref=recent")
        time.sleep(3)

        # Step 3: Enter the username and password
        otp_login_button = driver.find_element(By.XPATH, "//input[@placeholder='Enter 10 digit mobile number']")
        otp_login_button.send_keys(username)
        time.sleep(2)
        try:
            btn = driver.find_element(By.XPATH, "//button[@class='login_btn']")
            btn.click()
        except:
            pass
        time.sleep(3)
        pass_btn = driver.find_element(By.XPATH, "//*[@id='passwordbtn1']")
        pass_btn.click()
        time.sleep(2)

        time.sleep(2)
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter Password']")
        password_input.click()
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(2)

        submit_button = driver.find_element(By.ID, "signWP")
        submit_button.click()

        time.sleep(5)

        if "recent" in driver.current_url:
            print("Logged in successfully!")
            driver.quit()
            
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        time.sleep(10)
        driver.quit()
