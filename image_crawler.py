import json
import os
import requests
import time
import re
import logging
import concurrent.futures
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

# Constants and Configurations
BASE_DIR = './background_transformed/train/image/'
OUTPUT_DIR = './background/train/image/'
MAX_NUM_IMAGES = 15
WAIT_TIME = 10
SCROLL_PAUSE_TIME = 1
IMAGE_CACHE = set()
MAX_THREADS = 16

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def natural_sort_key(s): 
    """
    Generate a sorting key for a given string to enable natural order sorting.

    Args:
        s (str): The string to be sorted.

    Returns:
        list: A list containing a mix of integers and strings for natural sorting.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def download_image(url, folder_path, image_number):
    """
    Download an image from a URL and save it to a specified folder without overwriting existing files.

    Args:
        url (str): URL of the image to download.
        folder_path (str): Path of the folder to save the downloaded image.
        image_number (int): Image number used for naming the saved file.
    """

    image_file_path = os.path.join(folder_path, f"{image_number}.jpg")
    if os.path.exists(image_file_path) or url in IMAGE_CACHE:
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(image_file_path, 'wb') as file:
            file.write(response.content)
        IMAGE_CACHE.add(url)
    except Exception as e:
        logging.error(f"Failed to download {url}. Error: {e}")

def download_images_concurrently(image_urls, output_folder):
    """
    Download multiple images concurrently from a list of URLs and save them to a specified folder.

    Args:
        image_urls (list[str]): List of image URLs to download.
        output_folder (str): Path of the folder to save the downloaded images.
    """

    os.makedirs(output_folder, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(download_image, url, output_folder, i+1)
                   for i, url in enumerate(image_urls)]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Handle exceptions inside download_image

def scroll_to_load_images(driver):
    """
    Scroll through a webpage to dynamically load all images.

    Args:
        driver (webdriver): Selenium WebDriver used for automated webpage navigation.
    """
    # Function body...

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 2);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def search_and_download_similar_images(image_path, driver, output_folder):
    """
    Search for similar images using a specified image path and download them using a Selenium WebDriver.

    Args:
        image_path (str): Path to the image used for searching similar images.
        driver (webdriver): Selenium WebDriver used for the search.
        output_folder (str): Path of the folder to save the downloaded images.
    """

    try:
        driver.get('https://www.bing.com/visualsearch')
        upload_button = WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'pstpn'))
        )
        upload_button.click()
        file_input = WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(os.path.abspath(image_path))
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.richImgLnk'))
        )
        scroll_to_load_images(driver)
        image_links = driver.find_elements(By.CSS_SELECTOR, 'a.richImgLnk')
        image_urls = [json.loads(link.get_attribute('data-m')).get('murl')
                      for link in image_links[:MAX_NUM_IMAGES] if link.get_attribute('data-m')]
        download_images_concurrently(image_urls, output_folder)
    except Exception as e:
        logging.error(f"Error during image search and download: {e}")

def process_image_categories(base_dir):
    """
    Process each image in each category within a base directory using a headless browser to search and download similar images.

    Args:
        base_dir (str): Base directory containing image categories for processing.
    """

    options = Options()
    options.headless = True
    driver = webdriver.Edge()

    try:
        categories = sorted(os.listdir(base_dir), key=natural_sort_key)
        for category in tqdm(categories, desc="Processing categories"):
            category_path = os.path.join(base_dir, category)
            if os.path.isdir(category_path):
                images = sorted(os.listdir(category_path), key=natural_sort_key)
                for img_name in tqdm(images, desc=f"Processing {category}"):
                    img_path = os.path.join(category_path, img_name)
                    output_folder = os.path.join(OUTPUT_DIR, category, os.path.splitext(img_name)[0])
                    search_and_download_similar_images(img_path, driver, output_folder)
    finally:
        driver.quit()

if __name__ == '__main__':
    process_image_categories(BASE_DIR)
