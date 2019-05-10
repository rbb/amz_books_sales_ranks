
from bs4 import BeautifulSoup
import requests
import re
import csv
import sys
import time
import random
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('--csv_name', action='store', default="slipstream.csv",
        help='output file: %(default)s')
parser.add_argument('--booted_name', action='store', default="booted.html",
        help='File for storing the booted HTML message from Amazon: %(default)s')
parser.add_argument('--min_sec_sleep', metavar='N', default=5.0,
        help=' %(default)s')
parser.add_argument('--inter_book_sleep', metavar='N', default=30.0,
        help='Max sleep between book lookups: %(default)s')
parser.add_argument('--inter_asin_sleep', metavar='N', default=15.0,
        help='Max sleep between ASIN lookups: %(default)s')
parser.add_argument('--max_book_links', metavar='N', default=4,
        help='Max number of book links to follow %(default)s')
parser.add_argument('--max_fails', metavar='N', default=5,
        help='Max number of failed http requests: %(default)s')
parser.add_argument('-v', '--verbose', dest='verbose', action='store', default=0,
        type=int, metavar = 'N',
        help='Verbosity level. Anything other than 0 for debug info.')
parser.add_argument('-V', '--verbose_on', dest='verbose_on', action='store_true',
        default=False,
        help='Set Verbosity level N = 1.')

args = parser.parse_args()

sec_sleep = args.min_sec_sleep

#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:63.0) Gecko/20100101 Firefox/63.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; http://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0'},
           {'User-Agent': 'Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)'},
           {'User-Agent': 'Chrome/54.0.2840.71 Safari/537.36'} ]
#           {'User-Agent': 'AppleWebKit/537.36 (KHTML, like Gecko)'},
N_headers = len(headers)

def save_soup_cont(text, name=args.booted_name, mode = 'w+'):
    print("Saving " +name)
    f = open(name, mode)
    f.write(text)
    f.close()


def random_sleep(maxN, minN=args.min_sec_sleep):
    s = float(random.randrange(minN, maxN))
    print("random sleeping " +str(s) +" seconds")
    time.sleep(s)

class amzCheck():
    def __init__ (self, max_fails=args.max_fails):
        self.n_fails = 0
        self.max_fails = max_fails

    def get_amz_img_link(self, soup_var, nh):
        for link in soup_var.findAll('link', href=True):
            print( link )
            url = link.get('href')
            r = requests.get(url, headers=headers[nh])
            return r

    def check_booted(self, soup_var, nh):
        BOOTED_STR = "To discuss automated access to Amazon data please contact api-services-support@amazon.com."
        if BOOTED_STR in str(soup_var.contents):
            self.n_fails += 1
            print("------------------- Got BOOTED by Amazon. ---------------------------")
            print("FAILED with nh = " +str(nh) +", n_fails = " +str(self.n_fails))
            save_soup_cont(str(soup_var.contents))
            if self.n_fails <= self.max_fails:
                self.get_amz_img_link(soup_var, nh)
            return True

        self.n_fails = 0
        return False


    def limit(self):
        if self.n_fails >= self.max_fails:
            return True
        return False

def process_book_list():
    nh = 0
    amz_check = amzCheck()

    # Book list from:https://web.archive.org/web/20100124072420/http://home.roadrunner.com/~lperson1/slip.html
    with open('slipstream_sci_fi.txt', 'r') as f:
        n_lines = 0
        for line in f:
            n_lines += 1
            book = line.strip()

            # Check if we've already processed this book
            csvf = open(args.csv_name, 'r')
            #print( "checking: " +book )
            if book in open(args.csv_name, 'r').read():
                #print('skipping: ' +book)
                continue

            print("--------------------------------------------------------")
            print("nh= " +str(nh) +'   processing ' +book)
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
            
            if amz_check.check_booted(soup, nh):
                if amz_check.limit():
                    break
                else:
                    continue

            sales_ranks = []
            n_book_links = 1
            links = soup.findAll('a', attrs={'href': re.compile("^\/.*\/dp\/")})
            if not links:
                print("WARNING: no links in request. Skipping to next book")
                continue

            for link in links:
                book_url = link.get('href')
                #print( "book_url: " +book_url )
                if link.string:
                    #print( "link text: " +link.string.strip() )
                    m = re.search( '\/dp\/.*\/', book_url)
                    if m:
                        dp_str = m.group(0)
                        dp = dp_str[4:-1]
                        #print( "dp: " +dp)

                        if 'Paperback' in link.string or 'Hardback' in link.string or 'Kindle' in link.string:
                            random_sleep(args.inter_asin_sleep)
                            book_type = link.string.strip()
                            print( "fetching " +book_type +" book_url: " +book_url )
                            #print( "book type: " +book_type)
                            sales_rank = sys.maxsize
                            book_r = requests.get('https://www.amazon.com' +book_url, headers=headers[nh])
                            book_soup = BeautifulSoup(book_r.content, "lxml")
                            if not amz_check.check_booted(book_soup, nh):
                                sr = book_soup.find(id='SalesRank')
                                if sr:
                                    srm = re.search( '\#[\d,]* ', sr.text)
                                    if srm:
                                        srm_str = srm.group(0)

                                        # Trim the leading '#' character and the trailing space. Drop ','
                                        sales_rank = srm_str[1:].strip().replace(',', '')

                                        #print( "Sales Rank: " +sales_rank)
                                        print( ", ".join(['nh='+str(nh), book_type, 'ASIN= '+dp, 'SR= '+sales_rank]) )
                                else:
                                    print("WARINING: Could not find Sales Rank")
                                    fname = str(dp) +"-" +str(n_book_links) +".html"
                                    save_soup_cont(str(book_soup.contents), name=fname)

                            sales_ranks.append( int(sales_rank) )

                            n_book_links += 1
                            if n_book_links > args.max_book_links:
                                print("Stopping at " +str(args.max_book_links) +" book links")
                                # Only look at the top 5 links
                                break
                            if amz_check.limit():
                                break
            if sales_ranks:
                book_rank = min(sales_ranks)
                print( "Top Book Sales Rank: " +str(book_rank))
                sec_sleep = args.inter_book_sleep

                csvf = open(args.csv_name, 'a+')
                csv_writer = csv.writer(csvf, lineterminator='\n')
                csv_writer.writerow( [book, str(book_rank)] )
                csvf.close()
            else:
                book_rank = sys.maxsize
                sec_sleep = sec_sleep * 2

            if amz_check.limit():
                break



            # Rotate user agent, to prevent getting booted
            #nh += 1
            #if nh >= N_headers:
            #    nh = 0
            nh = random.randrange(0, N_headers-1)

            random_sleep(sec_sleep)  # Don't hammer Amazon, so we don't get booted.
            print("")
    if n_lines >= 329:
        return True
    return False

book_list_complete = False
while not book_list_complete:
    book_list_complete = process_book_list()
    if not book_list_complete:
        print("")
        print("")
        print("Got a lot of Amazon boots. Pausing for a bit")
        random_sleep(1200, 120)  # Don't hammer Amazon, so we don't get booted.
