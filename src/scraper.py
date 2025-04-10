from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from scripts.analysis import analyze_data
import pandas as pd
import time
from datetime import datetime
import logging
import os


class CarScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(
            service=self.service,
            options=self.options
        )

        self.base_url = "https://www.avito.ru/all/avtomobili/mercedes-benz-ASgBAgICAUTgtg3omCg?cd=1&f=ASgBAQICAUTgtg3omCgDQOK2DTSMtCjypCjupCjqtg009oAppIEp1IAppv8RNOiHiwP6h4sD7oeLAw"
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s: %(message)s',
            level=logging.INFO
        )

    def _parse_item(self, item):
        try:
            raw_url = "https://www.avito.ru" + item.find('a', {'itemprop': 'url'})['href']
            clean_url = self._clean_url(raw_url)

            return {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'title': item.find('h3', {'itemprop': 'name'}).text.strip(),
                'price': item.find('meta', {'itemprop': 'price'})['content'],
                'url': raw_url,
                'base_url': clean_url
            }
        except Exception as e:
            logging.warning(f"Failed to parse item: {str(e)}")
            return None

    def scrape(self):
        """сбор данных"""
        try:
            logging.info("Starting scraping session...")
            self.driver.get(self.base_url)
            time.sleep(3)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = soup.find_all('div', {'data-marker': 'item'})

            data = []
            for item in items:
                parsed = self._parse_item(item)
                if all(parsed.values()):
                    data.append(parsed)

            return pd.DataFrame(data)

        except Exception as e:
            logging.error(f"Scraping failed: {str(e)}")
            return pd.DataFrame()

        finally:
            self.driver.quit()
            logging.info("Browser session closed")

    def _clean_url(self, url):
        if pd.isna(url):
            return None
        return url.split('?')[0].split('#')[0].rstrip('/')

    def save_data(self, df, filename='data/raw_data.csv'):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            if not df.empty:
                df['base_url'] = df['url'].apply(self._clean_url)

                if os.path.exists(filename):
                    existing_df = pd.read_csv(filename)

                    if 'base_url' not in existing_df.columns:
                        existing_df['base_url'] = existing_df['url'].apply(self._clean_url)

                    mask = ~df['base_url'].isin(existing_df['base_url'])
                    new_df = df[mask].copy()

                    if not new_df.empty:
                        final_df = pd.concat([existing_df, new_df], ignore_index=True)
                        final_df.drop(columns=['base_url'], inplace=True, errors='ignore')
                        final_df.to_csv(filename, index=False)

                        logging.info(f"New unique ads: {len(new_df)}. Total: {len(final_df)}")
                    else:
                        logging.info("No new unique ads found")

                else:
                    df.drop(columns=['base_url'], inplace=True, errors='ignore')
                    df.to_csv(filename, index=False)
                    logging.info(f"Initial save: {len(df)} records")

            else:
                logging.warning("Nothing to save: empty DataFrame")

        except Exception as e:
            logging.error(f"Save error: {str(e)}")
            raise


if __name__ == "__main__":
    scraper = CarScraper()
    df = scraper.scrape()

    if not df.empty:

        scraper.save_data(df)
        print(f"Success! Collected {len(df)} listings")
        analyze_data()
    else:
        print("Scraping completed with 0 results")
