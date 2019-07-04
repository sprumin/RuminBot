from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from slacker import Slacker
from urllib import parse

import re
import requests
import settings
import time


def send_message(message):
    slack = Slacker(settings.RUMIN_TOKEN)
    slack.chat.post_message(settings.ON_ON_BOT_TEST, message)


def record_lol(url, driver):
    driver.get(url)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

    driver.implicitly_wait(3)

    try:
        record_button = driver.find_elements_by_class_name("Recording")[0]
    except:
        print("Does not Game")
    else:
        record_button.click()


def download_record(url, driver, games):
    driver.get(url)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.implicitly_wait(3)

    try:
        download_button = driver.find_elements_by_id("right_match_replay")[0]
    except:
        print("Does not replay")
    else:
        download_button.click()
        time.sleep(5)


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--safebrowsing-disable-download-protection")

    driver = webdriver.Chrome("chromedriver", chrome_options=options)
    users = ["아는척좀하지말장"]
    games = list()

    for user in users:
        record_lol(f"https://www.op.gg/summoner/spectator/userName={parse.quote(user)}&", driver)
        download_record(f"https://www.op.gg/summoner/userName={user}", driver, games)


if __name__ == "__main__":
    main()
    """
    while True:
        main()
        time.sleep(600)
    """