import json, re, gzip, base64, os, logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Processor:
    def __init__(self):
        """Initializes paths for input and output data."""
        self.input_path = './data/raw'
        self.output_path = './data/processed'
    
    def clean_text(self, text: str) -> str:
        """Removes HTML tags, special characters, and unnecessary spaces."""
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)  # Remove special characters
        text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
        return text.lower()  # Convert to lowercase

    def compress_text(self, text: str) -> str:
        """Compress text using gzip and encode it in Base64."""
        compressed = gzip.compress(text.encode("utf-8"))
        return base64.b64encode(compressed).decode("utf-8")

    def decompress_text(self, compressed_text: str) -> str:
        """Decode Base64 and decompress gzip compressed content."""
        compressed = base64.b64decode(compressed_text.encode("utf-8"))
        return gzip.decompress(compressed).decode("utf-8")

    def preprocess_articles(self, quote: str):
        """Cleans and compresses raw news articles from all matching .ndjson files."""
        with os.scandir(self.input_path) as entries:
            files = [entry.name for entry in entries if entry.is_file()]
        
        matching_files = [f for f in files if f"articles_{quote.lower()}_{datetime.now().date()}" in f and f.endswith(".ndjson")]
        # print('matching_files:', matching_files)
        
        for file_name in matching_files:
            file_path = os.path.join(self.input_path, file_name)

            # Read NDJSON file line by line into a list
            articles = []
            with open(file_path, "r") as f:
                for line in f:
                    articles.append(json.loads(line.strip()))

            # Convert to Pandas DataFrame
            df = pd.DataFrame(articles)

            # Process each article
            df["processed_content"] = df["content"].apply(self.clean_text)
            df["compressed_content"] = df["content"].apply(self.compress_text)

            # Ensure the output directory exists
            os.makedirs(self.output_path, exist_ok=True)

            output_file = os.path.join(self.output_path, f"cleaned_articles_{quote.lower()}_{datetime.now().date()}.json")
            with open(output_file, "w") as f:
                json.dump(df.to_dict(orient="records"), f, indent=4)

            logging.info(f"✅ Processed data and saved to: {output_file}")


if __name__ == "__main__":
    processor = Processor()
    processor.preprocess_articles(quote="PTT.BK")
