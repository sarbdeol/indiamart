# config.py

import subprocess

# Categories of keywords to be tracked
keywordcategory = ['Couplings', 'Seals', 'Hydraulic Tools']
# Keywords that should trigger rejection
keywordsrejectheading = []
# Maximum number of successful runs before stopping
max_counter = 3  # Change this to the desired max value
# Control variable to start or stop the script
run_script = True  # Set to False to stop the script
process = None  # Initialize a global process variable

# Function to start or stop the main.py script
def run_main():
    global process
    if run_script:
        if process is None or process.poll() is not None:  # Check if process is not running
            process = subprocess.Popen(['python', 'main.py'], shell=False)
            print("main.py is running.")
        else:
            print("main.py is already running.")
    else:
        if process:
            process.terminate()  # Terminate the main.py process
            process.wait()  # Wait for the process to terminate
            print("main.py has been stopped.")
            process = None  # Reset the process variable
