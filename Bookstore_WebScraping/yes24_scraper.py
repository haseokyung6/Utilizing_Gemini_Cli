import requests
from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger
import time
import os

# --- Constants and Configuration ---
BASE_URL = "https://www.yes24.com/product/category/CategoryProductContents"
# dispNo is for AI category
PARAMS = {
    "dispNo": "001001003032",
    "order": "SINDEX_ONLY",
    "addOptionTp": "0",
    "page": 1,
    "size": 120,
    "statGbYn": "N",
    "viewMode": "",
    "_options": "",
    "directDelvYn": "",
    "usedTp": "0",
    "elemNo": "0",
    "elemSeq": "0",
    "seriesNumber": "0",
}
HEADERS = {
    "host": "www.yes24.com",
    "referer": "https://www.yes24.com/product/category/display/001001003032",
    "rtt": "50",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "viewport-width": "813",
    "x-requested-with": "XMLHttpRequest",
}
START_PAGE = 1
END_PAGE = 10
REQUEST_DELAY_SECONDS = 2
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "yes24_AIdata.csv")

# --- Logger Setup ---
logger.add("scraping.log", rotation="10 MB", level="INFO", format="{time} {level} {message}")


def get_book_data(item_unit):
    """Extracts book information from a single item unit div."""
    try:
        title_elem = item_unit.select_one(".info_name .gd_name")
        title = title_elem.text.strip() if title_elem else None

        author_elem = item_unit.select_one(".info_auth a")
        author = author_elem.text.strip() if author_elem else None

        publisher_elem = item_unit.select_one(".info_pub a")
        publisher = publisher_elem.text.strip() if publisher_elem else None

        date_elem = item_unit.select_one(".info_date")
        pub_date = date_elem.text.strip() if date_elem else None

        list_price_elem = item_unit.select_one(".info_price .dash .yes_m")
        list_price = list_price_elem.text.strip() if list_price_elem else None

        sale_price_elem = item_unit.select_one(".info_price .yes_b")
        sale_price = sale_price_elem.text.strip() if sale_price_elem else None

        review_count_elem = item_unit.select_one(".rating_rvCount .txC_blue")
        review_count = review_count_elem.text.strip() if review_count_elem else "0"

        sales_index_elem = item_unit.select_one(".saleNum")
        sales_index = sales_index_elem.text.strip().replace("판매지수 ", "") if sales_index_elem else None

        description_elem = item_unit.select_one(".info_read")
        description = description_elem.text.strip() if description_elem else None
        
        details_elem = item_unit.select_one(".info_row.info_name > a.gd_name")
        details_url = "https://www.yes24.com" + details_elem['href'] if details_elem else None


        return {
            "제목": title,
            "저자": author,
            "출판사": publisher,
            "발행일": pub_date,
            "정가": list_price,
            "판매가": sale_price,
            "리뷰 수": review_count,
            "판매지수": sales_index,
            "상세 정보": description,
            "설명": description,
            "상세 페이지 URL": details_url,
        }
    except Exception as e:
        logger.error(f"Error parsing book data: {e}")
        return None


def main():
    """Main function to scrape Yes24 and save data."""
    logger.info("Starting Yes24 book scraping process.")
    all_books = []

    for page in range(START_PAGE, END_PAGE + 1):
        logger.info(f"Scraping page {page}...")
        PARAMS["page"] = page
        
        try:
            response = requests.get(BASE_URL, params=PARAMS, headers=HEADERS)
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.text, "html.parser")
            item_units = soup.select(".itemUnit")

            if not item_units:
                logger.warning(f"No books found on page {page}.")
                continue

            for item in item_units:
                book_data = get_book_data(item)
                if book_data:
                    all_books.append(book_data)

            logger.info(f"Successfully scraped {len(item_units)} books from page {page}.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
        except Exception as e:
            logger.error(f"An error occurred on page {page}: {e}")
        
        logger.info(f"Waiting for {REQUEST_DELAY_SECONDS} seconds before next request...")
        time.sleep(REQUEST_DELAY_SECONDS)

    if not all_books:
        logger.warning("No books were scraped. Exiting.")
        return

    logger.info(f"Total books scraped: {len(all_books)}")

    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_books)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    logger.info(f"Data successfully saved to {OUTPUT_FILE}")
    
    # Display sample of the data
    print("--- Sample of Scraped Data ---")
    print(df.head())
    print("------------------------------")


if __name__ == "__main__":
    main()
