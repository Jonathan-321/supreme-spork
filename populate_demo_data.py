"""
Script to populate the AgriFinanceIntelligence platform with demo data.
This script runs the data scraper and then loads the data into the database.
"""
import os
import logging
from data_scraper import DataScraper
from data_loader import DataLoader
from app import app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the data population process."""
    logger.info("Starting demo data population process")
    
    # Create data directory if it doesn't exist
    data_dir = "scraped_data"
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # Step 1: Run the data scraper
        logger.info("Running data scraper...")
        scraper = DataScraper()
        scrape_summary = scraper.scrape_all_data(data_dir)
        logger.info(f"Data scraping complete: {scrape_summary}")
        
        # Step 2: Load the data into the database
        logger.info("Loading data into database...")
        loader = DataLoader(app, db)
        success = loader.load_all_data()
        
        if success:
            logger.info("Data loading complete!")
        else:
            logger.error("Data loading failed!")
            
    except Exception as e:
        logger.error(f"Error in data population process: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Demo data population complete!")
        print("You can now run the application to see the data in action.")
        print("Run: python app.py")
    else:
        print("\n❌ Demo data population failed!")
        print("Check the logs for details.")
