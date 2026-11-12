from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

driver.get("https://www.apple.com")

# Accept potential region redirects automatically
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Click Music (hover-based nav on Apple)
music_link = wait.until(
    EC.element_to_be_clickable((By.LINK_TEXT, "TV & Home"))
)
music_link.click()

# Now navigate to HomePod from Music page
homepod_link = wait.until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "HomePod"))
)
homepod_link.click()

wait.until(EC.title_contains("HomePod"))

assert "HomePod" in driver.title

driver.quit()