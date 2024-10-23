from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# Create an instance of Chrome with the same running instance
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=options)

# Open the target URL
driver.get("https://seller.indiamart.com/bltxn/?pref=recent")

# Wait for the page to load completely
time.sleep(5)

try:
    # Click the first span with text "Contact Buyer Now"
    contact_buyer_button = driver.find_element(By.XPATH, "//span[text()='Contact Buyer Now']")
    contact_buyer_button.click()
    print("Clicked the first 'Contact Buyer Now' button.")

except Exception as e:
    print(f"Error: {e}")

# Close the browser after completing the task
driver.quit()
