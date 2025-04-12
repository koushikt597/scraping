import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import csv
import logging
import time
from typing import List
# import requests
from curl_cffi import requests
from camoufox.sync_api import Camoufox
from main.schema import Drug

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, base_url: str, api_url: str, file_name: str, length:int = 100):
        self.headers = {}
        self.base_url = base_url
        self.api_url = api_url
        self.file_name = file_name
        self.all_drugs = []
        self.total_data = None
        self.length = length

    def _handle_request(self, request):
        if "produk-dt" in request.url:
            self.headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["content-length", "transfer-encoding", "set-cookie"]
            }

    def get_headers_from_browser(self):
        with Camoufox() as browser:
            page = browser.new_page()
            page.goto("https://google.com")
            page.on("request", self._handle_request)
            page.goto(self.base_url)
            # Wait for Network Idle
            page.wait_for_load_state("networkidle")
            # Wait more, just in case
            page.wait_for_timeout(10000)
            # browser.close()
            logger.info(f"Final session headers: {self.headers}")

    def _build_payload(self, draw: int) -> dict:
        length = self.length
        return {
            'draw': str(draw),
            'columns[0][data]': 'PRODUCT_ID',
            'columns[0][name]': '',
            'columns[0][searchable]': 'false',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'PRODUCT_REGISTER',
            'columns[1][name]': '',
            'columns[1][searchable]': 'false',
            'columns[1][orderable]': 'false',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 'PRODUCT_NAME',
            'columns[2][name]': '',
            'columns[2][searchable]': 'false',
            'columns[2][orderable]': 'false',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 'MANUFACTURER_NAME',
            'columns[3][name]': '',
            'columns[3][searchable]': 'false',
            'columns[3][orderable]': 'false',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'order[0][column]': '0',
            'order[0][dir]': 'asc',
            'start': str((draw - 1) * length),
            'length': str(length),
            'search[value]': '',
            'search[regex]': 'false',
            'product_register': '',
            'product_name': '',
            'product_brand': '',
            'product_package': '',
            'product_form': '',
            'ingredients': '',
            'submit_date': '',
            'product_date': '',
            'expire_date': '',
            'manufacturer_name': '',
            'status': '',
            'release_date': '',
        }

    def retrieve_data(self, draw: int) -> List[Drug]:
        payload = self._build_payload(draw)
        try:
            resp = requests.post(self.api_url, headers=self.headers, data=payload)
            resp.raise_for_status()
            data = resp.json()
            drug_list = [Drug(**item) for item in data.get("data", [])]
            if drug_list:
                self.all_drugs.extend(drug_list)
                if self.total_data is None:
                    total_data = data.get("recordsTotal", [])
                    self.total_data = total_data
                    logger.info(f"Total data:", {self.total_data})
                logger.info(f"Page {draw}. Successfully retrieved {len(drug_list)} drugs.")
            else:
                self.status = True
        except Exception as e:
            print(e)
            return []

    def save_to_csv(self):
        if not self.all_drugs:
            logger.warning("No data to save.")
            return
        with open(self.file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.all_drugs[0].model_dump().keys())
            writer.writeheader()
            writer.writerows([d.model_dump() for d in self.all_drugs])
        logger.info(f"Saved {len(self.all_drugs)} drugs to {self.file_name}")


if __name__ == "__main__":
    LENGTH = 100

    s = Scraper(
        base_url="https://cekbpom.pom.go.id/produk-obat",
        api_url="https://cekbpom.pom.go.id/produk-dt/01",
        file_name="all_drugs.csv",
        length=LENGTH
    )
    s.get_headers_from_browser()

    start_time = time.time() 
    i = 0
    while s.total_data is None or len(s.all_drugs) < s.total_data:
        s.retrieve_data(draw=i)
        i += 1
    s.save_to_csv()

    end_time = time.time()  
    elapsed_time = end_time - start_time  
    logger.info(f"Process completed in {elapsed_time:.2f} seconds.")

