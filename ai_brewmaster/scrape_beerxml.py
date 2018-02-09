import requests
import time
import re

#
# This file scrapes brewersfriend for recipes and adds them to a single text
# file for use with https://github.com/hunkim/word-rnn-tensorflow.git
#
# Usage: %> python scrape_beerxml.py
#

# Index range for brewersfiend crawling, change file every 10000 indexes
start_index = 110000
end_index   = 120000

tot_count = 1

while (True):
    # Output file location
    output_file = open("data/beerxml_recipes_"+str(start_index)+"_"+str(end_index)+".txt", "w")

    for index in range(start_index, end_index):
        url = 'https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/'+str(index)
        try:
            page = requests.get(url)
        except:
            print "Exeption thrown"
            time.sleep(10)
            continue
        page_text = page.text
        if (page):
            # only use pages that successfully found a recipe
            if (re.search("<RECIPE>", page.text)):
                print "Downloaded BeerXML at index: " + str(index) + ", total: " + str(tot_count) + "\n"
                # add a space around <> tags so that they are split into independent words in train.py
                page_text = re.sub("<", " <", page_text)
                page_text = re.sub(">", "> ", page_text)
                # remove special character
                page_text = re.sub("&#13;", "\n", page_text)
                # move style to first block after recipe
                matchObj = re.match( r'(.*)<RECIPE>(.*)<STYLE>(.*)</STYLE>(.*)', page_text, re.S)
                page_text = matchObj.group(1) + "<RECIPE> \n   <STYLE>" + matchObj.group(3) + "</STYLE>" + matchObj.group(2) + matchObj.group(4)

                output_file.write(page_text.encode('utf-8', 'ignore'))
                tot_count = tot_count + 1;

        # only query website once per 2 seconds
        time.sleep(2)

    output_file.close()

    # update start & end indexes
    start_index = start_index + 10000
    end_index   = end_index + 10000
