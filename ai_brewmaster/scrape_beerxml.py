import requests
import time
import re

#
# This file scrapes brewersfriend for recipes and adds them to a single text
# file for use with https://github.com/hunkim/word-rnn-tensorflow.git
#
# Usage: %> python scrape_beerxml.py
#

# Index range for brewersfiend crawling
start_index = 1633
end_index   = 16000

tot_count = 1

# Output file location
output_file = open("data/beerxml_recipes.txt", "w")

for index in range(start_index, end_index):
    url = 'https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/'+str(index)
    page = requests.get(url)
    page_text = page.text
    if (page):
        # only use pages that successfully found a recipe
        if (re.search("<RECIPE>", page.text)):
            print "Downloaded BeerXML at index: " + str(index) + ", total: " + str(tot_count) + "\n"
            # add a space around <> tags so that they are split into independent words in train.py
            page_text = re.sub("<", " <", page_text)
            page_text = re.sub(">", "> ", page_text)
            output_file.write(page_text.encode('ascii', 'ignore'))
            tot_count = tot_count + 1;

    # only query website once per second
    time.sleep(1)

output_file.close()
