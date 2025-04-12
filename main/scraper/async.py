import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import csv
import logging
import time
import asyncio
import json
from typing import List, Dict, Any, Optional
from curl_cffi import requests as curl_requests
from camoufox.async_api import AsyncCamoufox
from main.schema import Drug

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncScraper:
    def __init__(self, base_url: str, api_url: str, file_name: str, concurrency_limit: int = 5, length: int = 100):
        self.headers: Dict[str, str] = {}
        self.base_url = base_url
        self.api_url = api_url
        self.file_name = file_name
        self.all_drugs: List[Drug] = []
        self.total_data: Optional[int] = None
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.length = length

    async def _handle_request(self, request):
        if "produk-dt" in request.url:
            self.headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["content-length", "transfer-encoding", "set-cookie"]
            }

    async def get_headers_from_browser(self):
        async with AsyncCamoufox() as browser:
            page = await browser.new_page()
            await page.goto("https://google.com")
            page.on("request", self._handle_request)
            await page.goto(self.base_url)
            # Wait for Network Idle
            await page.wait_for_load_state("networkidle")
            # Wait more, just in case
            await page.wait_for_timeout(10000)
            logger.info(f"Final session headers: {self.headers}")

    def _build_payload(self, draw: int) -> Dict[str, str]:
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

    async def retrieve_data(self, draw: int) -> List[Drug]:
        async with self.semaphore:  # Limit concurrent requests
            payload = self._build_payload(draw)
            try:
                # Use curl_ffi for the HTTP request
                loop = asyncio.get_event_loop()
                # Execute the curl request in the thread pool to prevent blocking
                resp = await loop.run_in_executor(
                    None,
                    lambda: curl_requests.post(
                        self.api_url, 
                        headers=self.headers, 
                        data=payload,
                        impersonate="chrome110"  # Use browser impersonation for better compatibility
                    )
                )
                
                if resp.status_code != 200:
                    logger.error(f"Request failed with status {resp.status_code} for draw {draw}")
                    return []
                
                data = resp.json()
                drug_list = [Drug(**item) for item in data.get("data", [])]
                
                if drug_list:
                    logger.info(f"Page {draw}. Successfully retrieved {len(drug_list)} drugs.")
                    
                    # Update total_data if not set yet
                    if self.total_data is None:
                        self.total_data = data.get("recordsTotal", 0)
                        logger.info(f"Total data: {self.total_data}")
                    
                    return drug_list
                else:
                    logger.info(f"Page {draw}. No data retrieved.")
                    return []
            except Exception as e:
                logger.error(f"Error retrieving data for draw {draw}: {str(e)}")
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

    async def process_batch(self, start_draw: int, batch_size: int, length:int) -> int:
        tasks = [self.retrieve_data(draw=i) for i in range(start_draw, start_draw + batch_size)]
        results = await asyncio.gather(*tasks)
        
        # Flatten results and extend all_drugs
        for drug_list in results:
            self.all_drugs.extend(drug_list)
        
        return len(self.all_drugs)

    async def run(self):
        await self.get_headers_from_browser()
        
        start_time = time.time()
        
        # First request to get total_data
        initial_drugs = await self.retrieve_data(draw=0)
        self.all_drugs.extend(initial_drugs)
        
        if self.total_data is None:
            logger.error("Failed to retrieve total data count.")
            return
        
        # Calculate how many batches we need
        remaining = self.total_data - len(self.all_drugs)
        batch_size = self.concurrency_limit * 2  # Process more than concurrency limit per batch
        
        draw = 1  # Start from 1 since we already processed 0
        
        while remaining > 0:
            current_batch_size = min(batch_size, remaining)
            logger.info(f"Processing batch starting at draw {draw} with size {current_batch_size}")
            
            retrieved_count = await self.process_batch(draw, current_batch_size, length = self.length)
            
            # Update progress
            remaining = self.total_data - retrieved_count
            draw += current_batch_size
            
            logger.info(f"Progress: {retrieved_count}/{self.total_data} ({retrieved_count/self.total_data*100:.1f}%)")
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.5)
        
        self.save_to_csv()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Process completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # Set concurrency limit
    CONCURRENCY_LIMIT = 20
    LENGTH = 100
    
    scraper = AsyncScraper(
        base_url="https://cekbpom.pom.go.id/produk-obat",
        api_url="https://cekbpom.pom.go.id/produk-dt/01",
        file_name="all_drugs_async.csv",
        concurrency_limit=CONCURRENCY_LIMIT,
        length = LENGTH
    )
    
    # Run the async scraper
    asyncio.run(scraper.run())