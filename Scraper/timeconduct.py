from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import json

# Create an instance of Chrome with the same running instance
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=options)

# Function to check the first <p><strong> element that contains 'mins ago'
def check_time_and_execute():
    try:
        # Locate the first <p><strong> element with 'mins ago'
        time_element = driver.find_element(By.XPATH, "//p/strong[contains(text(),'mins ago')]")
        time_text = time_element.text
        #print(f"Found: {time_text}")

        # Extract the number before 'mins ago'
        minutes = int(time_text.split()[0])  # Get the number part
        
        # If time is less than 5 minutes, run another Python script
        if minutes < 5:
            print("0")
            subprocess.run(["python3", "click.py"])  # Runs another script
            return 1  # Return 1 if script is run

        else:
            print("1")
            return 0  # Return 0 if no action is taken

    except Exception as e:
        print("1")
        return 0  # Return 0 in case of error

# Start the process
result = check_time_and_execute()

# Print the result (0 or 1)
#print("0")



# Close the browser after completing the task
driver.quit()
