
from bs4 import BeautifulSoup
import requests
import re
import csv
import sys
import time


#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0'},
           {'User-Agent': 'Chrome/54.0.2840.71 Safari/537.36'} ]
#           {'User-Agent': 'AppleWebKit/537.36 (KHTML, like Gecko)'},
N_headers = len(headers)
nh = 0

csv_name = 'slipstream.csv'
# Open the output file
#csvf = open('slipstream.csv', 'w')
#csv_writer = csv.writer(csvf)


# Book list from:https://web.archive.org/web/20100124072420/http://home.roadrunner.com/~lperson1/slip.html 
with open('slipstream_sci_fi.txt', 'r') as f:
    for line in f:
        book = line.strip()

        # Check if we've already processed this book
        csvf = open(csv_name, 'r')
        have_book = False
        print( "checking: " +book )
        row = True
        while csvf and row and not have_book:
            row = csvf.readline()
            #print('row: ' +str(row.strip()))
            if book in row:
                print('skipping: ' +book)
                have_book = True
                break
        time.sleep(0.1)
        if have_book:
            continue

        print(str(nh) +' processing ' +book)
        line = line.replace(':', '').strip()
        line = line.replace(',', ' ')
        line = line.replace("'s", 's')
        line = line.replace('etc.', '')
        #print( line.split() )

        terms = '+'.join(line.split())
        #print(terms)

        url="https://www.amazon.com/s?k=" +terms +"&i=stripbooks"
        print(url)
        r = requests.get(url, headers=headers[nh])
        soup = BeautifulSoup(r.content, "lxml")
        if 'automated access to Amazon data please contact' in soup.contents:
            print("Got booted by Amazon. Bye")
            sys.exit()

        sales_ranks = []
        n_book_links = 0
        for link in soup.findAll('a', attrs={'href': re.compile("^\/.*\/dp\/")}):
            time.sleep(0.5)  # Don't hammer Amazon, so we don't get booted.
            book_url = link.get('href')
            print( "book_url: " +book_url )
            if link.string:
                print( "link text: " +link.string.strip() )
                m = re.search( '\/dp\/.*\/', book_url) 
                if m:
                    dp_str = m.group(0)
                    dp = dp_str[4:-1]
                    print( "dp: " +dp)

                if 'Paperback' in link.string or 'Hardback' in link.string or 'Kindle' in link.string:
                    book_type = link.string.strip()
                    #print( "book type: " +book_type)
                    book_r = requests.get('https://www.amazon.com' +book_url, headers=headers[nh])
                    book_soup = BeautifulSoup(book_r.content, "lxml")
                    sr = book_soup.find(id='SalesRank')
                    if sr:
                        srm = re.search( '\#[\d,]* ', sr.text)
                        if srm:
                            srm_str = srm.group(0)

                            # Trim the leading '#' character and the trailing space. Drop ',' 
                            sales_rank = srm_str[1:].strip().replace(',', '') 

                            #print( "Sales Rank: " +sales_rank)
                            print( ", ".join([str(nh), book_type, dp, sales_rank]) )
                            sales_ranks.append( int(sales_rank) )

                    n_book_links += 1
                    if n_book_links > 5:
                        print("Stopping at 5 book links")
                        # Only look at the top 5 links
                        break
        if sales_ranks:
            book_rank = min(sales_ranks)
            print( "Top Book Sales Rank: " +str(book_rank))

            csvf = open(csv_name, 'a+')
            csv_writer = csv.writer(csvf)
            csv_writer.writerow( [book, str(book_rank)] )
            csvf.close()
        else:
            print("FAILED with nh = " +str(nh))
            book_rank = sys.maxsize
        

        # Rotate user agent, to prevent getting booted
        nh += 1
        if nh >= N_headers:
            nh = 0

        time.sleep(5.0)  # Don't hammer Amazon, so we don't get booted.
        print("")

