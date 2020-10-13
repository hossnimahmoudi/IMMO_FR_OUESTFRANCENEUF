#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

UTF8_ENCODING = 'utf-8'

import sys
reload(sys)
sys.setdefaultencoding(UTF8_ENCODING)

import scrapy
import neukolln.spiders
from neukolln.items import ImmoItem
from bs4 import BeautifulSoup
import requests
import re

import logging
logger = logging.getLogger()


class OuestfranceneufSpider(neukolln.spiders.NeukollnBaseSpider, scrapy.Spider):
    # name="ouest_fev_2020"
    # name="ouest2020_02"
    # name="ouest_202002"
    #name="ouestfrance_2020_02"
    name="test_2020_02"
    allowed_domains = ['ouestfrance-immo.com']  # FIXME
    start_urls = []  # FIXME

    neukolln_export_to_json = False
    neukolln_export_to_csv = True
    neukolln_export_to_tab = False

    # Pre processsing to get url from website sitemap.xml
    def __init__(self, *args, **kwargs):
        super(OuestfranceneufSpider, self).__init__(*args, **kwargs)
        response = requests.get('https://www.ouestfrance-immo.com/sitemaps-bdd/sitemaps.immobilier-neuf-ann-prgm-1.xml').content
        response = str(response).replace("<![CDATA[","")
        response = str(response).replace("]]>","")
        soup = BeautifulSoup(response,'lxml')
        # get all urls
        urls = soup.find_all('loc')
        # get distributors url having at the end a number diffrent from zero => distributor minipage format
        #urls_distributor = [item for item in urls if (bool(re.match('.*trouver-un-distributeur/[1-9]+',item.text)))] 
        for url in urls:
            # we ignore home page : https://www.ouestfrance-immo.com/immobilier-neuf/
            if url != "https://www.ouestfrance-immo.com/immobilier-logement-neuf/":
                self.logger.info(url.text)
                self.start_urls.append(url.text)

    def response_is_ban(self, request, response):
        # use default rules, but also consider HTTP 200 responses
        # a ban if there is 'captcha' word in response body.
        ban = super(OuestfranceneufSpider, self).response_is_ban(request, response)
        # ban = ban or 'captcha' in response.body.lower()
        return ban


    def start_requests(self):
        for url in self.start_urls:
            try:
                id_client = re.split("-",url)[-1].replace("/","")
                yield scrapy.Request(url, callback=self.parse, meta= {'crawl_date': self.crawl_date, 'id_client': id_client})
            except Exception as e:
                self.logger.error(str(e))

    
    '''
    def start_requests(self):
        
        urls=['https://www.ouestfrance-immo.com/immobilier-logement-neuf/bordoscena-prix-maitrises-bordeaux-33000-13568559/',
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/cote-mail-rennes-35000-13571040/?utm_source=alerte&utm_medium=email_interne&utm_campaign=alerte_immo&$
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/ty-ruz-saint-renan-29290-13522933/',
        #'https://www.ouestfrance-immo.com/immobilier-logement-neuf/viseo-nantes-44000-13365543/'
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/villapollonia-neuilly-sur-marne-93330-13523638/',
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/le-clos-des-moulins-bolbec-76210-13609499/']
        

             
        urls = ['https://www.ouestfrance-immo.com/immobilier-logement-neuf/le-bosquet-saint-pierre-les-elbeuf-76320-13621244/',
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/les-joyaux-de-l-erdre-nantes-44000-13610927/',
        'https://www.ouestfrance-immo.com/immobilier-logement-neuf/prochainement-dijon-21000-13610548/']
        
#       urls=['https://www.ouestfrance-immo.com/immobilier-logement-neuf/prochainement-nice-06000-13610508/',
#             'https://www.ouestfrance-immo.com/immobilier-logement-neuf/nature-sens-reims-51100-13610417/#']
#       
        #'https://www.ouestfrance-immo.com/immobilier-logement-neuf/ascension-paysagere-rennes-35000-13384407/']
        #urls=['https://www.ouestfrance-immo.com/immobilier-logement-neuf/la-garenne-de-rohan-blain-44130-13523562/']
        my_file = open("/home/n.aouini/projects/FR_OUESTFRANCE_NEUF/ouestfranceneuf/ouestfranceneuf/spiders/OFN.txt", "r")
        urls= [i.replace('\n','').replace('"','')  for i in my_file]

        for url in urls:
            try:
                #id_client = re.split("-",url)[-1].replace("/","")
                yield scrapy.Request(url, callback=self.parse)  #meta= {'crawl_date': self.crawl_date, 'id_client': id_client})
            except Exception as e:
                self.logger.error(str(e))
    '''

    def parse(self, response):
        self.logger.info("My IP is ============> " + str(response.meta["bindaddress"]))
        self.logger.info("My USER AGENT is ============> " + str(response.request.headers['User-Agent']))
        item = ImmoItem()
       # item["ANNONCE_LINK"] = response.xpath("//meta[@property='og:url']/@content").extract_first()
     

        #item["ID_CLIENT"] = response.css("#ann_id").xpath(".//@value").extract_first()
	#link = item["ANNONCE_LINK"]
	#item["ID_CLIENT"] = re.split("-",link)[-1].replace("/","")
	
        #item["PAYS_AD"] = "FR"
        # if ID_CLIENT is empty, we drop the ad
	
       # if len(item["ID_CLIENT"]) == 0:
           # return None
        soup = BeautifulSoup(response.text, 'lxml')
        js= soup.findAll("script")[2].get_text().replace("\r", " ").replace("\n", " ")
        latitude=js[js.find('lat')+7: js.find('lng')-2]
        photo=response.xpath("//img/@src[contains(.,'.jpg')]").extract()        
        categories_set = set()
        for elem in photo:
            categories_set.add(elem.strip())

        tel=response.xpath('//div[@class="btn btn-tel btn-disabled text-nowrap"]').extract()
        log = logging.getLogger("my-logger")
        log.info(tel )       
        # print(js)        
        #photo=
        #item["LATITUDE"] = response.css("#ann_lat").xpath(".//@value").extract_first()
        #item["LONGITUDE"] = response.css("#ann_long").xpath(".//@value").extract_first()
        #item["PHOTO"] = response.css("#nb_photos").xpath(".//@value").extract_first()
        # Always for sale because it is new goods
        #item["CATEGORIE"] = response.css(".blocInfosPhot
        
        #categories_td = response.css("table").xpath(".//td/strong/text()").extr
	#categories_td = response.xpath('//div[@class="libTypePrix"]/strong/text()').extract()
                #item["CATEGORIE"] = " ".join(categories_s

	#categories_td = response.xpath('//td[@class="libelle"]/text()').extract()       
        #categories_td = response.xpath('//div[@class="libTypePrix"]/strong/text()').extract()
       # categories_td1 = response.xpath('//div[@id="blocInfos"]/h3[3]/strong/text()').extract_first()

       # categories_set = set()
       # for i in range(len(categories_td)):
           # try:
                #categories_set.add(categories_td[i].strip())
                #self.logger.info(str(response.url)+"zzzzzzzzz"+str(categories_set))

           # except Exception as e:
                #self.logger.error(str(e))
        #try:
            #if categories_set:
               #for i in range(len(categories_set)):
                   #if categories_set[i] in "Appartement" :
                      
                #self.logger.info(str(response.url)+"zzzzzzzzzz"+str(categories_set))
                #categories_set = categories_set.split(',')
                #self.logger.info(str(response.url)+"zzzzzzzzzz"+str(categories_set))            
                #item["CATEGORIE"] = ' ''Appartement'' '" ".join(categories_set)
            #elif 'Terrain' or 'Maison' in categories_set:
                #cat = categories_td1
                #item["CATEGORIE"] = cat.replace('Appartement','')

           # else:
               # item["CATEGORIE"]= "AUTRES"
       # except Exception as e:
            #self.logger.error(str(e
        
       # for i in range(len(categories_td1)):
        
                #item["CATEGORIE"] = response.css("h4 strong::text").extract_first()
             

	#piece1 = response.xpath('//div[@id="blocInfos"]/h3[3]/text()').extract_first()
   

	#piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text()')[1].extract()
	#piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text

        # piece1 = response.xpath('//div[@id="blocInfos"]/h3[3]/text()').extract_first()

        #piece1 = response.xpath('//div[@id="blocInfos"]/h3[3]/text()').extract_first()
        #piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong[2]/text()').extract()
       # h = response.xpath('//div[@class="description col-10 col-md-12"]/h3[3]/text()').extract_first()
        #piece22 = piece2.xpath('//h3/strong[2]/text()')

        #piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text()')[1].extract()
        #piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text()')
        # if not h:
		#try:
                	#h=''.join([i for i in piece1 if i.isdigit()])
                #h= p 
           
