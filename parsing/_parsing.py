import os
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint


class StadionParser:

    def __init__(self, url):
        self.url = url
        self.write_json_file()

    def get_soup(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(e)
            return
        return soup

    def get_json_data(self):
        json_data: dict = {}
        soup = self.get_soup()

        online_tablo = soup.find("div", id="online_tablo")

        for i in range(1, 6):
            li_child = online_tablo.select(f"#online_tablo > ul > li:nth-child({i})")[0]

            online_tablo_game_list = li_child.find_all("ul", id="online_tablo_game")
            matches = []
            for online_tablo_game in online_tablo_game_list:

                li_list = online_tablo_game.find_all("li")
                keys = ["date", "time", "team1", "result", "team2"]
                data = []

                for li in li_list:
                    item = li.get_text(strip=True)
                    if " " in item:
                        date, time = item.split(" ")
                        data.append(date)
                        data.append(time)
                        continue
                    data.append(item)
                matches.append(dict(zip(keys, data)))

            liga_title = li_child.find("b").get_text(strip=True)
            json_data[liga_title] = matches
        return json_data

    def write_json_file(self):
        json_data = self.get_json_data()
        os.makedirs("data_files", exist_ok=True)
        with open("data_files/data.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)


class AsaxiyParser:
    pass





