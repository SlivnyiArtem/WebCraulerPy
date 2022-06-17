import unittest
from urllib.parse import urlparse

import main


class RobotParserTests(unittest.TestCase):
    def test_robot_parser_can_not_fetch(self):
        robot_parser = main.NewRobotParser("https://en.wikipedia.org/robots.txt")
        fetch_result = robot_parser.can_fetch("/wiki/Wikipedia:Articles_for_deletion")
        print(fetch_result)
        self.assertEqual(fetch_result, False)

    def test_robot_parser_can_fetch_true(self):
        robot_parser = main.NewRobotParser("https://en.wikipedia.org/robots.txt")
        fetch_result = robot_parser.can_fetch("https://ru.wikipedia.org/wiki/%D0%9C%D1%91%D1%80%"
                                              "D1%82%D0%B2%D1%8B%D0%B5_%D0%B4%D1%83%D1%88%D0%B8")
        print(fetch_result)
        self.assertEqual(fetch_result, True)


class CheckValidUrlTests(unittest.TestCase):
    def test_unvalid_url_test(self):
        self.assertEqual(main.valid_url("://ru.wikipedia.org/"
                                        "%D0%9D%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9"
                                        "%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D0%A2%D0%B5-%D0%9F%D0%B0%D0%BF%D0%B0-%D0%A"
                                        "2%D0%BE%D0%BD%D0%B3%D0%B0%D1%80%D0%B5%D0%B2%D0%B0"), False)

    def test_valid_url(self):
        self.assertEqual(main.valid_url("https://www.kinopoisk.ru/series/1227803/"), True)


class WebsiteLinksTests(unittest.TestCase):
    def test_find_all_links(self):
        correct_links = {
            'https://ru.wikipedia.org/wiki/%D0%A8%D1%82%D0%B0%D0%B4%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%B2_%D0%9D%D0%B8%D0%B6%D0%BD%D0%B5%D0%B9_%D0%A1%D0%B0%D0%BA%D1%81%D0%BE%D0%BD%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9F%D0%A0%D0%9E:%D0%90%D0%A2%D0%94:%D0%9F%D0%BE%D1%81%D0%BB%D0%B5%D0%B4%D0%BD%D1%8F%D1%8F_%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0:_%D0%B2_%D0%BF%D1%80%D0%BE%D1%88%D0%BB%D0%BE%D0%BC_%D0%B3%D0%BE%D0%B4%D1%83',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BE%D0%B4%D0%B5%D1%80%D0%B6%D0%B0%D0%BD%D0%B8%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D1%82%D0%B5%D1%80%D1%85%D0%BE%D0%BB%D1%8C%D1%86_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F_%D0%BE%D0%B1_%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B0%D1%85',
            'https://ru.wikipedia.org/wiki/%D0%AD%D0%B4%D0%B5%D0%BC%D0%B8%D1%81%D1%81%D0%B5%D0%BD',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%9A%D1%83%D0%BA%D1%81%D1%85%D0%B0%D1%84%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9B%D1%8E%D0%BD%D0%B5%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%BD%D0%B4%D0%B5%D0%B1%D1%83%D1%80%D0%B3',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%B7%D0%B5%D1%80%D0%BC%D0%B0%D1%80%D1%88_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%A4%D0%BE%D1%80%D1%83%D0%BC',
            'https://ru.wikipedia.org/wiki/%D0%AD%D0%BC%D0%B4%D0%B5%D0%BD',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Coat_of_arms_of_Lower_Saxony.svg',
            'https://ru.wikipedia.org/wiki/%D0%9B%D1%8E%D1%85%D0%BE%D0%B2-%D0%94%D0%B0%D0%BD%D0%BD%D0%B5%D0%BD%D0%B1%D0%B5%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9D%D0%B5%D0%BC%D0%B5%D1%86%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%90%D0%B4%D0%BC%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B5_%D0%B5%D0%B4%D0%B8%D0%BD%D0%B8%D1%86%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83',
            'https://ru.wikipedia.org/wiki/%D0%9D%D0%BE%D1%80%D1%82%D1%85%D0%B0%D0%B9%D0%BC_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D0%BE%D0%B5_%D0%B4%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9D%D0%BE%D0%B2%D1%8B%D0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
            'https://ru.wikipedia.org/wiki/%D0%94%D0%B8%D0%BF%D1%85%D0%BE%D0%BB%D1%8C%D1%86_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%B8%D0%BB%D1%8C%D0%B4%D0%B5%D1%81%D1%85%D0%B0%D0%B9%D0%BC_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%93%D1%91%D1%82%D1%82%D0%B8%D0%BD%D0%B3%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%AD%D0%BC%D1%81%D0%BB%D0%B0%D0%BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A4%D1%80%D0%B8%D1%81%D0%BB%D0%B0%D0%BD%D0%B4%D0%B8%D1%8F_(%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F)',
            'https://ru.wikipedia.org/wiki/Википедия:Текст_лицензии_Creative_Commons_Attribution-ShareAlike_3.0_Unported',
            'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D0%B3%D0%BE%D1%80%D0%BE%D0%B4,_%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F)',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%B2%D1%8F%D0%B7%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B8/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9B%D0%B5%D0%BD%D0%B3%D0%B5%D0%B4%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%9B%D0%B0%D1%88%D1%82%D0%B5%D0%B4%D1%82',
            'https://ru.wikipedia.org/wiki/%D0%93%D1%80%D0%B0%D1%84%D1%81%D1%82%D0%B2%D0%BE_%D0%91%D0%B5%D0%BD%D1%82%D1%85%D0%B0%D0%B9%D0%BC_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%90%D0%BC%D0%BC%D0%B5%D1%80%D0%BB%D0%B0%D0%BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F',
            'https://ru.wikipedia.org/wiki/%D0%91%D1%80%D0%B0%D1%83%D0%BD%D1%88%D0%B2%D0%B0%D0%B9%D0%B3',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%9E%D1%82%D0%BA%D0%B0%D0%B7_%D0%BE%D1%82_%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BF%D0%B5%D1%86%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
            'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F:%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD_%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5:%D0%93%D0%BE%D1%80%D0%BE%D0%B4%D0%B0',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%85%D0%B5%D0%BB%D1%8C%D0%B4%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%B6%D0%BD%D1%8F%D1%8F_%D0%A1%D0%B0%D0%BA%D1%81%D0%BE%D0%BD%D0%B8%D1%8F',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0',
            'https://ru.wikipedia.org/wiki/%D0%93%D0%B8%D1%84%D1%85%D0%BE%D1%80%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%A2%D0%B5%D0%BA%D1%83%D1%89%D0%B8%D0%B5_%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D1%8F',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Lower_saxony_pe.png',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Lage_des_Landkreises_Peine_in_Deutschland.PNG',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B2%D0%B0%D0%B4%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%B9_%D0%BA%D0%B8%D0%BB%D0%BE%D0%BC%D0%B5%D1%82%D1%80',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9F%D0%A0%D0%9E:%D0%90%D0%A2%D0%94:%D0%A0%D0%B0%D0%B7%D0%BC%D0%B5%D1%80_%D1%81%D1%82%D0%B0%D1%82%D1%8C%D0%B8:_%D0%BC%D0%B5%D0%BD%D0%B5%D0%B5_1000_%D1%81%D0%B8%D0%BC%D0%B2%D0%BE%D0%BB%D0%BE%D0%B2',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%98%D0%B7%D0%B1%D1%80%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5_%D1%81%D1%82%D0%B0%D1%82%D1%8C%D0%B8',
            'https://ru.wikipedia.org/wiki/1885_%D0%B3%D0%BE%D0%B4',
            'https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD_%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%97%D0%BE%D0%BB%D1%8C%D1%82%D0%B0%D1%83-%D0%A4%D0%B0%D0%BB%D0%BB%D0%B8%D0%BD%D0%B3%D0%B1%D0%BE%D1%81%D1%82%D0%B5%D0%BB%D1%8C_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9E%D0%BB%D1%8C%D0%B4%D0%B5%D0%BD%D0%B1%D1%83%D1%80%D0%B3',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%80%D0%B4%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%9D%D0%B8%D0%B6%D0%BD%D0%B5%D0%B9_%D0%A1%D0%B0%D0%BA%D1%81%D0%BE%D0%BD%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0',
            'https://ru.wikipedia.org/wiki/%D0%93%D0%B0%D0%BD%D0%BD%D0%BE%D0%B2%D0%B5%D1%80_(%D1%80%D0%B5%D0%B3%D0%B8%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D1%81%D1%8B%D0%BB%D0%BA%D0%B8_%D1%81%D1%8E%D0%B4%D0%B0/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Wappen_Landkreis_Peine.svg',
            'https://ru.wikipedia.org/wiki/Википедия:Контакты',
            'https://ru.wikipedia.org/wiki/%D0%93%D0%BE%D1%81%D0%BB%D0%B0%D1%80_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%98%D0%BB%D1%8C%D1%86%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%BE%D0%BB%D1%8C%D1%84%D0%B5%D0%BD%D0%B1%D1%8E%D1%82%D1%82%D0%B5%D0%BB%D1%8C_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0:%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BB%D1%8C%D0%BC%D0%B5%D0%BD%D1%85%D0%BE%D1%80%D1%81%D1%82',
            'https://ru.wikipedia.org/wiki/%D0%A0%D0%BE%D1%82%D0%B5%D0%BD%D0%B1%D1%83%D1%80%D0%B3-%D0%BD%D0%B0-%D0%92%D1%8E%D0%BC%D0%BC%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%B2%D0%B5%D0%B6%D0%B8%D0%B5_%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D1%91_%D0%BE%D0%B1%D1%81%D1%83%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%B0%D0%BC%D0%B5%D0%BB%D1%8C%D0%BD-%D0%9F%D0%B8%D1%80%D0%BC%D0%BE%D0%BD%D1%82_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BE%D1%86%D0%B8%D0%B0%D0%BB-%D0%B4%D0%B5%D0%BC%D0%BE%D0%BA%D1%80%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F_%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D1%8F_%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%98%D0%BB%D1%8C%D0%B7%D0%B5%D0%B4%D0%B5',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D1%82%D1%82%D0%BC%D1%83%D0%BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D0%BB%D1%8C%D1%86%D0%BC%D0%B8%D0%BD%D0%B4%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%BB%D0%BE%D0%BF%D0%BF%D0%B5%D0%BD%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9B%D0%B5%D1%80_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9B%D0%B0%D0%BD%D0%B4%D1%80%D0%B0%D1%82',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D0%B9_%D0%B2%D0%BA%D0%BB%D0%B0%D0%B4',
            'https://ru.wikipedia.org/wiki/%D0%90%D1%83%D1%80%D0%B8%D1%85_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%B0%D1%80%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D1%82%D0%B5%D1%80%D0%BE%D0%B4%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A6%D0%B5%D0%BB%D0%BB%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%85%D1%82%D0%B0_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%B5%D0%BB%D1%8C%D0%BC%D1%88%D1%82%D0%B5%D0%B4%D1%82_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D1%8D%D0%BD%D1%85%D0%B0%D0%BC%D0%B5%D0%BB%D1%8C%D0%BD',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BB%D1%8C%D0%B3%D0%B5%D0%BB%D1%8C%D0%BC%D1%81%D1%85%D0%B0%D1%84%D0%B5%D0%BD',
            'https://ru.wikipedia.org/wiki/%D0%9E%D0%BB%D1%8C%D0%B4%D0%B5%D0%BD%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%B0%D0%B1%D1%80%D1%8E%D0%BA_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%BE',
            'https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%BB%D1%8C%D1%86%D0%B3%D0%B8%D1%82%D1%82%D0%B5%D1%80',
            'https://ru.wikipedia.org/wiki/%D0%92%D0%BE%D0%BB%D1%8C%D1%84%D1%81%D0%B1%D1%83%D1%80%D0%B3',
            'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D1%83%D0%BC%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
            'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D0%B8',
            'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%B0%D0%B1%D1%80%D1%8E%D0%BA'}
        real_links = main.website_links(
            "https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)",
            ["ru.wikipedia.org"], main.RobotParser("http://" +
                                                   urlparse(
                                                       "https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)").netloc + "/robots.txt"))
        self.assertSetEqual(correct_links, real_links)


'''
class TestSum(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

class TestSum2(unittest.TestCase):
    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
'''

if __name__ == '__main__':
    unittest.main()