import re

import requests
from bs4 import BeautifulSoup

WIKI_PREFIX = "https://wiki.southpark.cc.com"


class CharacterListScraper:

    @staticmethod
    def get_and_parse_url(url):
        html_doc = requests.get(url).text
        return BeautifulSoup(html_doc, 'html.parser')

    def parse_characters_list_page(self, url):
        node_map = {}
        soup = self.get_and_parse_url(url)
        wiki_body = soup.find_all('div', attrs={"class": "wiki-body"})

        current_category = ""
        current_category_id = ""

        for line in str(wiki_body).split("\n"):
            # If the current line represents a new category, store this info for later use.
            if self.is_category(line):
                split_line = re.split('[><"]', line)
                current_category_id = split_line[6].replace("_", "")
                current_category = split_line[8]
                continue

            # If the current line represents a character entry, save the info.
            if self.is_character(line):
                split_line = re.split('[><"]', line)
                if "/wiki/" in split_line[6]:
                    wiki_url = WIKI_PREFIX + split_line[6]
                else:
                    wiki_url = ""
                image_url = split_line[10]
                name = split_line[14]
                # If the node has a unique wiki page, we use the suffix of the URL.
                node_id = wiki_url[35:len(wiki_url)]
                if node_id == "":
                    # If is does not, just use the name and replace all spaces by underscores.
                    node_id = name.replace(" ", "_")

                # Add the entry to our list.
                if node_id not in node_map:
                    node_map[self.simple_format(node_id)] = [self.simple_format(node_id), name, wiki_url, image_url,
                                                             current_category,
                                                             self.simple_format(current_category_id) + ";Character"]

        return node_map

    @staticmethod
    def is_category(line):
        return "class=\"mw-headline\"" in line

    @staticmethod
    def is_character(line):
        return "class=\"character\"" in line

    @staticmethod
    def simple_format(string):
        string = string.replace("%27","").replace("%22","").replace("-","_")
        return re.sub('[\W]+', '', string)