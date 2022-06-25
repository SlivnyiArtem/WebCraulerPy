import os
import re
import threading

import requests
from bs4 import BeautifulSoup


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


def contains_file(file_name):
    """ функция проверки существания файла по его имени"""
    sub_title = re.sub(r'[:></"\\|*?]', "_", file_name)
    return os.path.exists(sub_title)


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
