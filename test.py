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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Constants and Configurations
BASE_DIR = './background_transformed/train/image/'
OUTPUT_DIR = './background/train/image/'
MAX_NUM_IMAGES = 15
WAIT_TIME = 10
SCROLL_PAUSE_TIME = 1  # Reduced pause time for faster scrolling
IMAGE_CACHE = set()  # Cache to store downloaded image URLs
MAX_THREADS = 5  # Maximum number of threads for ThreadPoolExecutor
MAX_RETRIES = 3  # Maximum number of retries for HTTP requests and browser interactions

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a requests.Session object with retry strategy
session = requests.Session()
retries = Retry(total=MAX_RETRIES, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def numerical_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def retryable_operation(function, *args, **kwargs):
    # [Function body remains the same]

def download_image(url, folder_path, image_number):
    """Download an image from a URL and save it to a specified folder."""
    image_file_path = os.path.join(folder_path, f"{image_number}.jpg")
    if os.path.exists(image_file_path):
        return
    try:
        response = session.get(url)
        response.raise_for_status()
        with open(image_file_path, 'wb') as file:
            file.write(response.content)
        IMAGE_CACHE.add(url)  # Add URL to cache after successful download
    except Exception as e:
        logging.error(f"Failed to download {url}. Error: {e}")

def download_images_threaded(image_urls, output_folder):
    # [Function body remains the same]

def scroll_to_load_images(driver):
    # [Function body remains the same]

def search_similar_images(image_path, driver, output_folder):
    # [Function body remains the same]

def process_categories(base_dir):
    # [Function body remains the same]

if __name__ == '__main__':
    options = Options()
    options.headless = True  # Enable headless mode
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    try:
        process_categories(BASE_DIR)
    finally:
        driver.quit()
