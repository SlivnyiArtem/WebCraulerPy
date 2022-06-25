import urllib

import requests


class RobotParser:
    """ Парсер robots.txt """
    def __init__(self, domains):
        disallow_list = set()
        right_user_agent = False

        for domain in domains:
            if requests\
                    .get("https://" + domain + "/robots.txt")\
                    .status_code == 200:
                url_for_domain = "https://" + domain + "/robots.txt"
            elif requests\
                    .get("http://" + domain + "/robots.txt")\
                    .status_code == 200:
                url_for_domain = "http://" + domain + "/robots.txt"
            else:
                continue
            try:
                for line in urllib.request.urlopen(url_for_domain):
                    robots_line = line.decode('utf-8')
                    if right_user_agent and robots_line.startswith('Disallow'):
                        res_line = \
                            robots_line.replace(': ', '\n').split("\n")[1]
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
