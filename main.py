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
robot_parser = None

class NewRobotParser:
    def __init__(self, robots_txt_url):
        disallow_list = []
        right_user_agent = False

        for line in urllib.request.urlopen(robots_txt_url):
            robots_line = line.decode('utf-8')
            if right_user_agent and robots_line.startswith('Disallow'):
                res_line = robots_line.replace(': ', '\n').split("\n")[1]
                disallow_list.append(res_line)
            if "User-agent: *" in robots_line:
                print("USER")
                right_user_agent = True


        '''
        with os.popen("curl " + robots_txt_url).read() as robots_file:
            print("OPEN")
            data = robots_file.read()
            for line in data.split("\n"):
                if right_user_agent and line.startswith('Disallow'):
                    disallow_list.append(line.split(": ")[1])
                if "User-agent: *" in line:
                    print("USER")
                    right_user_agent = True
        '''
        self.disallow = disallow_list
        print(disallow_list)

    def can_fetch(self, url_for_fetch):
        for disallow_member in self.disallow:
            if disallow_member in url_for_fetch:
                return False
        return True


class RobotParser:
    def __init__(self, robots_txt_url):
        print("@@@@")
        response = requests.get(robots_txt_url)
        if response.status_code != 200:
            return
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(robots_txt_url)
        self.robot_parser.read()

    def can_fetch(self, url, user_agent="*"):
        # return True
        # print("@@@@@@@@@" + " " + url)
        result = self.robot_parser.can_fetch(user_agent, url)
        if not result:
            print("MISSED " + url)
        return result


class perpetual_timer():
    def __init__(self, t, hFunction, pos_offset):
        self.t = t
        self.pos_offset = pos_offset
        self.hFunction = hFunction
        self.job = Timer(self.t, self.handle_function)

    def handle_function(self):
        with threading.Lock():
            new_args = url_queue.get()
        self.hFunction(new_args, self.pos_offset)
        self.pos_offset = None
        self.job = Timer(self.t, self.handle_function)
        self.job.start()


def initial(args):
    global updateFiles
    global domains
    global start_page
    global robot_parser
    updateFiles = args.updateFiles
    domains = args.domains
    start_page = args.page
    robot_parser = NewRobotParser("http://" + urlparse(start_page).netloc + "/robots.txt")
    '''
    robot_parser = RobotParser("http://" +
                               urlparse(start_page).netloc + "/robots.txt")
    '''
    url_queue.put(start_page)


def crauler(current_url, offset):
    global robot_parser
    print(current_url + " current_url_for_crauler")
    # print(str(offset) + " offset")
    if not on_pause:
        visited.add(current_url)

        title = unquote(current_url).split('/')
        title = title[-1]

        if offset is not None:
            safe_html(current_url, offset)
        else:
            safe_multi_thread(100, current_url, title + ".html")

        for link in website_links(current_url, domains, robot_parser):
            if link not in visited:
                with threading.Lock():
                    url_queue.put(link)
            else:
                continue


def contains_file(file_name):
    sub_title = re.sub(r'[:></"\\|*?]', "_", file_name)
    return os.path.exists(sub_title)


def safe_html(cur_url, offset):
    # print(cur_url + " safe this html")
    if contains_file(cur_url):
        return
    # !!!! исправить на имя файла

    if offset is not None:
        print("OFFSET Is not None but " + str(offset))
        response = requests.head(cur_url)
        # print(response.headers)
        content_length = response.headers.get("content-length")
        # print(content_length)
        headers = {'Range': 'bytes=1000-10000'}

        response = requests.get(cur_url, headers=headers, stream=True)
        content = response.content
        code = response.status_code
        # print(len(content))
        # print(code)
        # print(response.headers)
    else:
        content = requests.get(cur_url).content

    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.string
    html_title = title + '.html'
    sub_title = re.sub(r'[:><\/"\\|*?]', "_", html_title)
    file = open(sub_title, "wb")
    soup_str = soup.encode("UTF8")
    file.write(soup_str)
    file.close()


def safe_multi_thread(size, file_url, file_name, threads_cnt=2):
    # print(file_name + " saving multi-thread")
    if contains_file(file_name):
        return
    part = int(size) / threads_cnt
    title = re.sub(r'[:></"\\|*?]', "_", file_name)
    fp = open(title, "wb")
    fp.write(b'\0' * size)
    fp.close()
    for i in range(threads_cnt):
        start = part * i
        end = start + part

        # create a Thread with start and end locations
        t = threading.Thread(target=safe_handler,
                             kwargs={'start': start,
                                     'end': end,
                                     'url': file_url,
                                     'filename': title})
        t.setDaemon(True)
        t.start()


def safe_handler(start, end, url, filename):
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
    except Exception:
        print("Invalid Key")


listener = keyboard.Listener(on_release=on_release)
listener.start()


def valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def website_links(url, domains, robot_parser):
    # print("###### " + url)
    # global robot_parser
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
            # print(domain_name)
            if domain_name in href:
                # print("lll")
                is_contains_in_domens = True
                break

        if not is_contains_in_domens:
            # print("*" + href)
            continue

        # print("###" + href)

        if not robot_parser.can_fetch(href):
            continue
        if href not in urls:
            # print(href)
            urls.add(href)
    # print(urls)
    # print(len(urls))
    return urls


def update_html_files():
    for filename in os.listdir(os.getcwd()):
        if '.html' in filename:
            with open(filename, encoding="UTF-8") as f:
                file = f.read()
                soup = BeautifulSoup(file, "html.parser")
                url = soup.find('link', rel=re.compile('canonical'))['href']
                index = file.find('dateModified')
                date = file[index + 15:index + 35]
                if '<' in date or '>' in date:
                    print("Not Apd")
                    continue
                else:
                    new_html = requests.get(url).text
                    index2 = new_html.find('dateModified')
                    date2 = new_html[index2 + 15:index2 + 35]
                    if date2 == date:
                        continue
                    else:
                        safe_html(url, None)


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
    # print(args.t + " Type")
    # print(args.domains)
    # print(args.page + " Start Page")
    # print(args.updateFiles + " Update")
    initial(args)

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
