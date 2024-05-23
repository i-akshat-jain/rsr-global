import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()

COOKIES_PATH = 'auth/cookies.json'
LOCAL_STORAGE_PATH = 'auth/local_storage.json'

EMAIL = os.getenv("LINKEDIN_EMAIL", "")
PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
login_page = "https://www.linkedin.com/login"


def load_data_from_json(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
        print(f"Error loading JSON from {path}: {e}")
        return None


def save_data_to_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        json.dump(data, file)


def add_cookies(driver, cookies):
    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)


def add_local_storage(driver, local_storage):
    if local_storage:
        for k, v in local_storage.items():
            driver.execute_script(
                f"window.localStorage.setItem('{k}', '{v}');")


def get_first_folder(path):
    return os.path.normpath(path).split(os.sep)[0]


def navigate_and_check(driver, probe_page):
    driver.get(probe_page)
    time.sleep(5)  # Wait for the page to load

    # Get the current URL
    current_url = driver.current_url

    # Check if the current URL matches the expected URL after successful login
    # Replace with the expected URL after successful login
    expected_url = "https://www.linkedin.com/feed/"
    if current_url == expected_url:  # return True if you are logged in successfully independent of saving new cookies
        save_data_to_json(driver.get_cookies(), COOKIES_PATH)
        save_data_to_json({key: driver.execute_script(f"return window.localStorage.getItem('{key}');")
                           for key in driver.execute_script("return Object.keys(window.localStorage);")}, LOCAL_STORAGE_PATH)
        time.sleep(5)
        return True
    else:
        return False


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            delete_folder(file_path) if os.path.isdir(
                file_path) else os.remove(file_path)
        os.rmdir(folder_path)


def login(driver, email, password):
    driver.find_element(By.ID, 'username').send_keys(email)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//*[@type="submit"]').click()


def check_cookies_and_login(driver):
    # you have to open some page first before trying to load cookies!
    driver.get(login_page)
    time.sleep(3)

    cookies = load_data_from_json(COOKIES_PATH)
    local_storage = load_data_from_json(LOCAL_STORAGE_PATH)

    if cookies and local_storage:
        add_cookies(driver, cookies)
        add_local_storage(driver, local_storage)
        time.sleep(3)
        print("cookies uploaded")
        # Use a page that is accessible only after login
        if navigate_and_check(driver, "https://www.linkedin.com/feed/"):
            return
        else:
            print("Cookies are outdated or invalid. Proceeding with manual login.")
            delete_folder(get_first_folder(COOKIES_PATH))
    else:
        print("No valid cookies or local storage data found. Proceeding with manual login.")

    driver.get(login_page)
    time.sleep(3)
    login(driver, email=EMAIL, password=PASSWORD)
    navigate_and_check(driver, "https://www.linkedin.com/feed/")
