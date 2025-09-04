from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


driver = None


def extract_urls_from_xpath(url):
    driver.get(url)
    sleep(3)
    a_tags = driver.find_elements(
        By.XPATH,
        '//*[contains(concat( " ", @class, " " ), concat( " ", "c-jobListView__titleLink", " " ))]',
    )
    urls = [a_tag.get_attribute("href") for a_tag in a_tags]
    return urls


def get_cleaned_a_texts(url):
    driver.get(url)
    sleep(2)
    try:
        container = driver.find_element(
            By.XPATH,
            '//*[contains(concat( " ", @class, " " ), concat( " ", "o-box--padded", " " ))]',
        )

        elements = container.find_elements(By.TAG_NAME, "div")

        cleaned_texts = []
        for elem in elements:
            text = elem.text.strip()
            if text:
                cleaned_texts.append(text)
    except Exception as e:
        print(e)
        return []

    return cleaned_texts


def contains_go_terms(strings_list):
    target_terms = ["Go", "Golang", "golang", "go", "GO","گولنگ"]
    for s in strings_list:
        for term in target_terms:
            pattern = r"\b{}\b".format(re.escape(term))
            if re.search(pattern, s):
                return True
    return False


def increment_page(url: str) -> str:
    # Parse the URL into its components
    parsed_url = urlparse(url)
    # Extract the query parameters into a dictionary
    query_params = parse_qs(parsed_url.query)

    # Check if 'page' parameter exists and process it
    if "page" in query_params:
        # Get the last occurrence of the 'page' parameter
        last_page_value = query_params["page"][-1]
        try:
            new_page = int(last_page_value) + 1
        except ValueError:
            # Handle non-integer page values by defaulting to 2
            new_page = 2
    else:
        # Add 'page' parameter starting at 2 if it doesn't exist
        new_page = 2

    # Update the query parameters with the new page value
    query_params["page"] = [str(new_page)]

    # Rebuild the query string
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct the URL with the updated query
    updated_url = urlunparse(parsed_url._replace(query=new_query))

    return updated_url


def jobinja_login():
    # Navigate to login page
    driver.get("https://jobinja.ir/login/user")

    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="identifier"]'))
        )
        username_field.send_keys("<EMAIL>")

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        password_field.send_keys("<PASSWORD>")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="sign-in"]/div/div/div[1]/form/div[2]/div/input[4]')
            )
        )
        login_button.click()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e


def get_driver_path():
    cache_file = "chromedriver_path.txt"

    # If we already saved the driver path before, just load it
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            path = f.read().strip()
        if os.path.exists(path):
            return path

    # Otherwise, install (requires VPN the first time)
    path = ChromeDriverManager().install()

    # Save for next time
    with open(cache_file, "w") as f:
        f.write(path)

    return path


def initialize_driver():
    driver_path = get_driver_path()
    service = ChromeService(executable_path=driver_path)
    return webdriver.Chrome(service=service)


if __name__ == "__main__":
    init_url = "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1?&sort_by=published_at_desc"

    driver = initialize_driver()
    print("got the driver", driver)
    jobinja_login()

    urls = extract_urls_from_xpath(init_url)

    pages_to_scan = 3
    for i in range(pages_to_scan):
        init_url = increment_page(init_url)
        urls.extend(extract_urls_from_xpath(init_url))

    for url in urls:
        if contains_go_terms(get_cleaned_a_texts(url)):
            print(url)
            print("==" * 50)
            print("\n\n")
