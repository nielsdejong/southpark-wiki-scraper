import copy
import csv
from character_page_scraper import CharacterPageScraper
from charlist_scraper import CharacterListScraper

charlist_url = 'https://wiki.southpark.cc.com/wiki/List_of_Characters'


def scrape_wiki(url):
    """
    Scrapes the South Park wiki in two steps:
    1. Collect a list of URLs for every character.
    2. For each URL (node), scrape the outgoing relationships (links).

    :param url: URL for the list of characters on the wiki.
    """

    # Get list of initial nodes (characters on list page)
    node_map = CharacterListScraper().parse_characters_list_page(url)

    # Write only the header to the edges.csv file. As new relationships are found we append this file.
    relationships_csv_header = [":START_ID", ":TYPE", ":END_ID"]
    write_output('output/edges.csv', None, header=relationships_csv_header, mode="w")

    # Go through characters, finding new relationships and nodes as we go.
    initial_node_map = copy.copy(node_map)
    single_page_scraper = CharacterPageScraper()

    for i, row in enumerate(initial_node_map.values()):
        print(i, node_id, wiki_url)

        node_id = row[0]
        wiki_url = row[2]

        # URL's may be misformed, so we skip these cases.
        if not wiki_url.startswith("http"):
            continue

        # Scrape the page
        single_page_data = single_page_scraper.parse_character_page(node_id, wiki_url, node_map)
        write_output('edges.csv', single_page_data, mode="a")

    # When all done, write the complete list of nodes (including newly discovered ones) to the file.
    nodes_csv_header = ["character_id:ID", "name", "wiki_url", "image_url", "group_name", "age", "gender", "full_name",
                        "hair_color", ":LABEL"]
    write_output('output/nodes.csv', node_map.values(), header=nodes_csv_header, mode="w")


def write_output(path, data, header=None, mode='w'):
    """
    Writes to an output file.
    :param path: path of the file.
    :param data: list of rows to write. Each row is a list of strings.
    :param header: the header row as a list of strings.
    :param mode: the write mode. ('w' for write, 'a' for append)
    :return:
    """
    with open(path, mode=mode) as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                            lineterminator='\n')
        if header is not None:
            writer.writerow(header)
        if data is not None:
            for row in data:
                writer.writerow(row)


if __name__ == '__main__':
    scrape_wiki(charlist_url)
