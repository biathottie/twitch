import time
from csv import DictReader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from xpath_and_css_selectors import *
from point_logic import get_points, how_much_to_bet, time_set

CHANNEL_NAME = "ludwig"
STREAMER = f"https://www.twitch.tv/{CHANNEL_NAME}"

driver = webdriver.Chrome()

def get_cookie_values(file):
    """
    Takes all the cookies from our csv file.
    Turns them into a list of dicts
    :param file: csv file
    :return: a list of dicts
    """
    with open(file, encoding="utf-8-sig") as f:
        dict_reader = DictReader(f)
        list_of_dicts = list(dict_reader)
    return list_of_dicts

def upload_cookies():
    """
    Reads and adds cookies to our browser. Refreshes the page when it's done.
    """
    cookies = get_cookie_values("twitch_cookies.csv")
    for i in cookies:
        driver.add_cookie(i)

    driver.refresh()

if __name__ == "__main__":
    driver.get(STREAMER)
    upload_cookies()

    while True:
        try:
            time.sleep(10)
            channel_points = driver.find_element(By.XPATH, my_channel_points).click()
            time.sleep(2)

            try:
                driver.find_element(By.XPATH, getting_started_prompt).click()
            except NoSuchElementException as e:
                pass

            time.sleep(2)
            driver.find_element(By.XPATH, channel_prediction_prompt).click()

            is_submission_closed = driver.find_element(
                By.CSS_SELECTOR, submission_text
            ).text.lower()

            if "closed" in is_submission_closed:
                try:
                    driver.find_element(By.XPATH, x_button).click()
                except NoSuchElementException as e:
                    pass
                time.sleep(30)
                continue
            elif "ended" in is_submission_closed:
                try:
                    driver.find_element(By.XPATH, x_button).click()
                except NoSuchElementException as e:
                    pass
                time.sleep(30)
                continue
            else:
                pass

            try:
                my_points = driver.find_element(By.XPATH, points_xpath).text
                total_points = get_points(my_points)
                #TODO: figure out how much to bet
                points_to_bet = 100

            except NoSuchElementException as e:
                try:
                    driver.find_element(By.XPATH, x_button).click()
                except NoSuchElementException as e:
                    continue
                continue

            total_time_remaining = driver.find_element(By.XPATH, timer).text
            lastSpace = total_time_remaining.rfind(' ')
            total_time_remaining = total_time_remaining[lastSpace:]
            total_time_for_func = total_time_remaining.split()[0]
            time_set(total_time_for_func)
            time.sleep(2)

            #WORKS TO HERE

            tbv = driver.find_element(By.XPATH, blue_votes).text
            trv = driver.find_element(By.XPATH, red_votes).text

            if tbv == "":
                total_blue_votes = 0
            else:
                total_blue_votes = get_points(tbv)

            if trv == "":
                total_red_votes = 0
            else:
                total_red_votes = get_points(trv)

            driver.find_element(By.XPATH, predict_with_custom_amount).click()

            #TODO: make EV calculator to figure out what side to bet
            if total_blue_votes > total_red_votes:
                red = driver.find_element(By.XPATH, red_field)
                red.click()
                time.sleep(2)
                red.send_keys(points_to_bet)
                time.sleep(2)
                red_vote_button = driver.find_element(By.XPATH, red_button)
                red_vote_button.click()
                time.sleep(2)
                driver.find_element(By.XPATH, red_end).click()
            else:
                blue = driver.find_element(By.XPATH, blue_field)
                blue.click()
                time.sleep(2)
                blue.send_keys(points_to_bet)
                time.sleep(2)
                blue_vote_button = driver.find_element(By.XPATH, blue_button)
                blue_vote_button.click()
                time.sleep(2)
                driver.find_element(By.XPATH, blue_end).click()
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            pass
        except StaleElementReferenceException:
            driver.refresh()

        time.sleep(30)