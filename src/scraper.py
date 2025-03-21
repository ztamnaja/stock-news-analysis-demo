import json
import os
import asyncio
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MAX_CONCURRENCY = 5

class Scraper:
    def __init__(self):
        self.max_concurrency = MAX_CONCURRENCY
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        self.output_path = "./data/raw"
        os.makedirs(self.output_path, exist_ok=True)

    async def scrape_links(self, quote: str, browser):
        logging.info(f"Scraping news links for {quote}...")
        page = await browser.new_page()
        url = f"https://finance.yahoo.com/quote/{quote.upper()}/latest-news/"
        await page.goto(url, timeout=300000)
        await page.wait_for_selector('ul.stream-items.yf-1usaaz9')

        prev_height = await page.evaluate("document.body.scrollHeight")

        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == prev_height:
                break
            prev_height = new_height

        all_links = await page.locator('ul.stream-items.yf-1usaaz9 li a').evaluate_all(
            'elements => elements.map(e => e.href).filter(link => link.startsWith("https://finance.yahoo.com/news/") && link.endsWith(".html"))'
        )
        await page.close()

        unique_links = list(set(all_links))
        
        if not unique_links:
            logging.info(f"No news articles found for {quote}.")
            return None
        links_filename = f"{self.output_path}/links_{quote.lower()}_{datetime.now().date()}.json"
        with open(links_filename, 'w') as f:
            json.dump(unique_links, f, indent=4)

        return unique_links

    async def extract_article(self, url: str, browser):
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=50000)
            await page.wait_for_selector('article', timeout=30000)

            last_height = 0
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            while await page.get_by_role('button', name="Story Continues").count() > 0:
                await page.get_by_role('button', name="Story Continues").click()
                await asyncio.sleep(2)

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            title_elem = soup.select_one('.cover-title.yf-1rjrr1')
            title = title_elem.get_text(strip=True) if title_elem else None
            date_elem = soup.select_one('div > time.byline-attr-meta-time')
            published_date = date_elem.get("data-timestamp") if date_elem else None
            content = "\n".join([p.get_text(strip=True) for p in soup.select('.body.yf-tsvcyu')])

            article_data = {
                "article_id": url.split("/")[-1].replace(".html", "").split("-")[-1],
                "title": title,
                "content": content,
                "url": url,
                "published_date": published_date
            }

            return article_data
        except Exception as e:
            # logging.error(f"❌ Error extracting article {url}: {e}")
            return None
        finally:
            await page.close()

    async def scrape_articles(self, quote: str, article_urls: list[str], browser):
        filename = f"{self.output_path}/articles_{quote.lower()}_{datetime.now().date()}.ndjson"

        async def extract_with_semaphore(url):
            async with self.semaphore:
                return await self.extract_article(url, browser)

        tasks = [extract_with_semaphore(url) for url in article_urls]

        with open(filename, "w") as f:
            completed = 0
            total = len(tasks)

            for task in asyncio.as_completed(tasks):
                try:
                    article = await task
                    if article:
                        f.write(json.dumps(article) + "\n")
                        f.flush()

                    completed += 1
                    logging.info(f"Progress: {completed}/{total} articles processed")
                except Exception as e:
                    logging.error(f"❌ Error processing article: {e}")

    async def run(self, quotes: list[str]):
        if not quotes:
            logging.info("No stock symbols provided. Exiting.")
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            tasks = [self.scrape_for_quote(quote, browser) for quote in quotes]
            await asyncio.gather(*tasks)
            await browser.close()

        logging.info(f"✅ All articles saved!")

    async def scrape_for_quote(self, quote: str, browser):
        logging.info(f"Scraping news for {quote}...")
        links = await self.scrape_links(quote, browser)
        
        if not links:
            return None
        
        await self.scrape_articles(quote, article_urls=links, browser=browser)

if __name__ == "__main__":
    quotes = ["PTT.BK"]
    scraper = Scraper()
    asyncio.run(scraper.run(quotes))