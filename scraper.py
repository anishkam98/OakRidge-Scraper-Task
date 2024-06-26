from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv

max_wait = 10
url = 'https://www.ornl.gov/staff-profile/juliane-weber?type=publications'
chrome_driver_path = './drivers/chrome/chromedriver-win64/chromedriver.exe'
cService = webdriver.ChromeService(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service = cService)

# Open the publications site
driver.get(url)

# Get the publication hyperlinks
publication_rows = WebDriverWait(driver, max_wait).until(
    EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="views-row"]')) # Alternatively, could've used '//div[parent::div[@class="staff-profile-publications"]]/div' or '//span[@class="field-content"]'
)

# Create a CSV file to capture Title, Link_URL, Pub_Type, and DOI_URL
publications_csv =  open('publications.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(publications_csv, delimiter=',')
csv_writer.writerow(['Title', 'Link_URL', 'Pub_Type', 'DOI_URL'])

for index, publication_row in enumerate(publication_rows):
    anchor_element = publication_row.find_element(By.TAG_NAME, 'a')
    publication = {}

    # Get the publication title 
    publication['Title'] = anchor_element.text

    # Open the publication in a new tab and save the link URL
    publication_url = str(driver.execute_script('return arguments[0].href', anchor_element))
    driver.execute_script('window.open(arguments[0], "_blank")', publication_url)
    driver.switch_to.window(driver.window_handles[-1])
    publication['Link_URL'] = driver.current_url

    # Get the publication type
    publication_type = WebDriverWait(driver, max_wait).until(
        EC.presence_of_element_located((By.XPATH, '//div[preceding-sibling::div[@class="publication-fields-row-left" and contains(text(), "Publication Type")]]'))
    ) 
    publication['Pub_Type'] = publication_type.text
    
    # Get the DOI URL, set it to null if there isn't one
    try:
        DOI_URL_element = driver.find_element(By.XPATH, '//a[contains(text(), "View DOI Listing")]')
        DOI_URL = driver.execute_script('return arguments[0].href', DOI_URL_element)
    except NoSuchElementException:
        DOI_URL = None
    publication['DOI_URL'] = DOI_URL
    
    # Write this publication to publications.csv
    csv_writer.writerow([publication['Title'], publication['Link_URL'], publication['Pub_Type'], publication['DOI_URL']])

    # Close the new tab and return to the previous one
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # If this is the last publication, close publications.csv and the driver
    if index == len(publication_rows)-1:
        publications_csv.close()
        driver.quit()