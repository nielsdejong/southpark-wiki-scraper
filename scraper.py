import copy
import csv
from character_page_scraper import CharacterPageScraper
from charlist_scraper import CharacterListScraper

charlist_url = 'https://wiki.southpark.cc.com/wiki/List_of_Characters'


def main():
    character_list_scraper = CharacterListScraper()
    single_page_scraper = CharacterPageScraper()

    node_map = character_list_scraper.parse_characters_list_page(charlist_url)

    nodes_csv_header = ["character_id:ID", "name", "wiki_url", "image_url", "group_name", ":LABEL"]
    relationships_csv_header = [":START_ID", ":TYPE", ":END_ID"]

    write_output('edges.csv', None, header=relationships_csv_header, mode="w")

    initial_node_map = copy.copy(node_map)
    for i, row in enumerate(initial_node_map.values()):
        node_id = row[0]
        wiki_url = row[2]
        print(i, node_id, wiki_url)

        # URL's may be misformed, so we skip these cases.
        if not wiki_url.startswith("http"):
            continue
        single_page_data = single_page_scraper.parse_character_page(node_id, wiki_url, node_map)
        write_output('edges.csv', single_page_data, mode="a")

    write_output('nodes.csv', node_map.values(), header=nodes_csv_header, mode="w")


def write_output(path, data, header=None, mode='w'):
    with open(path, mode=mode) as output_file:
        nodes_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                  lineterminator='\n')
        if header is not None:
            nodes_writer.writerow(header)
        if data is not None:
            for row in data:
                nodes_writer.writerow(row)


if __name__ == '__main__':
    main()
