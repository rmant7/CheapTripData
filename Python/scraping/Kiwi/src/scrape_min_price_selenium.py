#!/usr/bin/env python3

import functools
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


seconds_waiting_between_actions = 1
seconds_waiting_result_rendered = 7

URL = "https://www.kiwi.com/en/"


def get_headless_options() -> Options:
    """Return chrome options for Selenium. Chrome options for a headless browser is enabled."""

    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"  # noqa: E501
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}  # disable images
    return chrome_options


def create_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return Chrome driver. Specify options corresponding to `headless` parameter."""

    if headless:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=get_headless_options()
        )
    else:
        options = Options()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
    return driver


def close_modal(driver: webdriver.Chrome) -> None:
    """Close the modal window."""

    driver.find_element(By.CSS_SELECTOR, 'button[data-test="ModalCloseButton"]').click()


def silent_shutdown_on_failure(scrape_func):
    """Return a decorator that silently shuts down the execution process, providing description."""

    @functools.wraps(scrape_func)
    def wrapper(*args, **kwargs):
        try:
            return scrape_func(*args, **kwargs)
        except NoSuchElementException as exc:
            sys.exit(
                f"{exc}The element was not found. Maybe the driver had no time to render results. "
                f"Consider increasing timeout parameters.\n"
                f"Otherwise a source code of a website has been changed and can not be parsed."
            )

    return wrapper


@silent_shutdown_on_failure
def scrape_min_price(
    city_from: str, city_to: str, currency_code: str = "eur", driver: webdriver.Chrome = None
) -> str:
    """
    Scrape and return a minimal price for a flight between `city_from` and `city_to`.
    Return a string, consisting of a price value and a `currency_code` like "60 €".
    """

    if driver is None:
        driver = create_chrome_driver()

    driver.get(URL)

    # close initial modal window
    close_modal(driver)
    time.sleep(seconds_waiting_between_actions)

    # choose currency
    driver.find_element(By.CSS_SELECTOR, 'button[data-test="RegionalSettingsButton"]').click()
    elem_select_currency = driver.find_element(
        By.CSS_SELECTOR, 'select[data-test="CurrencySelect"]'
    )
    elem_select_currency.find_element(By.CSS_SELECTOR, f'option[value="{currency_code}"]').click()
    driver.find_element(By.CSS_SELECTOR, 'button[data-test="SubmitRegionalSettingsButton"]').click()
    time.sleep(seconds_waiting_between_actions)

    # clear city inputs if filled by default
    try:
        for i in range(2):
            driver.find_element(
                By.CSS_SELECTOR, 'div[data-test="PlacePickerInputPlace-close"'
            ).click()
            time.sleep(seconds_waiting_between_actions)
    except NoSuchElementException:
        pass

    element_city_from = driver.find_element(
        By.CSS_SELECTOR, 'div[data-test="PlacePickerInput-origin"] > input'
    )
    element_city_to = driver.find_element(
        By.CSS_SELECTOR, 'div[data-test="PlacePickerInput-destination"] > input'
    )

    # fill in the initial and destination cities
    element_city_from.send_keys(city_from)
    time.sleep(seconds_waiting_between_actions)
    element_city_from.send_keys(Keys.ENTER)
    time.sleep(seconds_waiting_between_actions)
    element_city_to.send_keys(city_to)
    time.sleep(seconds_waiting_between_actions)
    element_city_to.send_keys(Keys.ENTER)

    # uncheck "accommodations with Booking.com" and start searching
    driver.find_element(By.CSS_SELECTOR, 'div[class|="Checkbox__StyledIconContainer"]').click()
    driver.find_element(By.CSS_SELECTOR, 'a[data-test="LandingSearchButton"]').click()
    time.sleep(seconds_waiting_result_rendered)  # ensure the site can process the request

    # look for the first price element and get the price
    elem_min_price = driver.find_element(
        By.CSS_SELECTOR, 'strong[data-test="ResultCardPrice"] > span'
    )
    return elem_min_price.get_attribute("innerText") or "Prices are not available at the moment"


if __name__ == "__main__":
    city_from = "London"
    city_to = "Paris"
    currency_code = "eur"

    driver = create_chrome_driver(headless=True)
    min_price = scrape_min_price(city_from, city_to, currency_code, driver)
    print(f"Minimal price for a flight between {city_from} and {city_to} is {min_price}")
