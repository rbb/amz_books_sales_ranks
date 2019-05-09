# Amazon Sales Rank

In reading some stuff about science fiction, I ran across a sub-genre called
"slipstream", that I had never heard of. So, I found a list of these books, but
where to start? Maybe look them up on Amazon, to see what has sold the best?

Enter, a Quick experiment: Look up the Amazon "Sales Rank" of some books with
python and BeautifulSoup.

# Basic Steps

After manually downloading the list of books and putting it into
`slipstream_sci_fi.txt`, I process the list with the following steps:

   * get rid of punctuation in the list. For each book in the list, put all the
     words into a list.
   * Create a RESTful URL based on the list of search terms
   * In the Amazon search results look for links that look like they have an 
     Amazon ASIN: `.../dp/XXXXXXXX/...`
   * Look for 'Paperback', 'Hardback', or 'Kindle' in the link text
   * Search for the Sales Rank
   * Output the results to a CSV file

# Warning
This is not the Amazon recommended way of doing things. They really want you to
sign up for a dev acount.

    > To discuss automated access to Amazon data please contact api-services-support@amazon.com.
    > For information about migrating to our APIs refer to our Marketplace APIs at
    > https://developer.amazonservices.com/ref=rm_c_sv, or our Product Advertising
    > API at https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html/ref=rm_c_ac
    > for advertising use cases.

* [Marketplace APIs](https://developer.amazonservices.com/ref=rm_c_sv)
* [Product Advertising API](https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html/ref=rm_c_ac)
