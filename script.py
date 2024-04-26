"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


import requests
import bs4
import loguru

import requests
import bs4
import loguru

def scrape_crossword_title():
    """
    Scrapes the title of the latest crossword puzzle from The Daily Pennsylvanian website.
    
    Returns:
        str: The title of the latest crossword puzzle if found, otherwise an empty string.
    """
    req_crosswords = requests.get("https://www.thedp.com/section/crosswords")
    loguru.logger.info(f"Request URL for crosswords: {req_crosswords.url}")
    loguru.logger.info(f"Request status code for crosswords: {req_crosswords.status_code}")
    
    if req_crosswords.ok:
        soup_crosswords = bs4.BeautifulSoup(req_crosswords.text, "html.parser")
        crossword_title_tag = soup_crosswords.find("h3", class_="standard-link")
        
        if crossword_title_tag:
            crossword_title = crossword_title_tag.text.strip()
            loguru.logger.info(f"Crossword title: {crossword_title}")
            return crossword_title
        else:
            loguru.logger.warning("Latest crossword title not found.")
    else:
        loguru.logger.warning("Failed to fetch the crossword page.")
    
    return ""



if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None:
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
