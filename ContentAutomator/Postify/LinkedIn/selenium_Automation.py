import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import  time
from selenium.webdriver.chrome.options import Options

# Set Chrome options for running in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
from selenium.webdriver.common import by

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.linkedin.com")
time.sleep(10)
email=driver.find_element('xpath',"//input[@name = 'session_key']")
password=driver.find_element('xpath',"//input[@name = 'session_password']")

email.send_keys("youremail@gmail.com") # replace with your email
time.sleep(3)
password.send_keys("yourpassword") # replace with your password
time.sleep(3)
login_button = driver.find_element('xpath','//button[@type="submit"]')
login_button.click()
time.sleep(3)
# input("Please complete any security checks and press Enter to continue...")


company_url = 'https://www.linkedin.com/company/<yourLinkedInCompanyURL>/'  # Update with your linkedin company URL
driver.get(company_url)
time.sleep(10)
post_content = 'Your post content here3'

post_input = driver.find_element('xpath','/html/body/div[5]/div[3]/div[1]/div/div[2]/div[1]/div[3]/div/div[2]/main/div/div[1]/div/div[2]/div[2]/button').click()

time.sleep(3)

post_text = driver.find_element('xpath', '/html/body/div[3]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div/div[1]')
post_text.send_keys(post_content)
post_button = driver.find_element('xpath','/html/body/div[3]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/button/span')
post_button.click()
time.sleep(5)
post_button = driver.find_element('xpath','/html/body/div[3]/div/div/div[3]/button/span').click()

time.sleep(5)
print("posted successfully")
driver.quit()