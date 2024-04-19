import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
import requests
from urllib.parse import urlparse, parse_qs, urljoin
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from scipy.spatial.distance import cosine
import itertools
import re
from bs4 import BeautifulSoup
from PIL import Image
import imagehash
import sys
import tkinter as tk
from tkinter import filedialog

class Screenshot:
    semaphore = threading.Semaphore(10)

    @staticmethod
    def convert_url(url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        parsed_url = urlparse(url)
        if not parsed_url.netloc.startswith("www."):
            url = parsed_url.scheme + "://www." + parsed_url.netloc + parsed_url.path
        return url

    @staticmethod
    def take_screenshot(url, screenshot_path):
        driver = None
        with Screenshot.semaphore:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
            driver.set_page_load_timeout(20)
            driver.get(url)
            time.sleep(1)
            driver.save_screenshot(screenshot_path)
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error while closing the browser: {e}")


class VisualAnalysis:
    def __init__(self, original_pic, test_pic):
        self.original_pic = original_pic
        self.test_pic = test_pic
        self.model = self._initialize_model()
        self.similarity_score = None

    def _initialize_model(self):
        base_model = VGG16(weights='imagenet', include_top=False)
        return base_model

    def _preprocess_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array

    def calculate_similarity(self):
        features1 = self._extract_features(self.original_pic)
        features2 = self._extract_features(self.test_pic)
        similarity_score = 1 - cosine(features1, features2)
        return similarity_score

    def _extract_features(self, img_path):
        img_array = self._preprocess_image(img_path)
        features = self.model.predict(img_array)
        return features.flatten()

class FaviconDownloader:
    def __init__(self, website_urls, output_folder):
        self.website_urls = website_urls
        self.output_folder = output_folder

    def download_favicon(self, url, output_image_path):
        try:
            favicon_url = Screenshot.convert_url(url)
            response = requests.get(favicon_url)
            response.raise_for_status()
            with open(output_image_path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading favicon {favicon_url}: {e}")

    def get_favicons_and_download(self, url):
        try:
            website_url = Screenshot.convert_url(url)
            response = requests.get(website_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            favicon_links = []
            domain = urlparse(website_url).netloc

            for link in soup.find_all('link', rel=['favicon', 'icon', 'shortcut icon', 'SHORTCUT ICON', 'Shortcut Icon']):
                favicon_url = link.get('href')
                if favicon_url:
                    favicon_links.append(urljoin(website_url, favicon_url))

            for i, favicon_url in enumerate(favicon_links, start=1):
                output_image_path = f"{self.output_folder}/{domain}.png"
                self.download_favicon(favicon_url, output_image_path)
        except Exception as e:
            print(f"Error fetching favicons for {website_url}: {e}")

    def download_all_favicons(self):
        threads = []
        for website_url in self.website_urls:
            t = threading.Thread(target=self.get_favicons_and_download, args=(website_url,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
    
    def favicon_analysis():
        ori = [f for f in os.listdir("Favicons/original")]
        tes = [g for g in os.listdir("Favicons/test")]
        for f in ori:
            for g in tes:
                hash1 = imagehash.average_hash(Image.open(f'Favicons/original/{f}'))
                hash2 = imagehash.average_hash(Image.open(f'Favicons/test/{g}'))
                diff = hash1 - hash2
                print(f'Testing Favicons for {f[:-4]} x {g[:-4]}')
                print('Similarity: ', diff)
            

class VisualSimilarityChecker:
    def __init__(self, original_urls, test_urls):
        self.original_urls = original_urls
        self.test_urls = test_urls

    def capture_screenshots(self, urls, folder):
        threads = []
        working_links = []

        for i, url in enumerate(urls, start=1):
            try:
                url = Screenshot.convert_url(url)
                response = requests.get(url)
                screenshot_path = f"{folder}/{i}.png"
                t = threading.Thread(target=Screenshot.take_screenshot, args=(url, screenshot_path))
                t.start()
                threads.append(t)
                working_links.append(url)
                if len(threads) >= 15:
                    for t in threads:
                        t.join()
                    threads = []
            except requests.exceptions.RequestException as e:
                print("\nWebsite not reachable: ", url)

        for t in threads:
            t.join()

        return working_links

    def check_visual_similarity(self, original_links, test_links):
        similarity_dict = {}
        for i, original_url in enumerate(original_links, start=1):
            print("\n CHECKING VISUAL SIMILARITY FOR", original_url)
            original_path = f"Screenshots/original/{i}.png"
            if os.path.exists(original_path):
                for j, test_url in enumerate(test_links, start=1):
                    test_path = f"Screenshots/test/{j}.png"
                    if os.path.exists(test_path):
                        print("\nChecking Visual Similarity between:", original_url, " and ", test_url)
                        website_analysis = VisualAnalysis(original_path, test_path)
                        similarity_score = website_analysis.calculate_similarity()
                        print("Visual Similarity Score: ", int(100 * similarity_score), "%")
                        key = original_url + " x " + test_url
                        similarity_dict[key] = [similarity_score]
                    else:
                        continue
        return similarity_dict


class URLComparator:
    def __init__(self, url1, url2):
        self.url1 = url1
        self.url2 = url2

    def extract_domain_parts(self, url):
        url = Screenshot.convert_url(url)
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if match:
            domain = match.group(1)
            parts = domain.split('.')
            return parts
        return None

    def calculate_string_similarity(self, str1, str2):
        m = len(str1)
        n = len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        max_len = max(len(str1), len(str2))
        similarity = 1 - (dp[m][n] / max_len)
        return similarity

    def get_tld_similarity_score(self):
        parts1 = self.extract_domain_parts(self.url1)
        parts2 = self.extract_domain_parts(self.url2)
        if parts1 is not None and parts2 is not None:
            tld_similarity = self.calculate_string_similarity(parts1[-1], parts2[-1])
            return tld_similarity
        else:
            return None

    def get_domain_name_similarity_score(self):
        parts1 = self.extract_domain_parts(self.url1)
        parts2 = self.extract_domain_parts(self.url2)
        parts1.pop(-1)
        parts2.pop(-1)
        parts1 = ''.join(parts1)
        parts2 = ''.join(parts2)

        if parts1 is not None and parts2 is not None:
            domain_name_similarity = self.calculate_string_similarity(parts1, parts2)
            return domain_name_similarity
        else:
            return None

def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def clean_mess(file_path):
    files = [f for f in os.listdir(file_path)]

    for f in files:
        os.remove(os.path.join(file_path, f))

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"Folder '{folder_path}' not found.")
    except PermissionError:
        print(f"Permission denied when trying to delete '{folder_path}'.")
    except OSError as e:
        print(f"Error occurred when deleting '{folder_path}': {e}")


def init_folder(folder):
    path = os.path.join(os.getcwd(), folder)
    if not os.path.exists(path):
        os.mkdir(path)

def get_file_path():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select a text file", filetypes=[("Text Files", "*.txt")])
    root.destroy()

    return file_path


if __name__ == "__main__":

    original_shots = "Screenshots/original"
    test_shots = "Screenshots/test"
    original_cons = "Favicons/original"
    test_cons = "Favicons/test"

    print("\n\n  ___________________________________   \n /   _____/\_   _____/   __   \   _  \  \n \_____  \  |    __) \____    /  /_\  \ \n /        \ |     \     /    /\  \_/   \ \n/_________/ \_____/    /____/  \_______/\n\n\n")
    
    input("Please Select VALID file containing original websites [Press Enter] ")
    original = get_file_path()

    input("Please Select VALID file containing database websites [Press Enter] ")
    database = get_file_path()
    
    try:
        with open(original, 'r') as file:
            original_urls = read_urls_from_file(original)
    except FileNotFoundError:
        print("File not found. Please make sure the file name is correct.")
        sys.exit()
    except Exception as e:
        print("An error occurred:", e)
        sys.exit()

    try:
        with open(database, 'r') as file:
            test_urls = read_urls_from_file(database)
    except FileNotFoundError:
        print("File not found. Please make sure the file name is correct.")
        sys.exit()
    except Exception as e:
        print("An error occurred:", e)
        sys.exit()
    
    url_similarity = {}
    visual_similarity = {}

    while(True):
        print("\n")
        print("1. URL Similarity Analysis")
        print("2. Visual Similarity Analysis")
        print("3. Favicon Similarity Analysis")
        print("4. Exit")

        choice = int(input("\nEnter Choice: "))
        if choice == 1:
            print("\n Starting URL Analysis")
            for original_url in original_urls:
                print("\n\n\tCHECKING URL SIMILARITY FOR", original_url)
                for test_url in test_urls:
                    key = original_url + " x " + test_url
                    url_comparator = URLComparator(original_url, test_url)
                    tld_similarity = url_comparator.get_tld_similarity_score()
                    domain_name_similarity = url_comparator.get_domain_name_similarity_score()
                    print("\nComparing: ", original_url + " and " + test_url)
                    # print("Top Level Domain Similarity: ", int(tld_similarity * 100), "%")
                    print("Domain Name Similarity: ", int(domain_name_similarity * 100), "%")

        elif choice == 2:
            init_folder("Screenshots")
            init_folder(test_shots)
            init_folder(original_shots)
            print("\n Starting Visual Analysis")
            visual_similarity_checker = VisualSimilarityChecker(original_urls, test_urls)   
            working_links_original = visual_similarity_checker.capture_screenshots(original_urls, original_shots)
            working_links_test = visual_similarity_checker.capture_screenshots(test_urls, test_shots)
            visual_similarity = visual_similarity_checker.check_visual_similarity(original_urls, test_urls)
            clean_mess(original_shots)
            clean_mess(test_shots)
            delete_folder("Screenshots")

        elif choice == 3:
            init_folder("Favicons")
            init_folder(test_cons)
            init_folder(original_cons)
            print("\n Starting Favicon Analysis")
            print("Downloading database favicons")
            favicon_downloader = FaviconDownloader(test_urls, test_cons)
            favicon_downloader.download_all_favicons()
            favicon_downloader = FaviconDownloader(original_urls, original_cons)
            favicon_downloader.download_all_favicons()
            FaviconDownloader.favicon_analysis()
            clean_mess(original_cons)
            clean_mess(test_cons)
            delete_folder("Favicons")

        elif choice == 4:
            break

        else:
            print("Invalid Choice")
            break