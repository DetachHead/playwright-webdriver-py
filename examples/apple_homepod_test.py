from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

driver.get("https://www.apple.com")

# Accept potential region redirects automatically
wait.until(expected_conditions.presence_of_element_located((By.TAG_NAME, "body")))

# Click Music (hover-based nav on Apple)
music_link = wait.until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "TV & Home")))
music_link.click()

# Now navigate to HomePod from Music page
homepod_link = wait.until(
    expected_conditions.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "HomePod"))
)
homepod_link.click()

wait.until(expected_conditions.title_contains("HomePod"))

assert "HomePod" in driver.title

driver.quit()
