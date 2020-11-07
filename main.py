import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime

BASE_URL = "https://www.hotpepper.jp"
# 対象地域を変えたい場合はここを修正する
LIST_URL = "campaign/gotoeat/SA15/Y925"


class Restaurant:
    name = ""
    url = ""
    checked_date = ""

    def __repr__(self):
        return f'name="{self.name}", url={self.url}'

    def to_dict(self):
        return {'name': self.name, 'url': self.url, 'checked_date': self.checked_date}
# 指定されたインデックスのページを返す


def get_list_page(page_idx):
    url = f'{BASE_URL}/{LIST_URL}/bgn{page_idx}'
    response = requests.get(url)
    return response

# ページ数を返す


def get_list_num():
    response = get_list_page(1)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 1/7ページみたいな文字列が取れる
    page_info = soup.select_one('li.lh27')
    max_page_info = re.search(r'\/(\d+)', page_info.string)
    return int(max_page_info.group(1))

# ページを解析して店のリストを返す


def analyze_page(page_text):
    soup = BeautifulSoup(page_text, 'html.parser')
    rest_soups = soup.select('div.shopDetailTop')
    rest_list = []
    for rest_soup in rest_soups:
        rest = Restaurant()
        title_info = rest_soup.select_one('h3.detailShopNameTitle > a')
        rest.name = title_info.string
        rest.url = f'{BASE_URL}{title_info["href"]}'
        rest_list.append(rest)
    return rest_list


if __name__ == '__main__':
    # ページ数を調べる
    list_num = get_list_num()

    # 店のリストを取得
    rest_list = []
    for page_idx in range(1, list_num+1):
        page = get_list_page(page_idx)
        rest_list.extend(analyze_page(page.text))

    checked_rests = []
    new_rests = []
    # 店の名前　URL チェック日
    with open('./rest_list.csv', encoding='utf8') as f:
        reader = csv.DictReader(f)
        checked_rests = [r for r in reader]
    for rest in rest_list:
        duplicate_rests = [checked_rest for checked_rest in checked_rests if checked_rest['url'] == rest.url]

        if len(duplicate_rests)==0:
            rest.checked_date = datetime.date.today()
            new_rests.append(rest.to_dict())

    with open('./rest_list.csv', 'w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, ['name', 'url', 'checked_date'])
        writer.writeheader()
        for new_rest in new_rests:
            writer.writerow(new_rest)
        for checked_rest in checked_rests:
            writer.writerow(checked_rest)

        print("========new========")
        for new_rest in new_rests:
            print(new_rest)
