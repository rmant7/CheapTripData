import json
import traceback
import urllib
from tkinter import Image

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import  time
from selenium.webdriver.chrome.options import Options
import requests
from io import BytesIO
# Set Chrome options for running in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Enable headless mode
from selenium.webdriver.common import by
chrome_options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(r"C:\Users\faisal\Downloads\chromedriver_win32\chromedriver.exe",options=chrome_options)

def page_post(url,retry,email_ ,password_,text,image_path):

    try:
        driver.get("https://www.linkedin.com")
        time.sleep(3)

        email=driver.find_element(By.XPATH,"//input[@name = 'session_key']")
        password=driver.find_element(By.XPATH,"//input[@name = 'session_password']")

        email.send_keys(email_) # replace with your email
        time.sleep(3)
        password.send_keys(password_) # replace with your password
        time.sleep(3)
        login_button = driver.find_element(By.XPATH,'//button[@type="submit"]')
        login_button.click()
        time.sleep(3)
        # input("Please complete any security checks and press Enter to continue...")


        # company_url = 'https://www.linkedin.com/company/94836531/'  # Update with your company URL
        #company_url= 'https://www.linkedin.com/groups/9379071/'
        company_url = url
        driver.get(company_url)
        time.sleep(3)


        post_data = text


        post_input = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--muted artdeco-button--4 artdeco-button--tertiary ember-view share-box-feed-entry__trigger']")
        time.sleep(3)                                               #artdeco-button artdeco-button--muted artdeco-button--4 artdeco-button--tertiary ember-view share-box-feed-entry__trigger
        post_input.click()
        time.sleep(3)
        post_text = driver.find_element(By.XPATH, "//div[@class='ql-editor ql-blank']")
        post_text.send_keys(post_data)
        time.sleep(3)
        # image_button = driver.find_element(By.XPATH,"//button[@class='artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view']")
        # image_button.click()
        # time.sleep(3)
        image_input = driver.find_element(By.XPATH,"//ul[@class='artdeco-carousel__slider ember-view']/li[1]")
        image_input.click()
        time.sleep(3)
        #<input id="image-sharing-detour-container__file-input" class="image-sharing-detour-container__media-button visually-hidden" name="file" multiple="" filecountlimit="20" accept="image/gif,image/jpeg,image/jpg,image/png" type="file">
        image_url= driver.find_element(By.XPATH,"//input[@class='image-sharing-detour-container__media-button visually-hidden']")
        image_url.send_keys(image_path)
        time.sleep(3)
        done_button= driver.find_element(By.XPATH,"//button[@class='share-box-footer__primary-btn artdeco-button artdeco-button--2 artdeco-button--primary ember-view']").click()
        time.sleep(3)


        post_button = driver.find_element(By.XPATH,"//button[@class='share-actions__primary-action artdeco-button artdeco-button--2 artdeco-button--primary ember-view']")
        post_button.click()
        time.sleep(20)
        #post_button = driver.find_element('xpath','/html/body/div[3]/div/div/div[3]/button/span').click()
        print("posted!")
        driver.quit()
    except Exception as e:
        print("error accured")
        error_message = traceback.format_exc()  # Get the formatted error message
        with open("error_log.txt", "w") as file:
            file.write(error_message)
        if retry>0:
            page_post(url,retry-1,email_,password_,text,image_path)



page_url="https://www.linkedin.com/company/94836531/admin/"
email="youremail@gmail.com"
password="your password"
image_path=r"C:\Users\faisal\PycharmProjects\automateLinkedInPosts\image.jpg"

with open('text.json', 'r') as file:
    data = json.load(file)

text = data['text']
hashtags = data['hashtags']
location = data['location']

post_text = f"{text}\n\n{', '.join(hashtags)}\n\nLocation: {location}"

page_post(page_url, 5,email,password,post_text,image_path)
