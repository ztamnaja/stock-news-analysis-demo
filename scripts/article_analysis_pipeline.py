import asyncio, logging, os
from src.scraper import Scraper
from src.preprocess import Processor
from src.analysis import Analyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

api_key = os.getenv("HUGGINGFACE_API_KEY")

class NewsArticleAnalysisPipeline:
    def __init__(self):
        self.scraper = Scraper()
        self.processor = Processor()
        self.analyzer = Analyzer(api_key=api_key)


    def run(self, quotes: list[str]):
        """Main pipeline: Scrape, preprocess, and analyze stock data."""
        if not quotes:
            logging.info("No stock symbols provided. Exiting.")
            return

        logging.info(f"Starting processing pipeline for stock symbols: {quotes}")

        try:
            logging.info("Starting scraping process...")
            asyncio.run(self.scraper.run(quotes))  # Runs all scraping tasks in parallel

            for symbol in quotes:
                logging.info(f"Preprocessing data for {symbol}...")
                self.processor.preprocess_articles(quote=symbol)

                logging.info(f"Analyzing data for {symbol}...")
                self.analyzer.analyze_articles(quote=symbol)

            logging.info("Done :)")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
