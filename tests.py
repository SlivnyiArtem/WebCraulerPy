import os
import re
import unittest
from queue import Queue
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

import main

correct_links = {
    'https://ru.wikipedia.org/wiki/%D0%A8%D1%82%D0%'
    'B0%D0%B4%D0%B5_'
    '(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D'
    '0%B1%D0%BB%D0%BE%D'
    '0%BD:%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%B2'
    '_%D0%9D%D0%B8%D0%'
    'B6%D0%BD%D0%B5%D0%B9_%D0%A1%D0%B0%D0%BA%D1%81%D'
    '0%BE%D0%BD%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82'
    '%D0%B5%D0%B3%D0%BE%'
    'D1%80%D0%B8%D1%8F:%D0%9F%D0%A0%D0%9E:%D0%90%D0%A2'
    '%D0%94:%D0%9F%D0%BE'
    '%D1%81%D0%BB%D0%B5%D0%B4%D0%BD%D1%8F%D1%8F_%D0%BF'
    '%D1%80%D0%B0%D0%B'
    '2%D0%BA%D0%B0:_%D0%B2_%D0%BF%D1%80%D0%BE%D1%88%D0%'
    'BB%D0%BE%D0%BC_%D0%B3%D0%BE%D0%B4%D1%83',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D'
    '0%B8%D0%BF%D0%B5'
    '%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BE%D0%B4%D0%B5%D1%80%'
    'D0%B6%D0%B0%D0%BD%D0%B8%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D1%82%D0'
    '%B5%D1%80%D1%85%D'
    '0%BE%D0%BB%D1%8C%D1%86_(%D1%80%D0%B0%D0%B9%D0%BE%D'
    '0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0'
    '%B8%D0%BF%D0%B5%'
    'D0%B4%D0%B8%D1%8F:%D0%A1%D0%BE%D0%BE%D0%B1%D1%89%D0'
    '%B5%D0%BD%D0'
    '%B8%D1%8F_%D0%BE%D0%B1_%D0%BE%D1%88%D0%B8%D0%B1%D'
    '0%BA%D0%B0%D1%85',
    'https://ru.wikipedia.org/wiki/%D0%AD%D0%B4%D0%B5%D0%BC'
    '%D0%B8%D1%81%D1%81%D0%B5%D0%BD',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%'
    'B8%D0%BF%D0'
    '%B5%D0%B4%D0%B8%D1%8F:%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%'
    'D0%BD%D0%B8%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0'
    '%BD%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%9A%D1%83%D0%B'
    'A%D1%81%D1%85%D'
    '0%B0%D1%84%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9B%D1%8E%D0%BD'
    '%D0%B5%D0%B1%D1%83'
    '%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%'
    'BD%D0%B4%D0%B5%D0%B1%D1%83%D1%80%D0%B3',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%B'
    '7%D0%B5%D1%80%D0%B'
    'C%D0%B0%D1%80%D1%88_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3'
    '%D0%BB%D0%B0%D0%B'
    '2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0'
    '%BD%D0%B8%D1%86%D0%B0',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D'
    '0%B8%D0%BF%D'
    '0%B5%D0%B4%D0%B8%D1%8F:%D0%A4%D0%BE%D1%80%D1%83%D0'
    '%BC',
    'https://ru.wikipedia.org/wiki/%D0%AD%D0%BC%D0%B4%D0'
    '%B5%D0%BD',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0'
    '%BB:Coat_of_arms_of_Lower_Saxony.svg',
    'https://ru.wikipedia.org/wiki/%D0%9B%D1%8E%D1%85%D0%'
    'BE%D0%B2-%D0%94%D0%B0%D0%BD%D0%BD%D0%B5%D0%BD%D0%B1%'
    'D0%B5%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9D%D0%B5%D0%BC%D0%'
    'B5%D1%86%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%'
    'B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%90%D0%B4%D0%BC%D'
    '0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D'
    '0%B2%D0%BD%D1%8B%D0%B5_%D0%B5%D0%B4%D0%B8%D0%BD%D0%B8%'
    'D1%86%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B'
    '2%D0%B8%D1%82%D1%83',
    'https://ru.wikipedia.org/wiki/%D0%9D%D0%BE%D1%80%D1%82%'
    'D1%85%D0%B0%D0%B9%D0%BC_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D0%B8%'
    'D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%'
    'D0%BD%D0%BE%D0%B5_%D0%B4%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8'
    '%D0%B5_%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%'
    'D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9D%D0%BE%D0%B2%D1%8B%D'
    '0%B5_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
    'https://ru.wikipedia.org/wiki/%D0%94%D0%B8%D0%BF%D'
    '1%85%D0'
    '%BE%D0%BB%D1%8C%D1%86_(%D1%80%D0%B0%D0%B9%D0%BE%D0'
    '%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%B8%D0%BB%D'
    '1%8C%D'
    '0%B4%D0%B5%D1%81%D1%85%D0%B0%D0%B9%D0%BC_(%D1%80%D0'
    '%B0%D0'
    '%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%93%D1%91%D1%82%D'
    '1%82%D0'
    '%B8%D0%BD%D0%B3%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0'
    '%BE%D0'
    '%BD)',
    'https://ru.wikipedia.org/wiki/%D0%AD%D0%BC%D1%81%'
    'D0%BB%D0%'
    'B0%D0%BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A4%D1%80%D0%B8%'
    'D1%81%D0'
    '%BB%D0%B0%D0%BD%D0%B4%D0%B8%D1%8F_(%D0%93%D0%B5%D1'
    '%80%D0%'
    'BC%D0%B0%D0%BD%D0%B8%D1%8F)',
    'https://ru.wikipedia.org/wiki/Википедия:Текст_лиц'
    'ензии_Cr'
    'eative_Commons_Attribution-ShareAlike_3.0_Unport'
    'ed',
    'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%'
    'D0%BD%D0'
    '%B5_(%D0%B3%D0%BE%D1%80%D0%BE%D0%B4,_%D0%93%D0%B5%'
    'D1%80%D0'
    '%BC%D0%B0%D0%BD%D0%B8%D1%8F)',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%'
    'D0%B6%D0'
    '%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%B2%D1%8F%D0'
    '%B7%D0%B0'
    '%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BF%D1%80%D0%B0%D0%B2'
    '%D0%BA%D0'
    '%B8/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0%B0%'
    'D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9B%D0%B5%D0%BD%'
    'D0%B3%D0%'
    'B5%D0%B4%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%9B%D0%B0%D1%88%'
    'D1%82%D0'
    '%B5%D0%B4%D1%82',
    'https://ru.wikipedia.org/wiki/%D0%93%D1%80%D0%B0%D'
    '1%84%D1%'
    '81%D1%82%D0%B2%D0%BE_%D0%91%D0%B5%D0%BD%D1%82%D1%85'
    '%D0%B0%'
    'D0%B9%D0%BC_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%90%D0%BC%D0%BC%D'
    '0%B5%D1%8'
    '0%D0%BB%D0%B0%D0%BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%B'
    'E%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D'
    '0%BC%D0%B'
    '0%D0%BD%D0%B8%D1%8F',
    'https://ru.wikipedia.org/wiki/%D0%91%D1%80%D0%B0%D1'
    '%83%D0%B'
    'D%D1%88%D0%B2%D0%B0%D0%B9%D0%B3',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0'
    '%B8%D0%BF'
    '%D0%B5%D0%B4%D0%B8%D1%8F:%D0%9E%D1%82%D0%BA%D0%B0%D'
    '0%B7_%D0%'
    'BE%D1%82_%D0%BE%D1%82%D0%B2%D0%B5%D1%82%D1%81%D1%82'
    '%D0%B2%D0'
    '%B5%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%'
    'B6%D0%B'
    '5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BF%D0%B5%D1%86%D'
    '1%81%D1%8'
    '2%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B',
    'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D0%B1%D0%'
    'BB%D0%BE%'
    'D0%BD:%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8'
    'F:%D0%A0'
    '%D0%B0%D0%B9%D0%BE%D0%BD_%D0%9F%D0%B0%D0%B9%D0%BD%D0%'
    'B5:%D0%9'
    '3%D0%BE%D1%80%D0%BE%D0%B4%D0%B0',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%85%D0%B'
    '5%D0%B'
    'B%D1%8C%D0%B4%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%B6%D0%'
    'BD%D'
    '1%8F%'
    'D1%8F_%D0%A1%D0%B0%D0%BA%D1%81%D0%BE%D0%BD%D0%B8%D1%8F',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B'
    '6%D0'
    '%B5%D0'
    '%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9'
    '%D0%'
    'BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86'
    '%D0%B0',
    'https://ru.wikipedia.org/wiki/%D0%93%D0%B8%D1%84%D1%85%D0%'
    'BE%'
    'D1%80%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0'
    '%B0%'
    'D0%BB:%D0%A2%D0%B5%D0%BA%D1%83%D1%89%D0%B8%D0%B5_%D1%81%D'
    '0%BE'
    '%D0%B1%D1%8B%D1%82%D0%B8%D1%8F',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:Lo'
    'wer_s'
    'axony_pe.png',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:La'
    'ge_des'
    '_Landkreises_Peine_in_Deutschland.PNG',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%B2%D0%B0%D0%B4%D1'
    '%80%D0'
    '%B0%D1%82%D0%BD%D1%8B%D0%B9_%D0%BA%D0%B8%D0%BB%D0%BE%D0%B'
    'C%D0%'
    'B5%D1%82%D1%80',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0'
    '%B3%D0%'
    'BE%D1%80%D0%B8%D1%8F:%D0%9F%D0%A0%D0%9E:%D0%90%D0%A2%D0%9'
    '4:%D0%A'
    '0%D0%B0%D0%B7%D0%BC%D0%B5%D1%80_%D1%81%D1%82%D0%B0%D1%82%'
    'D1%8C%D'
    '0%B8:_%D0%BC%D0%B5%D0%BD%D0%B5%D0%B5_1000_%D1%81%D0%B8%D0'
    '%BC%D0%'
    'B2%D0%BE%D0%BB%D0%BE%D0%B2',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0'
    '%BF%D0%B5'
    '%D0%B4%D0%B8%D1%8F:%D0%98%D0%B7%D0%B1%D1%80%D0%B0%D0%BD%'
    'D0%BD%D1%8'
    'B%D0%B5_%D1%81%D1%82%D0%B0%D1%82%D1%8C%D0%B8',
    'https://ru.wikipedia.org/wiki/1885_%D0%B3%D0%BE%D0%B4',
    'https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B9%D0%BE%D0'
    '%BD_%D0%93'
    '%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%97%D0%BE%D0%BB%D1%8C%D'
    '1%82%D0%B'
    '0%D1%83-%D0%A4%D0%B0%D0%BB%D0%BB%D0%B8%D0%BD%D0%B3%D0%B1'
    '%D0%BE%D'
    '1%81%D1%82%D0%B5%D0%BB%D1%8C_(%D1%80%D0%B0%D0%B9%D0%BE%D'
    '0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9E%D0%BB%D1%8C%D0%B4%D'
    '0%B5%D0%'
    'BD%D0%B1%D1%83%D1%80%D0%B3',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%80%D0%B4%D'
    '0%B5%D0%'
    'BD_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D'
    '0%B3%D0%'
    'BE%D1%80%D0%B8%D1%8F:%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8'
    'B_%D0%9D%'
    'D0%B8%D0%B6%D0%BD%D0%B5%D0%B9_%D0%A1%D0%B0%D0%BA%D1%81%D'
    '0%BE%D0%'
    'BD%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D'
    '0%BF%D0%'
    'B5%D0%B4%D0%B8%D1%8F:%D0%A1%D0%BF%D1%80%D0%B0%D0%B2%D0%B'
    'A%D0%B0',
    'https://ru.wikipedia.org/wiki/%D0%93%D0%B0%D0%BD%D0%BD%D'
    '0%BE%D0%B'
    '2%D0%B5%D1%80_(%D1%80%D0%B5%D0%B3%D0%B8%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B'
    '5%D0%B'
    '1%D0%BD%D0%B0%D1%8F:%D0%A1%D1%81%D1%8B%D0%BB%D0%BA%D0%B8_%'
    'D1%81%D'
    '1%8E%D0%B4%D0%B0/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5_(%D1%80%D0'
    '%B0%D0%'
    'B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B9%D0%BB:'
    'Wappen_Lan'
    'dkreis_Peine.svg',
    'https://ru.wikipedia.org/wiki/Википедия:Контакты',
    'https://ru.wikipedia.org/wiki/%D0%93%D0%BE%D1%81%D0%BB%D0%'
    'B0%D1%80'
    '_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9D%D0%B8%D0%BD%D0%B1%D1'
    '%83%D1%80'
    '%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%98%D0%BB%D1%8C%D1%86%D0'
    '%B5%D0%BD'
    '_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%BE%D0%BB%D1%8C%D1'
    '%84%D0%B5'
    '%D0%BD%D0%B1%D1%8E%D1%82%D1%82%D0%B5%D0%BB%D1%8C_(%D1%80%'
    'D0%B0%D0%B'
    '9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D1%80%D0%B0%D'
    '0%B2%D0%BA'
    '%D0%B0:%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BB%D1%8C%D0'
    '%BC%D0%B'
    '5%D0%BD%D1%85%D0%BE%D1%80%D1%81%D1%82',
    'https://ru.wikipedia.org/wiki/%D0%A0%D0%BE%D1%82%D0%B5%'
    'D0%BD%D0%B1'
    '%D1%83%D1%80%D0%B3-%D0%BD%D0%B0-%D0%92%D1%8E%D0%BC%D0%BC'
    '%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D'
    '0%B5%D0%B1'
    '%D0%BD%D0%B0%D1%8F:%D0%A1%D0%B2%D0%B5%D0%B6%D0%B8%D0%B5_'
    '%D0%BF%D1%'
    '80%D0%B0%D0%B2%D0%BA%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%'
    'D0%B5%D0%B1'
    '%D0%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D1%91_%D0%BE%D0%B1%D1%81'
    '%D1%83%D0%'
    'B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%B0%D0%BC%D0%B5%'
    'D0%BB%D1%8C'
    '%D0%BD-%D0%9F%D0%B8%D1%80%D0%BC%D0%BE%D0%BD%D1%82_(%D1'
    '%80%D0%B0%D0%'
    'B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BE%D1%86%D0%B8%'
    'D0%B0%D0%BB-%'
    'D0%B4%D0%B5%D0%BC%D0%BE%D0%BA%D1%80%D0%B0%D1%82%D0%B8%'
    'D1%87%D0%B5%D1'
    '%81%D0%BA%D0%B0%D1%8F_%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D'
    '1%8F_%D0%93%D0'
    '%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%98%D0%BB%D1%8C%D0%B7'
    '%D0%B5%D0%B4%D0'
    '%B5',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D1%82%D1%82'
    '%D0%BC%D1%83%D0%'
    'BD%D0%B4_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D0%BB%D1%8'
    'C%D1%86%D0%BC%D0'
    '%B8%D0%BD%D0%B4%D0%B5%D0%BD_(%D1%80%D0%B0%D0%B9%D0%BE'
    '%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9A%D0%BB%D0%BE%D0%B'
    'F%D0%BF%D0%B5%D0%'
    'BD%D0%B1%D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9B%D0%B5%D1%80_(%D1'
    '%80%D0%B0%D0%B9%D'
    '0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9B%D0%B0%D0%BD%D0%B'
    '4%D1%80%D0%B0%D1'
    '%82',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B'
    '6%D0%B5%'
    'D0%B1%D0'
    '%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D0%B9_%D0%B2%D0%BA%D0%BB'
    '%D0%B0%D0%B4',
    'https://ru.wikipedia.org/wiki/%D0%90%D1%83%D1%80%D0%B'
    '8%D1%85_(%D1%80%'
    'D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%B0%D1%80%D0%B'
    '1%D1%83%D1%80%D0'
    '%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D1%82%D0%B'
    '5%D1%80%D0%BE%D0%'
    'B4%D0%B5_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A6%D0%B5%D0%BB%D0%B'
    'B%D0%B5_(%D1%80%D'
    '0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D1%85%D1%8'
    '2%D0%B0_(%D1%80%D'
    '0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%B5%D0%BB%D1%8'
    'C%D0%BC%D1%88%D1%8'
    '2%D0%B5%D0%B4%D1%82_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D1%8D%D0%B'
    'D%D1%85%D0%B0%D0%BC'
    '%D0%B5%D0%BB%D1%8C%D0%BD',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BB%D1%8'
    'C%D0%B3%D0%B5%D0%BB'
    '%D1%8C%D0%BC%D1%81%D1%85%D0%B0%D1%84%D0%B5%D0%BD',
    'https://ru.wikipedia.org/wiki/%D0%9E%D0%BB%D1%8C%D0%B'
    '4%D0%B5%D0%BD%D0%B1%'
    'D1%83%D1%80%D0%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%B'
    'D%D0%B5_(%D1%80%D0%B'
    '0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%B'
    '0%D0%B1%D1%80%D1%8E%D'
    '0%BA_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B'
    '8%D0%BF%D0%B'
    '5%D0%B4%D'
    '0%B8%D1%8F:%D0%A1%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%8'
    '1%D1%82%D0%B'
    '2%D0%BE',
    'https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%BB%D1%'
    '8C%D1%86%D0%'
    'B3%D0%B8%D'
    '1%82%D1%82%D0%B5%D1%80',
    'https://ru.wikipedia.org/wiki/%D0%92%D0%BE%D0%BB%D1%'
    '8C%D1%84%D1%'
    '81%D0%B1%D1%'
    '83%D1%80%D0%B3',
    'https://ru.wikipedia.org/wiki/%D0%A8%D0%B0%D1%83%D'
    '0%BC%D0%B1%D1'
    '%83%D1%80%D0'
    '%B3_(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)',
    'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%'
    'B6%D0%B5%D0%'
    'B1%D0%BD%D0'
    '%B0%D1%8F:%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80'
    '%D0%B8%D0%B8',
    'https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0'
    '%B0%D0%B1%D1%'
    '80%D1%8E%D'
    '0%BA'}


class RobotParserTests(unittest.TestCase):
    def test_robot_parser_can_not_fetch(self):
        robot_parser = main.RobotParser(domains=['en.wikipedia.org'])

        fetch_result = robot_parser.can_fetch("/wiki/Wikipedia:"
                                              "Articles_for_deletion")
        self.assertEqual(fetch_result, False)

    def test_robot_parser_can_fetch_true(self):
        robot_parser = main.RobotParser(domains=['ru.wikipedia.org'])
        fetch_result = robot_parser.can_fetch("https://ru.wikipedia.org"
                                              "/wiki/%D0%9C%D1%91%D1%80%"
                                              "D1%82%D0%B2%D1%8B%D0%B5_"
                                              "%D0%B4%D1%83%D1%88%D0%B8")
        self.assertEqual(fetch_result, True)


class CheckValidUrlTests(unittest.TestCase):
    def test_unvalid_url_test(self):
        self.assertEqual(main.valid_url("://ru.wikipedia.org/"
                                        "%D0%9D%D0%B0%D1%86%D0%B8%D0%BE%D"
                                        "0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1"
                                        "%8B%D0%B9"
                                        "%D0%BC%D1%83%D0%B7%D0%B5%D0%B9_%D"
                                        "0%A2%D0%B5-%D0%9F%D0%B0%D0%BF%D0"
                                        "%B0-%D0%A"
                                        "2%D0%BE%D0%BD%D0%B3%D0%B0%D1%80%D"
                                        "0%B5%D0%B2%D0%B0"), False)

    def test_valid_url(self):
        self.assertEqual(main.valid_url("https://www.kinopo"
                                        "isk.ru/series/1227803/"), True)


class WebsiteLinksTests(unittest.TestCase):
    def test_find_all_links(self):
        real_links = main.website_links(
            "https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%"
            "BD%D0%B5_(%D"
            "1%80%D0%B0%D0%B9%D0%BE%D0%BD)",
            ["ru.wikipedia.org"], main.RobotParser(domains=['ru.wikipedia.org']))
        self.assertSetEqual(correct_links, real_links)


class SafeFileTests(unittest.TestCase):
    def test_safe_when_offset_is_none(self):
        sub_title = None
        try:
            url = "https://ru.wikipedia.org/wiki/%D0%92%D0%B" \
                  "8%D0%B2%D0%B5%D1%80%D0%BD%D0%B0"
            content = requests.get(url).content
            soup = BeautifulSoup(content, "html.parser")
            title = soup.title.string
            html_title = title + '.html'
            sub_title = re.sub(r'[:></"\\|*?]', "_", html_title)
            if os.path.exists(sub_title):
                os.remove(sub_title)
            main.safe_html(url, None)
            self.assertEqual(os.path.exists(sub_title), True)
        finally:
            os.remove(sub_title)

    def test_safe_when_offset_is_not_none(self):
        try:
            url = "https://docs.python.org/3/"
            content = requests.get(url).content
            soup = BeautifulSoup(content, "html.parser")
            title = soup.title.string
            html_title = title + '.html'
            sub_title = re.sub(r'[:></"\\|*?]', "_", html_title)
            if os.path.exists(sub_title):
                os.remove(sub_title)
            main.safe_html(url, 1000)
            self.assertEqual(os.path.exists(sub_title), True)
            self.assertEqual(17458, os.stat(sub_title).st_size)
        finally:
            print()
            # os.remove(sub_title)


class SafeMultiThreadTests(unittest.TestCase):
    @staticmethod
    def test_safe():
        url = "https://ru.wikipedia.org/wiki/%D0%" \
              "92%D0%B8%D0%B2%D0%B5%D1%80%D0%BD%D0%B0"
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string
        html_title = title + '.html'
        sub_title = re.sub(r'[:></"\\|*?]', "_", html_title)
        if os.path.exists(sub_title):
            os.remove(sub_title)
        title = unquote(url).split('/')
        title = "MT" + title[-1] + ".html"
        main.safe_multi_thread(url, title)
        # self.assertEqual(os.path.exists(title), True)
        os.remove(title)


class RUpdateHtmlFilesTests(unittest.TestCase):
    def test_update_html_files(self):
        title = "Бурбоны — Википедия.html"
        with open(title, "w+") as f:
            f.write("\"dateModified\":\"2021-05-04T11:03:15Z\"" + " " + "<link rel=\"canonical\" href=\"https://"
                                                                        "ru.wikipedia.org/wiki/%D0%91%D1%83%D1%80"
                                                                        "%D0%B1%D0%BE%D0%BD%D1%8B\"/>")
        file_length = os.stat(title).st_size
        main.update_html_files()
        file_length2 = os.stat(title).st_size
        os.remove(title)
        self.assertNotEqual(file_length, file_length2)


class CraulerTests(unittest.TestCase):
    def test_crauler_general_functionality(self):
        start_page = "https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)"
        main.q_type = "tm"
        main.start_page = start_page
        main.robot_parser = main.RobotParser(domains=['ru.wikipedia.org'])
        main.crauler(start_page, None)
        correct_queue = Queue()
        correct_visited_set = set()
        correct_visited_set.add(start_page)
        for link in correct_links:
            if link not in correct_visited_set:
                correct_queue.put(link)
        os.remove("Пайне(район).html")
        print(correct_visited_set)
        self.assertSetEqual(main.visited, correct_visited_set)
        current = []
        correct = []
        while main.url_queue.qsize() > 0 and correct_queue.qsize() > 0:
            current.append(main.url_queue.get())
            correct.append(correct_queue.get())
        current.sort()
        correct.sort()
        self.assertListEqual(current, correct)


class ConstructorRobotParser(unittest.TestCase):
    def test_EmptyString(self):
        self.assertRaises(TypeError, main.RobotParser, None, ["abc"])


class ConstructorPerpetual_timer(unittest.TestCase):
    def test_EmptyString(self):
        self.assertRaises(TypeError, main.perpetual_timer, None, main.crauler("https://ru."
                                                                              "wikipedia.org/wiki/"
                                                                              "%D0%9F%D0%B0%D0%B9%D0%BD%D"
                                                                              "0%B5(%D1%80%D0%B0%D0%B9%D0%BE%D"
                                                                              "0%BD)", None))


class InitialTests(unittest.TestCase):
    def test_initial_behaviour(self):
        main.initial("tm", ['ru.wikipedia.org'],
                     "https://ru.wikipedia.org/wiki/"
                     "%D0%9F%D0%B0%D0%B9%D0%BD%D0%B5"
                     "(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)")
        self.assertEqual(main.domains, ['ru.wikipedia.org'])
        self.assertEqual(main.start_page, "https://ru.wikipedia.org/wiki/""%D0%9F%D0%B0%D0%B9"
                                          "%D0%BD%D0%B5""(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)")

        self.assertEqual(main.q_type, "tm")
        self.assertEqual(main.url_queue.qsize(), 1)
        self.assertEqual(main.url_queue.get(), "https://ru.wikipedia.org/wiki/""%D0%9F%D0%B0%"
                                               "D0%B9%D0%BD%D0%B5""(%D1%80%D0%B0%D0%B9%D0%BE%D0%BD)")


if __name__ == '__main__':
    unittest.main()
