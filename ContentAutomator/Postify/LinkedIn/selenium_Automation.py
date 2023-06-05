import json

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import  time
from selenium.webdriver.chrome.options import Options

# Set Chrome options for running in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Enable headless mode
from selenium.webdriver.common import by
chrome_options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(r"C:\Users\faisal\Downloads\chromedriver_win32\chromedriver.exe",options=chrome_options) # add your chrome driver path
driver.get("https://www.linkedin.com")
time.sleep(3)

email=driver.find_element(By.XPATH,"//input[@name = 'session_key']")
password=driver.find_element(By.XPATH,"//input[@name = 'session_password']")

email.send_keys("youremail@gmail.com") # replace with your email
time.sleep(3)
password.send_keys("yourpassowrd") # replace with your password
time.sleep(3)
login_button = driver.find_element(By.XPATH,'//button[@type="submit"]')
login_button.click()
time.sleep(3)
# input("Please complete any security checks and press Enter to continue...")


company_url = 'https://www.linkedin.com/company/<your company id>/'  # Update with your company URL
driver.get(company_url)
time.sleep(3)


post_data = {
    "location": "your_location",
    "text": "your_text",
    "hashtags": ["#test"]
}
# Convert the JSON data to a string
post_data_string = json.dumps(post_data)

post_input = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--muted artdeco-button--4 artdeco-button--tertiary ember-view share-box-feed-entry__trigger']")
time.sleep(3)
post_input.click()
time.sleep(3)
post_text = driver.find_element(By.XPATH, "//div[@class='ql-editor ql-blank']")
post_text.send_keys(post_data_string)
time.sleep(3)
# image_button = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view']")
# image_button.click()
# time.sleep(3)

image_input = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view']")
image_input.click()
time.sleep(3)
#<input id="image-sharing-detour-container__file-input" class="image-sharing-detour-container__media-button visually-hidden" name="file" multiple="" filecountlimit="20" accept="image/gif,image/jpeg,image/jpg,image/png" type="file">
image_url= driver.find_element(By.XPATH,"//input[@class='image-sharing-detour-container__media-button visually-hidden']")
image_url.send_keys(r"C:\Users\faisal\PycharmProjects\automateLinkedInPosts\example.jpg") # replace with your relevant path
time.sleep(3)
# < button
# id = "ember906"
#
#
# class ="share-box-footer__primary-btn artdeco-button artdeco-button--2 artdeco-button--primary ember-view" type="button" > < !---->
#
# < span
#
#
# class ="artdeco-button__text" >
#
#
# Done
#
# < / span > < / button >
done_button= driver.find_element(By.XPATH,"//button[@class='share-box-footer__primary-btn artdeco-button artdeco-button--2 artdeco-button--primary ember-view']").click()
time.sleep(3)

# <button id="ember903" class="artdeco-button artdeco-button--2 artdeco-button--secondary ember-view" type="button"><!---->
# <span class="artdeco-button__text">
#     Back
# </span></button>
# back_button = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--2 artdeco-button--secondary ember-view']")
# back_button.click()
# time.sleep(3)



post_button = driver.find_element(By.XPATH,"//button[@class='share-actions__primary-action artdeco-button artdeco-button--2 artdeco-button--primary ember-view']")
post_button.click()
time.sleep(5)
#post_button = driver.find_element('xpath','/html/body/div[3]/div/div/div[3]/button/span').click()
print("posted!")
driver.quit()