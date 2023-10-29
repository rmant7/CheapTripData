from bs4 import BeautifulSoup
from pathlib import Path
import json


def href_modify():
    with open('../index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    for li_tag in soup.find_all('li'):
        a_tag = li_tag.find('a')
        a_tag['href'] = f'tree/city_descriptions/en/{Path(a_tag["href"]).name}'

    with open('../index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
        

if __name__ == '__main__':
    href_modify()