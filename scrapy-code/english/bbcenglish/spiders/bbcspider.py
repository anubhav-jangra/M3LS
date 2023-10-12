import scrapy
from scrapy.crawler import CrawlerProcess  # To call within script

import pandas as pd
import numpy as np
import os

# hashlib for consistent hash valuess
import hashlib


#
#
# json_save = "./json_save"
# if not os.path.exists(json_save):
#     os.mkdir(json_save)

# save_name = json_save + str(nums_start) + '.json'


def hashit(s):
    '''This function takes a string as its argument and returns its hash value based on sha1 algorithm'''
    x = hashlib.sha1()
    x.update(s.encode())
    return x.hexdigest()

def domain_split(s):
    ''' This function is used for web urls which are similar to modern BBC hindi news article urls, it obtains the domain  name from the URL'''
    for i, item in enumerate(s):
        if item == "/" or item == "-":
            return s[0:i]


extra_links = [] # array for storing extra links

class bbcSpider(scrapy.Spider):
    '''This is our original spider for bbchindi scraping'''

    # Defining the name of the spider
    name = 'bbcenglish'

    # This is where we enter all our url's for scraping

    data = pd.read_csv('extractedlinks2.csv', header= None)[0]
    valid_ind = (data.str.contains('bbc')) & (data.str.startswith('http'))
  #  print (valid_ind)
    urls = data[valid_ind]
 
    #
    #
    # nums_start = pd.read_csv('./bbchindi/spiders/lastnum.csv', header = None) # which url to start from
    # nums_start = nums_start[0][0]



    start_urls = [link for link in urls]

   # start_urls = ['https://www.bbc.com/news/world-asia-58880707']

    def parse(self, response):

        #
        # yield {"START": "START",}


        ''' This function is responsible for parsing the webpage and processing it into different pipelines '''


        # Please refer to the flow chart to check how the document is being parsed
        
        subhead = 0 # Subsection count
        img_count = 0 # image count
        flag = False # summary found flag
        if 'bbc' not in response.url:
            return
 
        url_main = response.url.split('?')[0] # removing the query parameters at the end of url (cleaning the url)
        try:
            domain = domain_split(url_main.split('world/')[1])  # generalize this (Tentative: Different language scrapers will only have this field different and
        except:
            domain = "NA"
        # end div with social links or divs with recommended links different) also for old urls
        if '/av/' in url_main:
            # Media articles are the ones with only video and short text, no summary
            pd.DataFrame(np.asarray([url_main])).to_csv('medialinksf.csv', index = False, mode = 'a', header = False)
            return

        if 'live'  in url_main:
            # handling for live here (ITEM PIPELINE)
            pd.DataFrame(np.asarray([url_main])).to_csv('livelinksf.csv', index = False, mode = 'a', header = False)
            return

        if 'podcast' in url_main:
            pd.DataFrame(np.asarray([url_main])).to_csv('podcastlinksf.csv', index = False, mode = 'a', header = False)
            return
        
        # hashing the url
        url_hash = hashit(url_main)
        
        # url
        yield{"hash": url_hash, 'type': 'url', 'url_main' : url_main, 'domain': domain, }
	
        # Title
        yield{"hash": url_hash, "type": 'title', 'Title': response.css('header h1::text').get(),}
        
        # Datetime
        yield{"hash":url_hash, "type":'date', 'date': response.css('header time::attr(datetime)').get(),}
        # article contents
        article = response.css('article')
        for i in article.css('div'):
            if i.css('div[data-component="image-block"]') or i.css('div[data-component="media-block"]'):
                 
                 if i.css('div[data-component="image-block"]'):
                     ty = 'image'
                 else:
                     ty = 'video'
                 url = i.css('img::attr(src)').get()
                 if (type(url) == str) and (url != "https://ichef.bbci.co.uk/news/464/cpsprodpb/10301/production/_98950366_presentational_grey_line464-nc.jpg") and (url != "https://ichef.bbci.co.uk/news/624/cpsprodpb/1FCD/production/_105914180_line976-nc.png"):
                     try:
                        img_nm = "{}##{}##{}.jpg".format(url_hash, subhead, img_count)
                     except:
                        img_nm = 'NA'

                     try:  
                        caption = i.css('figcaption::text').getall()[-1]
                     except:
                        caption = "NA"
                     try:
                        source = i.css('figure span[role="text"]::text').getall()[-1]
                     except:
                        source = "NA"
                     
                     yield{"hash": url_hash, 'type': ty, 'image_name': img_nm, 'image_urls' : [url + "###" + img_nm], 'caption': caption, 'source': source, 'subhead':subhead, 'num_img': img_count,}
                     img_count += 1


         #        else:
          #           yield {"hash": url_hash, 'type': 'video', subhead: 'subhead'}
                
           
            elif i.css('div[data-component="text-block"]'):
                if i.css('p>b') and flag == False:
                    flag = True
                    yield{"hash":url_hash, "type": "summary", "summary":  i.css('p>b::text').get(),}
                else:
                    yield{"hash":url_hash, "type": 'para', "text": ''.join(i.css('p *::text').getall()) , 'subhead' : subhead,}
            elif i.css('div[data-component="crosshead-block"]'):
                subhead += 1 
                yield{"hash": url_hash, 'type': 'subheading', 'subheading': subhead, 'sub_head_title': i.css('h2::text').get(), }
            

        yield{"hash":url_hash, 'type': 'keyword', 'keywords': response.css('section[data-component="tag-list"] li ::text').getall(),}

        yield {"hash": url_hash, 'type': 'related', 'related_articles': list(map(response.urljoin, response.css('article>section[data-component="see-alsos"] a::attr(href)').getall())),}

        extra_links = set(map(response.urljoin, response.css('main a::attr(href)').getall()))
        ex_lnk = set(pd.read_csv('extractedlinks3.csv', header = None)[0])
        extra_links.difference_update(ex_lnk)
    #    print (rest_links, "\n\n\n\n\\n\n\n=====================\n\\n\n\n\n\n\n\n===========")
        pd.DataFrame(np.asarray(list(extra_links))).to_csv('extractedlinks3.csv', header = False, mode = 'a', index = False)
    #    yield {'\n\n\n\n\\n\n\n\n\n\n\\n\n\n\n\nasdasdsdasdasds==========================================================================================================================================================\n\n\n\n\\n\n\n\n\n\n\n\\n\n\n=======================t': rest_links,}

        # Youtube Links

       # try:
        #    yield {"hash": url_hash, 'type': 'youtube', 'youtube_links' : [i.css('div').attrib['data-e2e'][14:] for i in main.css('div[data-e2e]') if 'youtube' in i.css('div').attrib['data-e2e']]}
       # except:
        #    pass

        # links from side
       # grid = response.css('.bbc-1wf62vy>div')
       # try:
        #    tst = [response.urljoin(i.get()) for i in grid[1].css('a::attr(href)')]
       #     extra_links.extend(tst)
       # except:
        #    pass

       
 
        # Write extra collected links  ( fix handling here, create a new handler for extractedlink2.csv)
      #  pd.DataFrame(np.asarray([extra_links])).to_csv('extractedlinks3.csv', index = False, mode = 'a', header = False)

        # save last visited link, if there is a crash
        pd.DataFrame(np.asarray([url_main])).to_csv('lastlinkf.csv', index = False, mode = 'a', header= False)

        



#
#
# Within script calls:

#
#
# process = CrawlerProcess(settings={
# "FEEDS": {
#     save_name: {"format": "json"},
#
#     },
# })
#
# process.crawl(bbcSpider)
# process.start()
#
# #
