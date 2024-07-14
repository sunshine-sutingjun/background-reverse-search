# Background Reverse Search

**Background Reverse Search** is a Python tool that utilizes Selenium to perform reverse image searches on Bing. It focuses on searching for images without foreground elements (e.g., people, animals) by blurring these elements and then finding similar backgrounds. The tool automates the process of downloading images from the search results and saves them locally.

## Features

- **Automated Image Blurring:** Blurs foreground elements in images to focus on backgrounds.
- **Reverse Image Search:** Uses Selenium to automate reverse image searches on Bing.
- **Concurrent Downloads:** Efficiently downloads multiple images concurrently.
- **Organized Output:** Saves downloaded images in structured directories.

## Installation

To get started with Background Reverse Search, follow these steps:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/sunshine-sutingjun/background-reverse-search.git
   cd background-reverse-search
   ```

2. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Set up Selenium WebDriver:**
   - Download the Edge WebDriver from the [official site](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
   - Ensure the WebDriver executable is in your PATH.

## Usage

To use the tool, run the main script with Python:

```sh
python scripts/image_crawler.py
```

The script processes images from the specified base directory, performs reverse image searches, and downloads similar images. Adjust the configuration constants in the script as needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact <37220232203813@stu.xmu.edu.cn>.
