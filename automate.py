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
from google import genai
import pathlib
import httpx
import ast



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
        EC.presence_of_element_located((By.CLASS_NAME, "organization__members--title")) 
    )
    print("Login detected. Saving cookies...")
    cookies = driver.get_cookies()
    with open(cookie_file, "wb") as f:  # Save cookies to local file for future sessions
        pickle.dump(cookies, f)
    print("Cookies saved.")

# Go to extraction site
driver.get("https://app.covidence.org/reviews/446621/extraction/index?filter%5Bstatus%5D=NOT_STARTED")




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
        # Find the nearest parent element with an <h2> inside it
        container = link.find_element(By.XPATH, "./ancestor::*[.//h2][1]")
        h2 = container.find_element(By.TAG_NAME, "h2")
        title_text = h2.text  #title of article 
        
        link.click()  # Click the link
    except Exception as e:
        print(f"Error extracting title or clicking link: {e}")
        # Fallback: Try JavaScript click
        try:
            driver.execute_script("arguments[0].click();", link)
        except Exception as js_error:
            print(f"JS click also failed: {js_error}")

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

client = genai.Client(api_key="SHHHHHHH")




print(f"TITLE OF ARTICLE: {title_text}")
article = input("Enter link or PDF file path: ")

if article.lower().endswith("pdf"):
    filepath = pathlib.Path('file.pdf')
    filepath.write_bytes(httpx.get(article).content)
else:
    pass


prompt = f'''


You will be given a link or pdf file path, answer all these questions in the same format everytime (python dictionary format to be easy scraped with code)

question 2: Last name first initial (e.g., Harry T) 

question 3: Research objective: List the research objective(s) from the abstract verbatim in this cell, starting with the verb. Do not start with a preposition (‘to’). 

question 4: Canada only or multiple countries including Canada? (return true or false bool)

question 5: If you selected multiple countries including Canada above (i.e if false bool), make a list of all the other countries for ex. ["australia", "Germany", "Canada"]

question 6: Indicate the province(s)/territor(ies) if available: (just list the available provinces seperated by commas in a list for ex. ["australia", "Germany", "Canada"]) Alberta British Columbia Manitoba New Brunswick Newfoundland and Labrador Northwest Territories Nova Scotia Nunavut Ontario Prince Edward Island Quebec Saskatchewan Yukon Not reported 

question 7: Abstract: Search the article on Google and copy and paste the abstract verbatim here. 

question 8: list all concepts mentioned in the abstract only from these options: experience, patient reported experience measures (PREMs), engagement, preference, perspective (or beliefs, views, attitudes), communication, decision-making, patient satisfaction, patient barriers ,patient reported outcome measures (PROMs), quality of life , Other, if Other: list the other ones


question 9: Identify the medical specialt(ies) or if it is a condition, identify the specialty most related to the condition from the list below. This should be easily identifiable from the abstract. Allergy and immunology, Anesthesiology ,Cardiology, Dermatology, Emergency medicine ,Endocrinology ,Family medicine/primary care ,Gastroenterology ,Geriatrics,Hematology, Infectious disease ,Medical genetics,Nephrology ,Neurology, Obstetrics and Gynecology (OB/GYN), Oncology, Opthalmology ,Otolaryngology (ENT-ear, nose, throat), Palliative/end-of-life care ,Pathology, Pediatrics, Physical medicine and rehabilitation, Psychiatry ,Pulmonology, Radiology, Rheumatology, Other, (if other, list the other ones/one) 


ALL LISTS SHOULD BE IN THE STANDARD PYTHON LIST FORMAT: ["hey", "hi", "bye"]  NOT ["hey"], ["hi"], ["bye"]
{article}
'''

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)



data = response.text.replace("```python", "").replace("```", "")



data_dict = ast.literal_eval(data)

with open("output.txt", "w", encoding="utf-8") as file:
    file.write(data)



# Wait for input box and enter data
# Wait for input box and enter data
try:
    input_element_1 = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "webpack-concepts-Extraction-Blocks-shared-BlockWidgets-module__Input"))
    )
    
    input_element_1.send_keys(title_text + Keys.ENTER)
    
    input_element_2 = driver.find_element(By.ID, "fea98d66-7f3a-4974-9658-bf4d55b391e6")
    input_element_2.send_keys(data_dict["question 2"] + Keys.ENTER)

    input_element_3 = driver.find_element(By.ID, "44e7db4f-d0c5-4673-bc12-c34b07926560")
    input_element_3.send_keys(data_dict["question 3"] + Keys.ENTER)

    input_element_4a = driver.find_element(By.XPATH, "//span[text()='Canada only']")
    input_element_4b = driver.find_element(By.XPATH, "//span[text()='Multiple countries including Canada']")

    if data_dict["question 4"] == True:
        input_element_4a.click()
    else:
        input_element_4b.click()
        input_element_5 = driver.find_element(By.ID, "819348b8-f7c3-4f94-bd6a-aff6bc073ad4")
        
        input_element_5.send_keys(data_dict["question 5"] + Keys.ENTER)

    
    
    provinces = data_dict["question 6"]

    
    
    for province in provinces:
        input_element_6 = driver.find_element(
        By.XPATH,
        f'//span[@class="webpack-concepts-Extraction-Blocks-Checkboxes-BaseCheckboxes-module__optionLabelText" and text()="{province}"]'
    )
        input_element_6.click()
    
    
    input_element_7 = driver.find_element(By.ID, "2f459861-31e5-4bfc-a0df-fa72540df611")
        
    input_element_7.send_keys(data_dict["question 7"] + Keys.ENTER)
    
    
    concepts = data_dict["question 8"]
    for concept in concepts:
        input_element_8 = driver.find_element(
        By.XPATH,
        f'//span[@class="webpack-concepts-Extraction-Blocks-Checkboxes-BaseCheckboxes-module__optionLabelText" and text()="{concept}"]'
    )
        input_element_8.click()
        
    
    specialities = data_dict["question 9"]
    for speciality in specialities:
        input_element_9 = driver.find_element(
        By.XPATH,
        f'//span[@class="webpack-concepts-Extraction-Blocks-Checkboxes-BaseCheckboxes-module__optionLabelText" and text()="{speciality}"]'
    )
        input_element_9.click()
    
    


    

except TimeoutException:
    pass
except Exception as e:
    print(f"Error: {str(e)}")

# script completed 

print("SCRIPT COMPLETE... CLOSING IN 60 SEC")

time.sleep(60)
driver.quit()
