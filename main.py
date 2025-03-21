from scripts.article_analysis_pipeline import NewsArticleAnalysisPipeline
from argparse import ArgumentParser
import logging

# Map feature names to their respective pipeline classes
SCRIPT_MAPPING = {
    "article": NewsArticleAnalysisPipeline,
}

def get_script(name: str):
    """
    Retrieve the script class based on the feature name.

    Args:
        name (str): Feature name for the reconciliation script.

    Returns:
        NewsArticleAnalysisPipeline: An instance of the corresponding pipeline class.

    Raises:
        NotImplementedError: If no mapping exists for the feature name.
    """
    script_class = SCRIPT_MAPPING.get(name.lower())
    
    if script_class:
        return script_class()

    raise NotImplementedError(f"No script mapped for feature: {name}")


def main():
    """
    Main entry point for the reconciliation script.
    Parses command-line arguments and runs the corresponding pipeline.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Parse arguments
    parser = ArgumentParser(description="Run a specific data reconciliation pipeline.")
    parser.add_argument(
        "feature",
        help="The feature for the pipeline to run.",
    )
    parser.add_argument(
        "--quote",
        help="The sigle stock symbol to analyze.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--quotes",
        help="The multiple sigle stock symbol to analyze.",
        type=str,
        default=None,
    )
    args = parser.parse_args()

     # Validate the 'quote' argument
    if args.quote and "," in args.quote:
        logging.error("The 'quote' argument should not contain commas. Please provide a single stock symbol.")
        return
    
    symbols = set()
    if args.quote:
        symbols.add(args.quote)
    if args.quotes:
        symbols.update(args.quotes.split(','))
    symbols = list(symbols)
    if not symbols:
        logging.error("No stock symbols provided. Exiting.")
        return

    logging.info(f"Starting pipeline: {args.feature} with stock symbols: {symbols}")

    try:
        pipeline = get_script(name=args.feature)
        pipeline.run(quotes=symbols)  # Assumes all pipelines have a `run()` method
        logging.info(f"Pipeline run successfully for {args.feature}.")
    except Exception as e:
        logging.error(f"An error occurred while running the pipeline: {e}", exc_info=True)


if __name__ == "__main__":
    main()
