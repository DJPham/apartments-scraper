# using selenium to do the scraping and navigation through the webpages
from selenium import webdriver
from selenium.webdriver.common.by import By
# using Chrome as the browser
from selenium.webdriver.chrome.service import Service as ChromeService

# assist with the selenium scraping
# automates the process
from webdriver_manager.chrome import ChromeDriverManager

# to assist with the time it takes to process a request
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException

# misc libraries 
import re
import time

class AptScraper():
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        self.base_url = 'https://www.apartments.com/'

        # open the window in full screen, may help with some elements
        self.driver.maximize_window()

    # go from home page to the search results 
    def navigate_homePage(self):
        self.driver.get(self.base_url)

        try:

            # explicit wait of 10 seconds before an error is thrown
            # selenium will look for the search bar and button
            search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "quickSearchLookup")))
            submit_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.go.btn.btn-lg.btn-primary")))

            # once found, enter the value below and click the button to search
            # eventually will allow end-user to search where they want
            search_box.send_keys('pittsburgh')
            submit_button.click()
        except Exception as e:
            print(f'An error has occured: {e}') 

    # function will open the all filters option and then show all the amentities
    def addFilters(self):
        try:
            allFilters_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "advancedFilterCombo")))
            allFilters_button.click()
            time.sleep(2)

            # Scroll to the element above the button
            scrollPoint = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.amenitiesHeading')))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'})", scrollPoint)
            time.sleep(2)

            # maybe re-add for when tracking user input
            # Wait for the 'Show More Amenities' button to be clickable and click it
            #showAmenities_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#showMoreAmenitiesBtn")))
            #self.driver.execute_script("arguments[0].click();", showAmenities_button)

            # eventual user-input but manual clicking filters for now
            # button1 is in-house washer & dryer
            button1 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-value='2'][data-path='3']")))
            # button2 is utilities included
            button2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-value='4194304'][data-path='3']")))
            self.driver.execute_script("arguments[0].click();", button1)
            self.driver.execute_script("arguments[0].click();", button2)

            time.sleep(2)

            # once done with filter inclusion, see the results
            seeResults_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "seeResultBtn")))
            self.driver.execute_script("arguments[0].click();", seeResults_button)
        
        except Exception as e:
            print(f"An error occurred: {e}")

    # function will scrap the results found
    def resultScraper(self):
        # prints out the general info of # of results returned w/ filters attached @ what location you searched for
        summaryText = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "placardSearchHeading"))).text

        print(summaryText)

        # find the parent element of the list of prices
        priceList = []
        combined_prices_list = []

        # going through all the potential pages of results
        while True:
            try:
                try:
                    parentElement = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "top-level-info")))
                # for some reason the classes switch after X pages, so we gotta do a double try-except block
                except NoSuchElementException:
                    parentElement = element.find_element(By.CLASS_NAME, "property-information-wrapper")
            except Exception as e:
                print(f"An error occurred: {e}")

            # loop through each child element that has the price and append to a list
            for element in parentElement:
                try:
                    try:
                        property_price_element = element.find_element(By.CLASS_NAME, "property-pricing")
                    # same instance as above
                    except NoSuchElementException:
                        property_price_element = element.find_element(By.CLASS_NAME, "price-range")

                    priceList.append(property_price_element.text)
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Extract and clean prices, and calculate the average
            for price_string in priceList:
                # Find all numeric parts in the price string
                numeric_parts = re.findall(r'\d+', price_string.replace(',', ''))
                # Combine numeric parts correctly
                combined_prices_list.extend(numeric_parts)

            try:
                next_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next ")))
                time.sleep(3)
                self.driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(self.driver, 10).until(EC.staleness_of(parentElement[0]))
            except Exception as e:
                print("No more pages")
                break

        # Convert to integers
        flat_list = [int(item) for item in combined_prices_list]

        # Calculate the average
        average = sum(flat_list) / len(flat_list) if flat_list else 0

        print(combined_prices_list)
        print(f"Average Price around Pittsburgh: ${round(average,2)}")

    def closeScraper(self):
        self.driver.quit()

