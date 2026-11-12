from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup Chrome driver
service = Service()
driver = webdriver.Chrome(service=service)

try:
    # 1. Open Wikipedia
    driver.get("https://www.wikipedia.org/")
    driver.maximize_window()

    # 2. Wait for search box to load
    wait = WebDriverWait(driver, 10)
    search_box = wait.until(
        EC.presence_of_element_located((By.ID, "searchInput"))
    )

    # 3. Type into search box
    search_box.send_keys("Selenium (software)")

    # 4. Press Enter
    search_box.send_keys(Keys.RETURN)

    # 5. Wait for page title to load
    wait.until(
        EC.presence_of_element_located((By.ID, "firstHeading"))
    )

    # 6. Grab page heading text
    heading = driver.find_element(By.ID, "firstHeading").text
    print("Page Heading:", heading)

    # 7. Assert correct navigation
    assert "Selenium" in heading

    # 8. Click a link inside the page — use partial match so we're resilient
    #    to Wikipedia rewording the exact anchor text.
    webdriver_link = wait.until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "WebDriver"))
    )
    webdriver_link.click()

    # 9. Wait and confirm new page loaded
    wait.until(
        EC.presence_of_element_located((By.ID, "firstHeading"))
    )

    print("Successfully navigated to WebDriver page.")

    time.sleep(3)

finally:
    driver.quit()
