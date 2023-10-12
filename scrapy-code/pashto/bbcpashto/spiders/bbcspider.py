import scrapy
# from scrapy.crawler import CrawlerProcess  # To call within script

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


# extra_links = [] # array for storing extra links

class bbcSpider(scrapy.Spider):
    '''This is our original spider for bbchindi scraping'''

    # Defining the name of the spider
    name = 'bbcpashto'

    # This is where we enter all our url's for scraping

    data = pd.read_csv('extralinks.csv', header = None)[0]
    valid_ind = (data.str.contains('bbc')) & (data.str.startswith('http'))
    urls = data[valid_ind]
    #
    #
    # nums_start = pd.read_csv('./bbchindi/spiders/lastnum.csv', header = None) # which url to start from
    # nums_start = nums_start[0][0]
    start_urls = [link for link in urls]

#    start_urls = ['https://www.bbc.com/pashto/world-58894043']

    def parse(self, response):

        #
        # yield {"START": "START",}


        ''' This function is responsible for parsing the webpage and processing it into different pipelines '''

        extra_links = []
        # Please refer to the flow chart to check how the document is being parsed
        div = response.css('main>div') # [-1] is to remove the last div which contains share and social media links
        subhead = 0 # Subsection count
        img_count = 0 # image count
        flag = False # summary found flag
        if 'bbc' not in response.url:
            return

        url_main = response.url.split('?')[0] # removing the query parameters at the end of url (cleaning the url)
        try:
            domain = domain_split(url_main.split('pashto/')[1])  # generalize this (Tentative: Different language scrapers will only have this field different and
        except:
            domain = "NA"
        # end div with social links or divs with recommended links different) also for old urls
        if 'media' in url_main or '/av/' in url_main or 'video' in url_main:
            # Media articles are the ones with only video and short text, no summary
            pd.DataFrame(np.asarray([url_main])).to_csv('medialinks.csv', index = False, mode = 'a', header = False)
            return

        if 'live'  in url_main:
            # handling for live here (ITEM PIPELINE)
            pd.DataFrame(np.asarray([url_main])).to_csv('livelinks.csv', index = False, mode = 'a', header = False)
            return

        if 'podcast' in url_main:
            pd.DataFrame(np.asarray([url_main])).to_csv('podcastlinks.csv', index = False, mode = 'a', header = False)
            return
     
       


        related_word_unchecked = True # Visiting related flag
        url_hash = hashit(url_main) # Hashing the url

        # Self explanatory
        yield{'hash': url_hash, 'type': 'url', 'url_main' : url_main, 'domain' : domain,}

        # Going over every div in our main section (The article content)
        for i in div:
            # links from within the div and recommended
            if i.css("section[data-e2e='recommendations-heading']"):
                extra_links.extend(list(map(response.urljoin, i.css('a::attr(href)').getall())))
                yield {"hash": url_hash, "type": "recommended",
                    "recommended_articles" : [response.urljoin(a.get()) for a in i.css('ul li a::attr(href)')],

                }

            # If div has some other links, we store them too
            if (i.css('a')):
                extra_links.extend(list(map(response.urljoin, i.css('a::attr(href)').getall())))

            # Getting content from the main part from every div

            # Start with heading
            if i.css('h1'):
                yield{"hash": url_hash, 'type': 'title', 'Title' : i.css('h1::text').get(),}

            # Check for date
            # Check for date
            elif i.css('time'):
                try:
                    dt = i.css('time::attr(datetime)').get()
                except:
                    dt = "NA"
                yield{"hash": url_hash, 'type': 'date', 'date': dt,}
                
            # Check for image
            elif i.css('time'):
                try:
                    dt = i.css('time::attr(datetime)').get()
                except:
                    dt = "NA"
                yield{"hash": url_hash, 'type': 'date', 'date': dt,}

            # Check for image
            elif i.css('figure'):
                url = i.css('img::attr(src)').get()
                if (url == "https://ichef.bbci.co.uk/news/640/cpsprodpb/C593/production/_106297505_3fbf8c1c-f922-4179-bf82-504ee210e5fe.jpg") or (url == "https://ichef.bbci.co.uk/news/640/cpsprodpb/D32F/production/_103936045_redlinenew.jpg") or (url == "https://ichef.bbci.co.uk/news/624/cpsprodpb/17BE/production/_92787060_line2.gif") or (url == "https://ichef.bbci.co.uk/news/640/cpsprodpb/13CD5/production/_110390118_4d2ec00d-ebaf-43e1-8c10-18ce76e8cbfe.jpg") or (url  =="https://ichef.bbci.co.uk/news/640/cpsprodpb/D32F/production/_103936045_redlinenew.jpg") or (url == "https://ichef.bbci.co.uk/news/640/cpsprodpb/F326/production/_121064226_line.jpg"):
                #    print (url, "HERE\n\n\\n\n\n\\n\n\n\n\\n\n\n\\n\\n\n\n\\n\n=======================\n\n\n\\n\n\n\n", hashit(url))
                     continue
                else:
                    # source list
                    src_list = i.css('span::text').getall()
                    if len(src_list) > 1: # source exists
                         source = src_list[1]
                    else:
                         source = None

                    # caption of the image
                    caption = i.css('figcaption>p::text').get()
                    # Image name is the hash of the "cleaned url without any query  parameters + ## the subheading to which the image belongs to + ## n-th image of the overall document "
                    img_nm = "{}##{}##{}.jpg".format(url_hash,subhead,img_count)

                    yield {"hash": url_hash, 'type': 'image','image_name': img_nm,
                # image_urls is the keyword which goes in the image pipeline as url and obtains the image, the name of the image is generated in the image pipeline
                # we pass the image name as a # value , since this does not affects the url in any way because its an image file, we can use it to disguise our image name in it
                # and pass it inside the image pipeline which takes url to save names, we then extract the hash value disguised in the url to save our image file

                    'image_urls' : [url+"###"+ img_nm], # image hashing with URLs
                    'caption' : caption, 'source' : source,'subhead' : subhead, 'num_img': img_count,}

                    img_count += 1


            #  summary, if summary is not found until now (flag)
            elif i.css('p>b') and flag == False:
                flag = True # swich summary found flag
                yield{
"hash": url_hash,                 'type': 'summary',
                'summary': i.css('p>b::text').get(),
                }

            # short subheadings
         #   elif i.css('p>b') and flag == True:
           #     r = i.css('b::text').getall()
          #      c = ''.join(r)
                # Hindi Specific code
            #    if c == 'य भ पढ' or c == 'यह भ पढ' or "ऐप क लए" in c or len(c) < 15:
             #       pass
              #  else:
               #     subhead += 1
                #    yield{"hash": url_hash, 'type': 'subheading', 'subheading': subhead,'sub_head_title' : c,}

            # Else paragraph normal
            elif i.css('p') and not i.css('h2'):
                # pargraph with link embed
                if (i.css('a')):
                    if "英語記事" in i.css('::text').get():  # japanese
                        yield {"hash" : url_hash, "type": "english_url", "english_url": i.css('a::attr(href)').get(),}
                        
                    elif (i.css('p a::text').get()) != None and (i.css('p::text').get()) != None:
                        x = i.css('p a::text').get()
                        y =  i.css('p::text').get()
                        yield{"hash": url_hash, 'type': 'para', 'text' : x  + y + "\n", 'subhead' : subhead}

                elif (i.css('p::text').get()) != None:
                    yield {"hash": url_hash, 'type': 'para', 'text' :  ''.join(i.css('p *::text').getall()), 'subhead': subhead}

            # subheadings general
            elif i.css('h2'):
                subhead += 1
                yield{"hash": url_hash, 'type': 'subheading' , 'subheading': subhead, 'sub_head_title': i.css('h2::text').get(),}

        # Outside our main loop now and check for other content
        # Key Words
        if related_word_unchecked:
            related_word_unchecked = False
            yield{"hash": url_hash, 'type': 'keyword', 'keywords': response.css('aside li>a::text').getall(),}

        # Youtube Links
        try:
            yield {"hash": url_hash, 'type': 'youtube', 'youtube_links' : [i.css('div').attrib['data-e2e'][14:] for i in main.css('div[data-e2e]') if 'youtube' in i.css('div').attrib['data-e2e']]}
        except:
            pass

        # Related Articles
        for i in response.css('section[data-e2e="related-content-heading"] li'):
            rel_url = response.urljoin(i.css('a::attr(href)').get())
            try:
                rel_date = i.css('time:attr(datetime)').get()
            except:
                rel_date = 'NA'
            rel_hash = hashit(rel_url)
            rel_tuple = ({'url': rel_url}, {'date', rel_date}, {'hash',
rel_hash})

            # add in extra links to scrape later
            extra_links.append(rel_url)
            # rel_articles.add(rel_tuple)
            yield {"hash": url_hash, 'type':'related', "related_article" : rel_tuple,}

        # Youtube Links
        try:
            yield {"hash": url_hash, 'type': 'youtube', 'youtube_links' : [i.css('div').attrib['data-e2e'][14:] for i in main.css('div[data-e2e]') if 'youtube' in i.css('div').attrib['data-e2e']]}
        except:
            pass

        try:
            sd = list(map(response.urljoin, response.css('section[data-e2e="features-analysis-heading"] a::attr(href)').getall()))
            extra_links.extend(sd)
            #print (sd)
           # print("ASIDHOASDH++++++++___________________===============================\n\n\n\n\n\n\\n\n\n====================================================n\n\n\\n\n\n\n\n\n\n\n\n")
        except:
            pass
        # links from side
        grid = response.css('.bbc-1wf62vy>div')
        try:
            tst = [response.urljoin(i.get()) for i in grid[1].css('a::attr(href)')]
            extra_links.extend(tst)
        except:
            pass

        lnks_ = list(map(response.urljoin, response.css('main a::attr(href)').getall()))
        extra_links.extend(lnks_)
        # save last visited link, if there is a crash
        pd.DataFrame(np.asarray([url_main])).to_csv('lastlink.csv', index = False, mode = 'a', header= False)

        extra_links = set(extra_links)
        ex_lnk = set(pd.read_csv('extralinks2.csv', header = None)[0])
        extra_links.difference_update(ex_lnk)
        l_lnk = set(pd.read_csv('lastlink.csv', header = None)[0])
        extra_links.difference_update(l_lnk)
      # print (rest_links, "\n\n\n\n\\n\n\n=====================\n\\n\n\n\n\n\n\n===========")
        pd.DataFrame(np.asarray(list(extra_links))).to_csv('extralinks2.csv', header = False, mode = 'a', index = False)
