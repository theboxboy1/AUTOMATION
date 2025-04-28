
# Setup

1. Go to: https://googlechromelabs.github.io/chrome-for-testing/
2. Install latest stable version of "chromedriver" by pasting link in browser

  For Intel-based macs: https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.114/mac-x64/chromedriver-mac-x64.zip

  For Arm-based macs (M-series chip: M1, M2 or M3 chip): https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.114/mac-arm64/chromedriver-mac-arm64.zip

  For Windows 64-bit: https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.114/win64/chromedriver-win64.zip

  For Linux: https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.114/linux64/chromedriver-linux64.zip

3. Unzip file and move "chromedriver.exe" file into Python file where you will keep the automation code

# Steps to use 

1. Open any IDE of your choosing (Microsoft VS code and Pycharm are good)
2. Go to terminal and input: `pip install selenium`(only need to do this once to install necessary libraries)
3. Run code by either clicking play button in top right (usually) or input `python3 automate.py` in terminal



# How it works

1. Selenium is a python library that automates alot of web things
2. First prompts you to login to get your login cookies, this code runs locally so no one can access these but you
3. Saves login cookies into "cookies.pkl" file, these last a long time (until whenever the expiry date is on the website)
4. Uses these cookies to login, automatically clicks the extraction link where all the articles are held
5. The program then keeps scrolling and clicking on "load more" until it finds an article that has yet to be extracted
6. Clicks on the extraction link for the article



# If cookies no longer work anymore....

The automatic login may not work after some time because its assoociated cookies expired. Simply find the "cookies.pkl" file located in your IDE file manager, delete it, and run code again.

![image](https://github.com/user-attachments/assets/3146dbb0-2ad6-4bf3-8a21-aa41638b5670)
