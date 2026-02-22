#pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_sri_lankan_cars(base_url, pages_to_scrape=1):
    """
    Scrapes car data from a static HTML listing page.
    Note: Always check a website's robots.txt before scraping.
    """
    
    # Headers mimic a real browser to prevent immediate blocking by the server
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_cars = []

    for page in range(1, pages_to_scrape + 1):
        print(f"Scraping page {page}...")
        
        # Handle pagination (e.g., ?page=2). Adjust based on the target website's URL structure.
        url = base_url if page == 1 else f"{base_url}?page={page}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Check for HTTP errors
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- CRITICAL STEP ---
            # You must inspect the target website (Right-Click > Inspect) 
            # to find the actual HTML tags and classes wrapping each car listing.
            # The classes below ('listing-item', 'title', 'price') are generic placeholders.
            
            listings = soup.find_all('li', class_='item') # Example wrapper class
            
            for item in listings:
                try:
                    # Use .text.strip() to extract the readable text and remove extra whitespace
                    title = item.find('h2', class_='more').text.strip() if item.find('h2', class_='more') else 'N/A'
                    price = item.find('div', class_='price').text.strip() if item.find('div', class_='price') else 'N/A'
                    location = item.find('div', class_='location').text.strip() if item.find('div', class_='location') else 'N/A'
                    mileage = item.find('div', class_='mileage').text.strip() if item.find('div', class_='mileage') else 'N/A'
                    
                    # Only add records that actually grabbed a title
                    if title != 'N/A':
                        all_cars.append({
                            'Brand/Model': title,
                            'Price (LKR)': price,
                            'Location': location,
                            'Mileage': mileage
                        })
                except AttributeError:
                    # Skip items that don't match the expected structure
                    continue
            
            # Be polite to the server: Pause between requests to avoid overloading it
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve page {page}: {e}")
            break

    return all_cars

def save_to_csv(data, filename='srilanka_cars.csv'):
    """Saves a list of dictionaries to a CSV file."""
    if not data:
        print("No data was extracted to save.")
        return
        
    # Extract headers from the keys of the first dictionary
    keys = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        
    print(f"\nSuccess! {len(data)} car listings successfully saved to '{filename}'.")

# --- Execution Block ---
if __name__ == "__main__":
    # Replace this with the actual URL of the marketplace you are targeting
    TARGET_URL = 'https://riyasewana.com/search/cars' 
    
    print("Initializing web scraper...")
    car_results = scrape_sri_lankan_cars(TARGET_URL, pages_to_scrape=3)
    save_to_csv(car_results, 'sl_car_prices.csv')


#mutiple sites to scrap

import requests
from bs4 import BeautifulSoup
import csv
import time
import random

class CarScraper:
    def __init__(self):
        self.results = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_riyasewana(self, pages=1):
        print("--- Scraping Riyasewana ---")
        base_url = "https://riyasewana.com/search/cars"
        for p in range(1, pages + 1):
            url = f"{base_url}?page={p}" if p > 1 else base_url
            soup = self.fetch_page(url)
            if not soup: break
            
            listings = soup.find_all('li', class_='item')
            for item in listings:
                title = item.find('h2').text.strip() if item.find('h2') else "N/A"
                price = item.find('div', class_='price').text.strip() if item.find('div', class_='price') else "N/A"
                # Riyasewana specific: usually "Location | Date"
                meta = item.find('div', class_='box').text.strip() if item.find('div', class_='box') else "N/A"
                
                self.results.append({
                    'Source': 'Riyasewana',
                    'Title': title,
                    'Price': price,
                    'Details': meta.replace('\n', ' ')
                })
            time.sleep(random.uniform(1, 3))

    def scrape_ikman(self, pages=1):
        print("--- Scraping Ikman.lk ---")
        # Note: Ikman uses highly dynamic classes (e.g., 'heading--3Y69L'). 
        # These change often. You must inspect the page to get the current ones.
        base_url = "https://ikman.lk/en/ads/sri-lanka/cars"
        for p in range(1, pages + 1):
            url = f"{base_url}?page={p}"
            soup = self.fetch_page(url)
            if not soup: break
            
            # Ikman listings are usually inside <a> tags with specific data-test attributes
            listings = soup.find_all('li', class_='normal--2QYVk') 
            for item in listings:
                title = item.find('h2').text.strip() if item.find('h2') else "N/A"
                price = item.find('div', class_='price--3H9eH').text.strip() if item.find('div', class_='price--3H9eH') else "N/A"
                desc = item.find('div', class_='description--2-S3E').text.strip() if item.find('div', class_='description--2-S3E') else "N/A"
                
                self.results.append({
                    'Source': 'Ikman',
                    'Title': title,
                    'Price': price,
                    'Details': desc
                })
            time.sleep(random.uniform(2, 4))

    def save_to_csv(self, filename="sl_car_market_data.csv"):
        if not self.results:
            print("No data to save.")
            return
        
        keys = self.results[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.results)
        print(f"Saved {len(self.results)} records to {filename}")

# --- Run Scraper ---
if __name__ == "__main__":
    scraper = CarScraper()
    
    # Scrape from multiple sources
    scraper.scrape_riyasewana(pages=2)
    scraper.scrape_ikman(pages=1)
    
    # Export combined data
    scraper.save_to_csv()