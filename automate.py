import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

# Setup
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

url = "https://app.covidence.org/reviews/active"
driver.get(url)

# Cookie file path
cookie_file = "cookies.pkl"

# If cookies file exists, load it
if os.path.exists(cookie_file):
    with open(cookie_file, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
else:
    print("Please log in manually in the browser window...")  # Let user manually login to save cookies
    # Give user time to login manually
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "webpack-concepts-Extraction-Blocks-shared-BlockWidgets-module__Input"))  # Wait for login to be detected by checking for input field
    )
    print("Login detected. Saving cookies...")
    cookies = driver.get_cookies()
    with open(cookie_file, "wb") as f:  # Save cookies to local file for future sessions
        pickle.dump(cookies, f)
    print("Cookies saved.")

# Go to extraction site
driver.get("https://app.covidence.org/reviews/446621/extraction/index")




# Function to check if "Begin extraction" link exists
def find_begin_extraction_link():
    try:
        # Try different possible selectors because Covidence uses dynamic classes sometimes
        selectors = [
            "//a[contains(text(), 'Begin extraction')]",
            "//a[@class='css-l51xn9' and contains(text(), 'Begin extraction')]",
            "//a[contains(@class, 'css-l51xn9') and contains(text(), 'Begin extraction')]",
            "//a[contains(text(), 'Begin extraction') or contains(text(), 'Continue extraction')]"
        ]

        for selector in selectors:
            try:
                links = driver.find_elements(By.XPATH, selector)
                if links:
                    return links[0]  # Return the first matching link
            except NoSuchElementException:
                continue

        return "no articles to extract"
    except Exception as e:
        return None

# Function to find and click the "Load more" button
def find_load_more_button():
    try:
        # Try different selectors for the "Load more" button
        button_selectors = [
            "//button[contains(@class, 'css-gwcxxq') and contains(text(), 'Load more')]",
            "//button[text()='Load more']",
            "//button[contains(text(), 'Load more')]"
        ]

        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    return buttons[0]
            except:
                continue

        return None
    except Exception as e:
        return None

# Main loop to keep clicking "Load more" until "Begin extraction" link is found
print("Starting to look for Begin extraction links...")

max_attempts = 30  # Maximum number of times to try loading more content
found_link = False

for attempt in range(max_attempts):
    # Check if we can find the extraction link
    link = find_begin_extraction_link()
    if link and link != "no articles to extract":
        found_link = True
        break

    # Find and click the "Load more" button
    load_more_button = find_load_more_button()

    if not load_more_button:
        # Scroll down to try to reveal the button
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(100/1000)
        load_more_button = find_load_more_button()

    if load_more_button:
        try:
            # Scroll to the button to make sure it's in view
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            time.sleep(800/1000)
            load_more_button.click()
        except StaleElementReferenceException:
            continue
        except ElementClickInterceptedException:
            try:
                driver.execute_script("arguments[0].click();", load_more_button)
            except Exception:
                pass
        except Exception:
            pass
    else:
        # Could not find 'Load more' button even after scrolling
        pass

   
    

# If we found the link, click it
if found_link:
    try:
        link.click()
    except Exception:
        # Try JavaScript click
        try:
            driver.execute_script("arguments[0].click();", link)
        except Exception:
            pass

# Wait for input box and enter data
try:
    input_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "webpack-concepts-Extraction-Blocks-shared-BlockWidgets-module__Input"))
    )
    input_element.clear()
    input_element.send_keys("tech boy" + Keys.ENTER)
except TimeoutException:
    pass
except Exception:
    pass

# script completed 
time.sleep(60)
print("SCRIPT COMPLETE... CLOSING IN 60 SEC")
driver.quit()
