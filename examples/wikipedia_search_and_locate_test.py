from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://www.wikipedia.org")

search_input = wait.until(
    EC.presence_of_element_located((By.ID, "searchInput"))
)

search_input.send_keys("Wayne Gretzky")
search_input.send_keys(Keys.RETURN)

heading = wait.until(
    EC.presence_of_element_located((By.ID, "firstHeading"))
)

assert "Wayne" in heading.text

# Locate a specific section link
webdriver_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Wayne")
assert webdriver_link is not None

driver.quit()