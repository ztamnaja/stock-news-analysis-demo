import json, os, logging
from huggingface_hub import InferenceClient
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Analyzer:
    def __init__(self, api_key: str):
        """Initialize with API key, input and output file paths."""
        self.api_key = os.getenv("HUGGINGFACE_API_KEY") or api_key
        self.client = InferenceClient(provider="hf-inference", api_key=api_key)
        self.input_path = "./data/processed"
        self.output_path = "./data/storage"

    def analyze_sentiment(self, article: str) -> str:
        """Analyzes sentiment of a given news article."""
        prompt = [
            {
                "role": "system",
                "content": """ 
                    You are a financial sentiment classifier. Your task is to analyze the sentiment of a given news article related to stocks or financial markets.

                    Classification Criteria:
                            Positive – Optimistic tone, strong financial performance, bullish market trends, or positive corporate developments.
                            Neutral – Balanced or factual reporting without a strong positive or negative bias.
                            Negative – Pessimistic tone, poor financial performance, bearish market trends, regulatory issues, or adverse developments.

                    Respond strictly with one of the following words: "Positive", "Neutral", or "Negative". Do not provide explanations or additional text.
                """
            },
            {
                "role": "user",
                "content": f"News Article:\n {article}"
            }
        ]
        
        response = self.client.chat.completions.create(
            model="Qwen/QwQ-32B", 
            messages=prompt, 
            temperature=0.7,
            max_tokens=1024,
            top_p=0.7,
            stream=False,
            response_format = {
                "type": "json",
                "value": {
                    "properties": {
                        "sentiment": {"type": "string",  "enum": ["positive", "neutral", "negative"]},
                    },
                    "required": ["sentiment"],
                },
            }
        )
        
        result = json.loads(response.choices[0].message.content)
        # Validate the result
        if result['sentiment'] not in ["positive", "neutral", "negative"]: 
            raise ValueError("Invalid sentiment classification.")
        
        return result['sentiment']

    def analyze_key_topic(self, article: str) -> list:
        """Extracts key topics from a financial news article."""
        messages = [
            {
                "role": "system",
                "content": """
                    You are an AI that extracts structured key financial topics from news articles.
                        Your task: Extract the key topics from the following financial news article.
                        - Focus on companies, stock market movements, economic indicators, and important financial events.
                        - Avoid generic or irrelevant topics.
                        - Return the most relevant of 7 key topics.
                        - Return the response as a JSON array in the format: {{"key_topics": ["topic1", "topic2", "topic3"]}}.
                """
            },
            {
                "role": "user",
                "content": f"Article:\n {article}"
            }
        ]
        
        response = self.client.chat.completions.create(
            model="Qwen/QwQ-32B", 
            messages=messages, 
            temperature=1.0,
            max_tokens=1024,
            top_p=0.7,
            stream=False,
            response_format = {
                "type": "json",
                "value": {
                    "properties": {
                        "key_topics": {"type": "array"},
                    },
                    "required": ["key_topics"],
                },
            }
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate the result
        if not isinstance(result['key_topics'], list): 
            raise ValueError("Invalid Extract Topics")
        
        return result['key_topics']

    def analyze_articles(self, quote: str):
        """Processes articles, performs sentiment and topic analysis, and saves the results."""
        file_path = f"{self.input_path}/cleaned_articles_{quote.lower()}_{datetime.now().date()}.json"
        if not os.path.exists(file_path):
            logging.info(f"No cleaned articles found for {quote}. Exiting!")
            return None

        with open(file_path, "r") as f:
            articles = json.load(f)
        
        logging.info(f"Analyzing sentiment and key topics for {len(articles)} articles...")
        
        # Analyze each article and update it with sentiment and key topics
        for article in articles:
            article_text = article.get("processed_content", "")
           
            if article_text:
                try:
                    sentiment = self.analyze_sentiment(article_text)
                    key_topics = self.analyze_key_topic(article_text)
                    article["sentiment"] = sentiment
                    article["key_topics"] = key_topics
                    
                    del article["content"]
                    del article["processed_content"]
             
                except ValueError as e:
                    logging.error(f"Skipping article {article['article_id']} due to error: {str(e)}")
                    continue

        # Save the analyzed results
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        file_name = f"{self.output_path}/analyzed_articles_{quote.lower()}_{datetime.now().date()}.json"
        with open(file_name, "w") as f:
            json.dump(articles, f, indent=4)

        logging.info(f"✅ Sentiment and key topic analysis completed and saved to: {file_name}")


if __name__ == "__main__":
    api_key = os.getenv("HUGGINGFACE_API_KEY")  

    analyzer = Analyzer(api_key=api_key)
    analyzer.analyze_articles(quote="PTT.BK")
