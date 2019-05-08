
from bs4 import BeautifulSoup
import requests
import re
import csv


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}

csvf = open('slipstream.csv', 'w')
csv_writer = csv.writer(csvf)

n = 0

# Book list from:https://web.archive.org/web/20100124072420/http://home.roadrunner.com/~lperson1/slip.html 
with open('slipstream_sci_fi.txt', 'r') as f:
    for line in f:
        n += 1
        book = line.strip()
        print('processing ' +book)
        line = line.replace(':', '').strip()
        line = line.replace(',', ' ')
        line = line.replace('etc.', '')
        #print( line.split() )

        terms = '+'.join(line.split())
        #print(terms)

        url="https://www.amazon.com/s?k=" +terms +"&i=stripbooks"
        #print(url)
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "lxml")

        sales_ranks = []
        for link in soup.findAll('a', attrs={'href': re.compile("^\/.*\/dp\/")}):
            book_url = link.get('href')
            #print( "link: " +book_url )
            if link.string:
                #print( "link text: " +link.string.strip() )
                m = re.search( '\/dp\/.*\/', book_url) 
                if m:
                    dp_str = m.group(0)
                    dp = dp_str[4:-1]
                    #print( "dp: " +dp)

                if 'Paperback' in link.string or 'Hardback' in link.string or 'Kindle' in link.string:
                    book_type = link.string.strip()
                    #print( "book type: " +book_type)
                    book_r = requests.get('https://www.amazon.com' +book_url, headers=headers)
                    book_soup = BeautifulSoup(book_r.content, "lxml")
                    sr = book_soup.find(id='SalesRank')
                    if sr:
                        srm = re.search( '\#[\d,]* ', sr.text)
                        if srm:
                            srm_str = srm.group(0)

                            # Trim the leading '#' character and the trailing space. Drop ',' 
                            sales_rank = srm_str[1:].strip().replace(',', '') 

                            #print( "Sales Rank: " +sales_rank)
                            #print( ", ".join([book_type, dp, sales_rank]) )
                            sales_ranks.append( int(sales_rank) )
        book_rank = min(sales_ranks)                    
        print( "Top Book Sales Rank: " +str(book_rank))
        

        #csvf.write( ", ".join([book, str(book_rank)]) )
        csv_writer.writerow( [book, str(book_rank)] )
        csvf.flush()

        print("")

