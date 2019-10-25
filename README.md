## South Park Wiki Scraper
Scrapes the South Park Wiki and converts it into a format acceptable by Neo4j 3.5.
Accompanying blog post for this code can be found on my website.
### Dependencies
- Python 3.7 or later
- Inflect Engine (`pip install inflect`)
- BeautifulSoup4 HTML Parser (`pip install beautifulsoup4`)

### How to run
1. Run `scraper.py` using Python 3.7.
2. Resulting output is written to the `/output/` folder. This may take about 15 minutes. 
3. Import the nodes and relationships into Neo4j: \
    `./bin/neo4j-admin import --nodes nodes.csv --relationships edges.csv`
4. You're done!
