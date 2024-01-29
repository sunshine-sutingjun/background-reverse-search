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
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options

# Constants and Configurations
BASE_DIR = './background_transformed/train/image/'
OUTPUT_DIR = './background/train/image/'
MAX_NUM_IMAGES = 15
WAIT_TIME = 10
SCROLL_PAUSE_TIME = 1  # Reduced pause time for faster scrolling
IMAGE_CACHE = set()  # Cache to store downloaded image URLs
MAX_THREADS = 16  # Maximum number of threads for ThreadPoolExecutor

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def numerical_sort_key(s):
    """Sort function for natural order sorting."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def download_image(url, folder_path, image_number):
    """Download an image from a URL and save it to a specified folder."""
    # Ensure the output folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    image_file_path = os.path.join(folder_path, f"{image_number}.jpg")
    if os.path.exists(image_file_path):
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(image_file_path, 'wb') as file:
            file.write(response.content)
        IMAGE_CACHE.add(url)  # Add URL to cache after successful download
    except Exception as e:
        logging.error(f"Failed to download {url}. Error: {e}")


def download_images_threaded(image_urls, output_folder):
    """Download images using ThreadPoolExecutor."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(download_image, url, output_folder, i+1)
                   for i, url in enumerate(image_urls) if url not in IMAGE_CACHE]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Failed to download image: {e}")

def scroll_to_load_images(driver):
    """Scroll through the webpage to load all images with optimized scrolling."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down a bit more each time to load more content
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 2);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def search_similar_images(image_path, driver, output_folder):
    """Search for similar images using Bing Visual Search and download them using threading."""
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
        image_urls = []
        for link in image_links[:MAX_NUM_IMAGES]:
            data_m = link.get_attribute('data-m')
            if data_m:
                data = json.loads(data_m)
                img_url = data.get('murl')
                if img_url:
                    image_urls.append(img_url)
        
        download_images_threaded(image_urls, output_folder)  # Call to threaded download function
    except Exception as e:
        logging.error(f"An error occurred while searching images: {e}")

def process_categories(base_dir):
    """Process each category and image in the base directory with headless browser."""
    # Configure headless browser
    options = Options()
    options.headless = True  # Enable headless mode
    driver = webdriver.Edge()
    
    try:
        categories = sorted(os.listdir(base_dir), key=numerical_sort_key)
        for category in tqdm(categories, desc="Processing categories"):
            category_path = os.path.join(base_dir, category)
            if os.path.isdir(category_path):
                images = sorted(os.listdir(category_path), key=numerical_sort_key)
                for img_name in tqdm(images, desc=f"Processing images in {category}"):
                    img_path = os.path.join(category_path, img_name)
                    output_folder = os.path.join(OUTPUT_DIR, img_name.split('_')[0], img_name.split('.')[0])
                    if not os.path.exists(output_folder):
                        search_similar_images(img_path, driver, output_folder)
                        print(output_folder)
    finally:
        driver.quit()

if __name__ == '__main__':
    process_categories(BASE_DIR)