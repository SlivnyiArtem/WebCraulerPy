import argparse
import os
import re
import threading
from urllib.parse import urlparse, urljoin, unquote

import requests
from bs4 import BeautifulSoup
from pynput import keyboard

from perpetual_timer import perpetual_timer, on_release, url_queue
from robot_parser import RobotParser
from safe_functions import safe_html, safe_multi_thread

start_page = None

domains = []

visited = set()

q_type = None
robot_parser = RobotParser(domains)


def initial(arg_type, arg_domains, arg_page):
    global domains
    global start_page
    global robot_parser
    global q_type
    q_type = arg_type
    domains = arg_domains
    start_page = arg_page
    robot_parser = RobotParser(domains)
    url_queue.put(start_page)


def crauler(current_url, offset):
    """обрабатывает текущий url, вызывая функцию сохранения страни
    цы и добавляя в список на посещение результат
    функции поиска ссылок на текущей странице """

    print(current_url + " current_url_for_crauler")
    visited.add(current_url)

    title = unquote(current_url).split('/')
    title = title[-1]

    if offset is not None or q_type != "tm":
        print("safe one thread")
        safe_html(current_url, offset)
    else:
        print("safe multi thread")
        safe_multi_thread(current_url, title + ".html")

    for link in website_links(current_url, domains, robot_parser):
        if link not in visited:
            with threading.Lock():
                url_queue.put(link)
        else:
            continue


listener = keyboard.Listener(on_release=on_release)
listener.start()


def valid_url(url):
    """ функция проверяющая наличие протокольного префикса и коррек
    тность доменного имени по url """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def website_links(url, domains, robot_parser):
    """ функция, возвращающая множество ссылок, найденных на html -
     странице по данному url, удовлетворяющих
    robots.txt и принадлежащих множеству доменов, указанных в
    качестве параметров"""
    urls = set()
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://"
        href = href + parsed_href.netloc + parsed_href.path
        if not valid_url(href):
            continue

        is_contains_in_domens = False

        for domain_name in domains:
            if domain_name in href:
                is_contains_in_domens = True
                break
        if not is_contains_in_domens:
            continue

        if not robot_parser.can_fetch(href):
            continue
        if href not in urls:
            urls.add(href)
    return urls


def update_html_files():
    """ функция, обновляющая содержимое сохраненных html - файлов """
    for filename in os.listdir(os.getcwd()):
        if '.html' in filename:
            message = None
            with open(filename, encoding="UTF-8") as f:
                try:
                    file = f.read()
                except UnicodeDecodeError:
                    continue
                if len(file) > 0:
                    soup = BeautifulSoup(file,
                                         "html.parser")
                    url = soup.find('link',
                                    rel=re.compile('canonical'))['href']
                    index = file.find('dateModified')
                    date = file[index + 15:index + 35]
                    if '<' in date or '>' in date:
                        continue
                    else:
                        new_html = requests.get(url).text
                        index2 = new_html.find('dateModified')
                        date2 = new_html[index2 + 15:index2 + 35]
                        if date2 == date:
                            continue
                        else:
                            safe_html(url, None, is_update=True)
                else:
                    message = f"Данный файл: {filename}" \
                              f" не содержал информацию " \
                              f"о url по которому его можно обновить"
            if message is not None:
                with open(filename, "w", encoding="UTF-8") as f:
                    f.write(message)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-t', type=str, help='type',
    )

    parser.add_argument('--domains', nargs='*', help='domains')

    parser.add_argument('--page', type=str, help="start page")

    parser.add_argument('--offset', type=int, help="recovery offset",
                        default=None)

    parser.add_argument('--updateFiles', type=str, help='update files')

    args = parser.parse_args()
    initial(args.t, args.domains, args.page)

    if args.updateFiles == "1":
        update_html_files()

    if args.t == "tm":
        t = perpetual_timer(1, crauler, None)
        t.job.start()
        t1 = perpetual_timer(3, crauler, None)
        t1.job.start()

    elif args.t == "or":
        t = perpetual_timer(1, crauler, args.offset)
        t.job.start()

    else:
        print("unknown type")


if __name__ == '__main__':
    main()
