import threading
import urllib
from queue import Queue
from pynput import keyboard
import lxml
import os
import time
import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from threading import Timer
import urllib.request as r
import argparse
from urllib.parse import unquote

start_page = None
url_queue = Queue()
domens = []

visited = set()
on_pause = False
robot_parser = None


class RobotParser:
    def __init__(self, robots_txt_url):
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(robots_txt_url)
        self.robot_parser.read()

    def can_fetch(self, url, user_agent="*"):
        return self.robot_parser.can_fetch(user_agent, url)


class perpetual_timer():
    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.job = Timer(self.t, self.handle_function)

    def handle_function(self):
        with threading.Lock():
            new_args: str = url_queue.get()
        self.hFunction(new_args)
        self.job = Timer(self.t, self.handle_function)
        self.job.start()


def crauler(current_url):
    print(current_url)
    if not on_pause:
        visited.add(current_url)

        title = unquote(current_url).split('/')
        title = title[-1]
        safe_multi_thread(100, current_url, title + ".html")

        for link in website_links(current_url):
            if link not in visited:
                with threading.Lock():
                    url_queue.put(link)
            else:
                continue


def contains_file(url):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    title = soup.title.string
    html_title = title + '.html'
    sub_title = re.sub(r'[:><\/"\\|*?]', "_", html_title)
    return os.path.exists(sub_title)


def safe_html(cur_url):
    print(cur_url)
    if contains_file(cur_url):
        return
    soup = BeautifulSoup(requests.get(cur_url).content, "html.parser")
    title = soup.title.string
    # print(cur_url)
    html_title = title + '.html'
    sub_title = re.sub(r'[:><\/"\\|*?]', "_", html_title)
    file = open(sub_title, "wb")
    soup_str = soup.encode("UTF8")
    file.write(soup_str)
    file.close()


def safe_multi_thread(size, file_url, file_name, threads_cnt = 2):
    part = int(size) / threads_cnt
    fp = open(file_name, "wb")
    fp.write(b'\0' * size)
    fp.close()
    for i in range(threads_cnt):
        start = part * i
        end = start + part

        # create a Thread with start and end locations
        t = threading.Thread(target=safe_handler,
                             kwargs={'start': start, 'end': end, 'url': file_url, 'filename': file_name})
        t.setDaemon(True)
        t.start()


def safe_handler(start, end, url, filename):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(filename, "r+b") as fp:
        print(int(start))
        fp.seek(int(start))
        fp.write(r.content)
    print("CLOSED")


def on_release(key):
    global on_pause
    try:
        if key.vk == 80:
            on_pause = not on_pause
    except Exception:
        print("Invalid Key")


listener = keyboard.Listener(on_release=on_release)
listener.start()


def valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def website_links(url):
    urls = set()
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not valid_url(href):
            continue

        is_contains_in_domens = False

        for domain_name in domens:
            if domain_name in href:
                is_contains_in_domens = True
                break

        if is_contains_in_domens == False:
            continue

        if not robot_parser.can_fetch(href):
            continue
        urls.add(href)
    return urls


def initial(args):
    global domens
    global start_page
    global robot_parser
    domens = args.domens
    start_page = args.page
    robot_parser = RobotParser("http://" + urlparse(start_page).netloc + "/robots.txt")
    url_queue.put(start_page)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-t', type=str, help='type',
    )

    parser.add_argument('--domens', nargs='*', help='domens')

    parser.add_argument('--page', type=str, help="start page")

    args = parser.parse_args()
    print(args.t + " Type")
    print(args.domens)
    print(args.page + " Start Page")

    initial(args)
    if args.t == "tm":
        t = perpetual_timer(1, crauler)
        t.job.start()
        t1 = perpetual_timer(3, crauler)
        t1.job.start()
    else:
        print("unknown type")
