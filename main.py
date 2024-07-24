# separating the main functionalities - scraping, database, visualization, web app into different classes

from scraper import AptScraper

import time

apt = AptScraper()

apt.navigate_homePage()
apt.addFilters()
time.sleep(5)
apt.resultScraper()
apt.closeScraper()