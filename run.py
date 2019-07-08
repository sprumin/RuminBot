from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from slacker import Slacker
from urllib import parse

import asyncio
import json
import re
import requests
# import settings
import sqlite3
import time
import websockets


_time = datetime.now()

slack = Slacker(settings.RUMIN_TOKEN)
response = slack.rtm.start()
endpoint = response.body['url']

# 진짜로 DB 이렇게 하기 싫었는데 비동기연동하면서 어떻게 써야할지 당장 생각이안나서 이렇게함.
conn = sqlite3.connect("db.sqlite3")
conn.text_factory = str
cur = conn.cursor()


def send_message(slack, message):
    slack.chat.post_message(settings.ON_ON_GENERAL, message)


def record_lol(driver, slack, url, username):
    driver.get(url)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")

    driver.implicitly_wait(3)

    try:
        record_button = driver.find_elements_by_class_name("Recording")[0]
    except:
        pass
    else:
        record_button.click()

        if not driver.find_elements_by_css_selector(".NowRecording.tip.tpd-delegation-uid-1"):
            send_message(slack, f"`{username}` 님이 현재 게임을 진행중입니다. 녹화를 시작합니다.")


def get_record_link(driver, slack, url, username, games):
    check_games = list()

    game_ids = re.findall(r"(data-game-id=\"\d+\")", requests.get(url).text)

    for _id in game_ids:
        split_id = _id.split("\"")[1]
        res = requests.get(f"https://www.op.gg/match/new/id={split_id}").content
        match_link = re.findall(r"(/match/new/batch/id=\d+)", res.decode())

        if match_link and split_id not in games:
            send_message(slack, f"`{username}` 님의 게임이 녹화되었습니다.\nhttps://op.gg{match_link[0]} 를 눌러 녹화파일을 다운로드 받아주세요.")
            check_games.append(split_id)

    return check_games


def get_last_data(table):
    cur.execute(f"select id from {table} order by id desc limit 1")
    last_id = cur.fetchall()
    try:
        return last_id[0][0]
    except:
        return 0


def time_check(legacy_time):
    now_time = datetime.now()

    if (now_time - legacy_time).seconds > 600:
        global _time
        _time = now_time

        return True


def main():
    # chromedriver
    driver = webdriver.Chrome("chromedriver")

    # sqlite3
    cur.execute("select name from User")
    users = cur.fetchall()

    cur.execute("select game_number from Games")
    games = [row[0] for row in cur.fetchall()]

    for user in users:
        record_lol(driver, slack, f"https://www.op.gg/summoner/spectator/userName={parse.quote(user[0])}&", user[0])
        check_games = get_record_link(driver, slack, f"https://www.op.gg/summoner/userName={user[0]}", user[0], games)
        print("game check", check_games)
        if check_games:
            for game in check_games:
                print('game', game)
                sql = "insert into Games(id, game_number) values (?, ?)"
                cur.execute(sql, (get_last_data("Games") + 1, game))

            conn.commit()

    driver.quit()


async def execute_bot():
    ws = await websockets.connect(endpoint)

    # Run Crawler
    main()

    while True:
        if time_check(_time):
            main()

        res = await ws.recv()
        message = json.loads(res)

        if message['type'] == "message":
            if message['text'].startswith("!롤 유저"):
                cur.execute("select name from User")
                users = [user[0] for user in cur.fetchall()]

                send_message(slack, f"현재 DB에 저장된 유저들 리스트입니다.\n {users}")
            elif message['text'].startswith("!롤 추가"):
                username = message['text'].split()[2]
                cur.execute("select name from User")
                users = [user[0] for user in cur.fetchall()]

                if username not in users:
                    sql = f"insert into User(id, name) values (?, ?)"
                    cur.execute(sql, (get_last_data('User') + 1, username))
                    conn.commit()

                    send_message(slack, f"{username} 님이 유저목록에 추가되었습니다.")
                else:
                    send_message(slack, "이미 존재하는 이름입니다.")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(execute_bot())
    asyncio.get_event_loop().run_forever()

    # main()
    """
    while True:
        main()
        time.sleep(600)
    """