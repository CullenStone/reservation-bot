import selenium.webdriver

options = selenium.webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')

driver = selenium.webdriver.Chrome(chrome_options=options)
driver.get('https://www.python.org/')
print(driver.title)
driver.close()