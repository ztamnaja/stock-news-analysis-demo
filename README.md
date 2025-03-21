# Stock News Analysis [DEMO]

This project is designed to scrape, preprocess, and analyze stock news articles to extract valuable insights.

## Overview
This pipeline automates the process of scraping stock-related articles from Yahoo Finance, preprocessing the content, and running various analyses. The pipeline can be executed via a Python script.

## Features
✅ Web Scraping
- Extracts stock news articles from the Yahoo Finance website.  
- Uses **BeautifulSoup** and **Playwright** for web scraping.

✅ Preprocessing
- Cleans the text (removes HTML tags, special characters, extra spaces).  
- Compresses text to reduce storage size before saving.

✅ Text Analysis
- Sentiment analysis classifies articles as **positive**, **negative**, or **neutral**.  
- Extracts relevant topics for better stock insights.

✅ Data Storage & Management
- Stores raw, processed, and analyzed data in structured directories for easy access.


## Setup
Follow the steps below to set up the pipeline. I've tried to explain the steps where possible.

First clone the repository into your home directory and follow the steps.

  ```bash
  git clone git@github.com:ztamnaja/stock-news-analysis-demo.git
  cd stock-news-analysis
  ```

### Step 1: Create .env file
Create a file named .env in the root directory of the project with the following content:
```bash
HUGGINGFACE_API_KEY=SECRET_TOKEN
```


### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Running the Pipeline
Run for a single stock quote:
  ```bash
  python main.py article --quote "PTT.BK"
  ```

Run for multiple stock quotes:

  ```bash
  python main.py article --quotes "PTT.BK,KBANK.BK,CPALL.BK"
  ```


## Example Output
```

{
    "article_id": "180219778",
    "title": "Kasikornbank And Two Dividend Stocks For Your Portfolio",
    "url": "https://finance.yahoo.com/news/kasikornbank-two-dividend-stocks-portfolio-180219778.html",
    "published_date": "2025-02-18T18:02:19.000Z",
    "compressed_content": "H4sIAEkf3WcC/51Y224bORL9Fb54MwEUrmzZluSXrO04djYT2xgpCDJvVDclcdRN9pBsOcr77DfsD...",
    "sentiment": "neutral",
    "key_topics": [
        "U.S. stock indexes nearing record highs",
        "European indices positive economic signals",
        "Inflation data influencing rate policies",
        "Dividend stocks for portfolio stability",
        "Kasikornbank dividend sustainability",
        "Torigoe Co. Ltd. dividend risks",
        "Hirogin Holdings dividend growth and volatility"
    ]
}
```
