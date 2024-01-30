import argparse
import json
import time
import datetime
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from logger import logging as log

UNAME = os.getenv('RESY_USERNAME')
PWORD = os.getenv('RESY_PASSWORD')
EXPECTED_TIME = datetime.datetime(year=2024, month=1, day=29, hour=12, minute=0, second=0)
RESERVE_BUFFER = 10
WAIT_TIME_NOT_HEADLESS = 1.5
WAIT_TIME_HEADLESS = 0.5
# Open Webpage
# Login to Resy
# Input code
# Verify



def create_url(restaurant, party_size, date):
    reservation_date = datetime.datetime.strftime(date, '%Y-%m-%d')
    return f'https://resy.com/cities/ny/{restaurant}?date={reservation_date}&seats={str(party_size)}'


def time_waiter(func):
    """
        Check the 3 edge conditions

        1. If the time is before the requested time, wait
        2. If the time is the current time (or near the current time), execute function on a faster cadence
        3. If the time is long after the requested time, break.

    """
    def inner(*args, **kwargs):

        # I want to wait until one minute before the expected time
        wait_seconds = (EXPECTED_TIME - datetime.datetime.now()).total_seconds() - RESERVE_BUFFER
        log.info(f"Trying to reserve time at: {EXPECTED_TIME}")
        log.info(f"Will try to reserve +- {RESERVE_BUFFER} seconds from reservation date/time")

        # Check if program should wait
        if wait_seconds <= 0:
            log.info('Expected time has already passed... will continue to run')
        else:
            log.info(f"Waiting {wait_seconds} seconds")
            time.sleep(wait_seconds)

        attempt_counter = 1
        while (datetime.datetime.now() - EXPECTED_TIME).total_seconds() < RESERVE_BUFFER:
            log.info(f"---Attempt: {attempt_counter}---")
            try:
                func(*args, **kwargs)
            except Exception as e:
                log.exception(f"Error: {e}, trying again")
                time.sleep(.25)
            time.sleep(1)
            attempt_counter += 1
    return inner



def authenticate(driver, uname, pword):
    # Open model to input credentials
    driver.find_element(By.XPATH, '//div[@class="MenuContainer MenuContainer--desktop"]').click()
    time.sleep(1)
    
    driver.find_element(By.XPATH, '//div[@class="AuthView__Footer"]').click()
    time.sleep(1)

    driver.find_element(By.NAME, 'email').send_keys(uname)
    log.info('Inserted username')
    driver.find_element(By.NAME, 'password').send_keys(pword)
    log.info('Inserted password')
    
    # Submit credentials -> find button first
    driver.find_element(By.NAME, 'login_form').find_element(By.TAG_NAME, 'button').click()
    log.info('User logged in')
    


def reserve_time(driver, resy):
    log.info('Trying to reserve...')
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # time.sleep(5)
    #Click the reservation
    resy.click()
    time.sleep(0.5) # This can be .5 for headless, 1 for safari

    # Reserve now
    #driver.find_element(By.XPATH, '//button[@class="Button Button--primary Button--lg"]').click()

    # Jump into iframe
    book_now_iframe = driver.find_element(By.CSS_SELECTOR, "[title='Resy - Book Now']")
    driver.switch_to.frame(book_now_iframe)
    log.debug('Switched to iFrame')
    
    time.sleep(1)
    # Click reserve
    #TODO: Need to wait until this is available, it may be longer/shorter than 1 second. This is the point it got to.
    driver.find_element(By.XPATH, '//div[@class="SummaryPage__book"]').click()
    log.info(f'Reserved time at: {datetime.datetime.now()}')
    time.sleep(4)
    log.info('I Hope we reserved????')
    # Check if the confirmation was successful
    # success = driver.find_element(By.XPATH, '//div[@class="ConfirmationPage__header"]')
    # log.info(f"Success?: {success.text}")
    
    return True

    #wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(""))
    # Switch back 
    #driver.switch_to.default_content()
    


@time_waiter
def check_availability(driver, url):
    driver.get(url)
    log.info(f"Getting url: {datetime.datetime.now()}")
    time.sleep(0.5) # This can be .5 for headless, 1.5 for safari

    slots = driver.find_element(By.XPATH, '//div[@class="ReservationButtonList ShiftInventory__shift__slots"]')
    log.info('Got reservation element')
    # Grab the available reservatins
    reservations = slots.find_elements(By.TAG_NAME, 'button')
    log.info(f"Available Reservations: {len(reservations) - 1}")
    if len(reservations) == 1:
        # There are no reservations, user should be notified
        log.info(f'There are no reservations')
        return

    for resy in reservations:
        # Check if there are resevations
        if resy.text != 'Notify':
            resy_time = resy.find_element(By.CLASS_NAME, "ReservationButton__time").text
            type = resy.find_element(By.CLASS_NAME, "ReservationButton__type").text
            # if resy_time == '5:00 PM':
            #     print('MATCHED RESERVING')
            #     reserve_time(driver, resy)
            log.info(f'Reserving Time: {resy_time}')
            if reserve_time(driver, resy):
                driver.close()
                log.info('---Closing Session---')
                sys.exit()


def main(driver):
    log.info('---Opening Session---')
    
    log.info('Opening browser')

    # Create URL (Tatiana reservation is 27 days away)
    reservation_date = datetime.datetime.now() + datetime.timedelta(days=28)
    adjusted_date = datetime.datetime(year=reservation_date.year, month=reservation_date.month, day=reservation_date.day, hour=12, minute=0, second=0)
    log.info(f'Trying to book reservation around {adjusted_date}')
    url = create_url(restaurant='tatiana', party_size=2, date=adjusted_date)
    #url = create_url(restaurant='cervos', party_size=2, date=adjusted_date)
    log.info(f'Created url: {url}')

    # test_URL
    driver.get(url)
    log.info('First request to url')

    time.sleep(1)

    # Authenticate user
    authenticate(driver, UNAME, PWORD)
    time.sleep(5)

    check_availability(driver, url)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', choices=['headless', 'safari'], help='The choice of execution, safari or headless(chrome)')

    args = parser.parse_args()

    if args.type == 'headless':
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)

    else:
        driver = webdriver.Safari(port=0, executable_path="/usr/bin/safaridriver", quiet=False)

    driver.maximize_window()

    main(driver)
