import re
import inflect
from charlist_scraper import CharacterListScraper

WIKI_PREFIX = "https://wiki.southpark.cc.com"
inflect_engine = inflect.engine()


class CharacterPageScraper:

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
        node_map[self.simple_format(id)][7] = full_name
        properties = []

        for line in lines:
            mode = self.determine_parse_mode(mode, line)

            if mode == "sections":
                last_rel = self.extract_relationships_from_sections(id, line, properties, last_rel, node_map)

            if mode == "info-box":
                last_rel = self.extract_relationships_from_info_box(id, line, properties, last_rel, node_map)

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

                if relationship == "HAS_AGE":
                    node_map[self.simple_format(id)][5] = other_name
                    return
                elif relationship == "HAS_GENDER":
                    node_map[self.simple_format(id)][6] = other_name
                    return
                elif relationship == "HAS_FULL_NAME":
                    return
                elif relationship == "HAS_HAIR_COLOR":
                    node_map[self.simple_format(id)][8] = other_name
                    return
                elif self.simple_format(other_node_id) != "" and relationship != "":
                    properties.append([self.simple_format(id), relationship, self.simple_format(other_node_id)])

                # if we already know the other node:
                #   We add a node label based on the name of the relationship
                if relationship is None:
                    continue

                new_other_node_label = relationship[3:].title().replace("_", "")
                if other_node_id in node_map:
                    other_node_existing_labels = node_map[other_node_id][9].split(";")
                    if new_other_node_label not in other_node_existing_labels:
                        node_map[other_node_id][9] += ";" + new_other_node_label

                if other_node_id != "" and self.simple_format(other_node_id) not in node_map:
                    node_map[self.simple_format(other_node_id)] = [self.simple_format(other_node_id), other_name,
                                                                   other_wiki_url, "", "", "", "", "", "",
                                                                   "Entity;" + new_other_node_label]
        return relationship

    def extract_relationships_from_sections(self, id, line, properties, relationship, node_map):

        if "\"mw-headline\"" in line:
            split_line = re.split('[><"]', line)
            relationship = self.convert_to_rel_syntax(split_line[8])
            relationship_words = relationship.split("_")
            if inflect_engine.singular_noun(relationship_words[-1]):
                relationship_words[-1] = inflect.engine.singular_noun(inflect_engine, relationship_words[-1])
                relationship = "_".join(relationship_words)

        if "class=\"character\"" in line:
            split_line = re.split('[><]', line)

            # Determine name for other node
            other_name = split_line[len(split_line) - 5]
            other_name_as_id = self.simple_format(other_name.replace(" ", "_"))

            # Determine wiki URL for other node
            other_wiki_url = line.split("href=\"")[1].split("\"")[0]
            if WIKI_PREFIX not in other_wiki_url:
                other_wiki_url = WIKI_PREFIX + other_wiki_url
            if other_wiki_url == "":
                other_wiki_url = other_name.replace(" ", "_")

            if relationship == "HAS_FAMILY":
                other_name_as_id = other_wiki_url.split("/")[-1]

            # Determine image for other node
            other_image_url = line.split("src=\"")[1].split("\"")[0]

            # Up the resolution of the images
            other_image_url = other_image_url.replace("?height=98", "?height=250")

            if other_name_as_id != "":
                properties.append([self.simple_format(id), relationship, other_name_as_id])

            new_other_node_label = relationship[3:].title().replace("_", "")
            # if the last word is plural, make it singular
            if inflect_engine.singular_noun(relationship.split("_")[-1]):
                try:
                    new_other_node_label = inflect_engine.engine.singular_noun(new_other_node_label)
                except AttributeError:
                    print("Unable to convert to singular:", new_other_node_label)

            # if we already know the other node:
            #   when we have a previous node entry already without a picture, we add the picture.
            #   We add a node label based on the name of the relationship
            if other_name_as_id in node_map:
                if node_map[other_name_as_id][3] == "":
                    node_map[other_name_as_id][3] = other_image_url

                # Other node should get label (relname).title().replace(" ","")
                other_node_existing_labels = node_map[other_name_as_id][9].split(";")
                if new_other_node_label not in other_node_existing_labels:
                    node_map[other_name_as_id][9] += ";" + new_other_node_label

                # If we don't know the other node:
            if other_name_as_id != "" and other_name_as_id not in node_map:
                node_map[other_name_as_id] = [other_name_as_id, other_name, other_wiki_url, other_image_url, "", "", "",
                                              "", "", "Entity;" + new_other_node_label]
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
        string = string.replace("%27", "").replace("%22", "").replace("-", "_").replace("/", "_SLASH_")
        return re.sub('[\W]+', '', string)
