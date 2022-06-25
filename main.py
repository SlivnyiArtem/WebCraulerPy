import argparse
import threading
import urllib
from queue import Queue
from pynput import keyboard
import os
import re
from bs4 import BeautifulSoup
import requests
import urllib.robotparser
from urllib.parse import urlparse, urljoin, unquote
from urllib.request import urlopen
from threading import Timer

start_page = None
url_queue = Queue()
domains = []

visited = set()
on_pause = False
q_type = None


class RobotParser:
    """ Парсер robots.txt """

    def __init__(self, domains):
        disallow_list = set()
        right_user_agent = False

        for domain in domains:
            if requests.get("https://" + domain + "/robots.txt").status_code == 200:
                url_for_domain = "https://" + domain + "/robots.txt"
            elif requests.get("http://" + domain + "/robots.txt").status_code == 200:
                url_for_domain = "http://" + domain + "/robots.txt"
            else:
                continue
            try:
                for line in urllib.request.urlopen(url_for_domain):
                    robots_line = line.decode('utf-8')
                    if right_user_agent and robots_line.startswith('Disallow'):
                        res_line = robots_line.replace(': ', '\n').split("\n")[1]
                        disallow_list.add(res_line)
                    if "User-agent: *" in robots_line:
                        right_user_agent = True
            except urllib.error.URLError:
                continue
        self.disallow = disallow_list


    def can_fetch(self, url_for_fetch):
        """ Проверка доступности url для краулинга """
        for disallow_member in self.disallow:
            if disallow_member in url_for_fetch:
                return False
        return True


class perpetual_timer():
    """ Класс, экземпляр которырого вызывает hFunction каждые t млс"""

    def __init__(self, t, hFunction, pos_offset):
        self.t = t
        self.pos_offset = pos_offset
        self.hFunction = hFunction
        self.job = Timer(self.t, self.handle_function)

    def handle_function(self):
        """функция, руководящая выполнением переданной функции, а также переопределяющая таймер для следующего
        периода """
        if not on_pause:
            with threading.Lock():
                new_args = url_queue.get()
            self.hFunction(new_args, self.pos_offset)
            self.pos_offset = None
        self.job = Timer(self.t, self.handle_function)
        self.job.start()


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
    """обрабатывает текущий url, вызывая функцию сохранения страницы и добавляя в список на посещение результат
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



def contains_file(file_name):
    """ функция проверки существания файла по его имени"""
    sub_title = re.sub(r'[:></"\\|*?]', "_", file_name)
    return os.path.exists(sub_title)


def safe_html(cur_url, offset, is_update=False):
    """ функция, сохранияющая файл в папку с проектом в однопоточном режиме """
    if offset is not None:
        print("OFFSET Is not None but " + str(offset))
        response = requests.head(cur_url)
        content_length = response.headers.get("content-length")
        range_header = f'bytes={offset}-{content_length}'
        headers = {'Range': range_header}

        response = requests.get(cur_url, headers=headers, stream=True)
        content = response.content
        code = response.status_code
        print(code)
    else:
        content = requests.get(cur_url).content

    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.string
    html_title = title + '.html'
    sub_title = re.sub(r'[:></"\\|*?]', "_", html_title)
    if contains_file(sub_title) and not is_update:
        print("File already contains")
        return
    file = open(sub_title, "wb")
    soup_str = soup.encode("UTF8")
    file.write(soup_str)
    file.close()


def safe_multi_thread(file_url, file_name, threads_cnt=2):
    """ функция, сохранияющая файл в папку с проектом в двухпоточном режиме """
    response = requests.head(file_url)
    content_length = response.headers.get("content-length")
    if content_length is None:
        content_length = 10000
    part = int(content_length) / threads_cnt
    title = re.sub(r'[:></"\\|*?]', "_", file_name)
    if contains_file(title):
        print("File already contains")
        return
    fp = open(title, "wb")
    fp.write(b'\0' * int(content_length))
    fp.close()
    for i in range(threads_cnt):
        start = part * i
        end = start + part
        thread = threading.Thread(target=safe_handler,
                                  kwargs={'start': start,
                                          'end': end,
                                          'url': file_url,
                                          'filename': title})
        thread.daemon = True
        thread.start()


def safe_handler(start, end, url, filename):
    """ Функция - task, сохраняющая часть файла"""
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(filename, "r+b") as fp:
        fp.seek(int(start))
        fp.write(r.content)


def on_release(key):
    global on_pause
    try:
        if key.vk == 80:
            on_pause = not on_pause
    except AttributeError:
        print("Invalid Key")


listener = keyboard.Listener(on_release=on_release)
listener.start()


def valid_url(url):
    """ функция проверяющая наличие протокольного префикса и корректность доменного имени по url """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def website_links(url, domains, robot_parser):
    """ функция, возвращающая множество ссылок, найденных на html - странице по данному url, удовлетворяющих
    robots.txt и принадлежащих множеству доменов, указанных в качестве параметров"""
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


if __name__ == '__main__':

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
