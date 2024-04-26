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


def scrape_data_point():
    """
    Scrapes the headline for the "Encampment at Penn" article from The Daily Pennsylvanian's featured page.
    Returns:
        str: The headline text if found, otherwise an empty string.
    """
    # First, make a request to the main page
    main_page_req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {main_page_req.url}")
    loguru.logger.info(f"Request status code: {main_page_req.status_code}")

    if main_page_req.ok:
        # Parse the main page to find the link to the featured page
        main_soup = bs4.BeautifulSoup(main_page_req.text, "html.parser")
        featured_page_link = main_soup.select_one("h3.frontpage-section > a")

        if featured_page_link:
            featured_page_url = featured_page_link.get("href")
            featured_page_req = requests.get(featured_page_url)
            loguru.logger.info(f"Request URL: {featured_page_req.url}")
            loguru.logger.info(f"Request status code: {featured_page_req.status_code}")

            if featured_page_req.ok:
                # Parse the featured page to find the "Encampment at Penn" headline
                featured_soup = bs4.BeautifulSoup(featured_page_req.text, "html.parser")
                headline_element = featured_soup.select_one(".special-edition a[href*='encampment-at-penn']")
                data_point = "" if headline_element is None else headline_element.text
                loguru.logger.info(f"Data point: {data_point}")
                return data_point

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
