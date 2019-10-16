import re

from charlist_scraper import CharacterListScraper

WIKI_PREFIX = "https://wiki.southpark.cc.com"


class CharacterPageScraper:
    unique_reltypes = {}

    def parse_character_page(self, id, url, node_map):
        soup = CharacterListScraper.get_and_parse_url(url)

        info_box_header = soup.find('span', attrs={"class": "info-box-header"})
        wiki_body = soup.find('div', attrs={"class": "wiki-body"})
        if wiki_body is None or info_box_header is None:
            return
        full_name = info_box_header.getText()
        lines = str(wiki_body).split("\n")

        last_rel = ""
        mode = ""
        properties = [[self.simple_format(id), "FULL_NAME", full_name]]
        for line in lines:
            mode = self.determine_parse_mode(mode, line)

            if mode == "sections":
                last_rel = self.extract_relationships_from_sections(id, line, properties, last_rel, node_map)

            if mode == "info-box":
                last_rel = self.extract_relationships_from_info_box(id, line, properties, last_rel, node_map)

            if last_rel not in self.unique_reltypes:
                self.unique_reltypes[last_rel] = ""
                print(len(self.unique_reltypes), last_rel)
        return properties

    def extract_relationships_from_info_box(self, id, line, properties, relationship, node_map):
        if "<td class=\"key\">" in line:
            split_line = re.split('[><"]', line)
            relationship = self.convert_to_rel_syntax(split_line[4])

        elif "<td class=\"value\">" in line or "</td>" in line:
            preprocessed_line = line.replace("<td class=\"value\">", "").replace("</td>", "")
            current_values = re.split(', |; |: ', preprocessed_line)
            for other_name in current_values:
                other_wiki_url = ""
                current_value_split = re.split('[><]', other_name)

                if len(current_value_split) > 2:
                    other_name = current_value_split[2]
                    url = re.findall(r'href=\"(.+?)\"', current_value_split[1])
                    if len(url) > 0:
                        other_wiki_url = WIKI_PREFIX + url[0]

                if other_wiki_url == "":
                    other_wiki_url = other_name.replace(" ", "_")

                if "action=edit&amp;redlink=1" in other_wiki_url:
                    other_wiki_url = re.findall(r'title=(.+?)&amp;', other_wiki_url)[0]

                other_node_id = other_wiki_url[35:len(other_wiki_url)]
                if other_node_id == "":
                    # If is does not, just use the name and replace all spaces by underscores.
                    other_node_id = other_wiki_url.replace(" ", "_")

                if other_node_id != "":
                    properties.append([self.simple_format(id), relationship, self.simple_format(other_node_id)])

                # Don't save these as they don't have pretty pictures
                other_name_as_id = other_name.replace(" ", "_")
                if other_name_as_id != "" and self.simple_format(other_node_id) not in node_map:
                    node_map[self.simple_format(other_name_as_id)] = [self.simple_format(other_name_as_id), other_name,
                                                                other_wiki_url, "", "", ""]
        return relationship

    def extract_relationships_from_sections(self, id, line, properties, relationship, node_map):
        if "\"mw-headline\"" in line:
            split_line = re.split('[><"]', line)
            relationship = self.convert_to_rel_syntax(split_line[8])

        if "class=\"character\"" in line:
            split_line = re.split('[><]', line)
            other_wiki_url = line.split("href=\"")[1].split("\"")[0]
            if WIKI_PREFIX not in other_wiki_url:
                other_wiki_url = WIKI_PREFIX + other_wiki_url
            other_name = split_line[len(split_line) - 5]
            other_image_url = line.split("src=\"")[1].split("\"")[0]
            if other_wiki_url == "":
                other_wiki_url = other_name.replace(" ", "_")
            other_node_id = other_wiki_url[35:len(other_wiki_url)]
            # If the other node id is not a URL, just use the name and replace all spaces by underscores.
            if other_node_id == "":
                other_node_id = other_wiki_url.replace(" ", "_")
            properties.append([self.simple_format(id), relationship, self.simple_format(other_node_id)])
            other_name_as_id = self.simple_format(other_name.replace(" ", "_"))

            # Weird case - when we have a previous node entry already without a picture, we add the picture.
            if other_name_as_id in node_map and node_map[other_name_as_id][3] != "":
                node_map[other_name_as_id][3] = other_image_url

            if other_name_as_id != "" and self.simple_format(other_node_id) not in node_map:
                node_map[other_name_as_id] = [other_name_as_id, other_name, other_wiki_url, other_image_url, "", ""]
        return relationship

    def convert_to_rel_syntax(self, current_key):
        # HAS_CHARACTER_ART:_SCOTT_MALKINSON <-- is filtered out
        return "HAS_" + current_key.upper().replace(" ", "_").split(":")[0]

    def determine_parse_mode(self, mode, line):
        if "<div class=\"table\">" in line:
            mode = "info-box"
        if "</table>" in line:
            mode = ""
        if "class=\"mw-headline\"" in line:
            mode = "sections"
        return mode

    @staticmethod
    def simple_format(string):
        string = string.replace("%27","").replace("%22","").replace("-","_")
        return re.sub('[\W]+', '', string)
