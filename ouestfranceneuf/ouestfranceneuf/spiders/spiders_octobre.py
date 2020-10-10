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
   #name="ouestfranceneuf_2020_02"
    name="ouestfranceneuf_2020_09"
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
        item["ANNONCE_LINK"] = response.xpath("//meta[@property='og:url']/@content").extract_first()
        item["FROM_SITE"] = response.xpath("//meta[@property='og:site_name']/@content").extract_first()

        #item["ID_CLIENT"] = response.css("#ann_id").xpath(".//@value").extract_first()
	link = item["ANNONCE_LINK"]
	item["ID_CLIENT"] = re.split("-",link)[-1].replace("/","")
	
        item["PAYS_AD"] = "FR"
        # if ID_CLIENT is empty, we drop the ad
	
        if len(item["ID_CLIENT"]) == 0:
            return None
        soup = BeautifulSoup(response.text, 'lxml')
        js= soup.findAll("script")[2].get_text().replace("\r", " ").replace("\n", " ")
       
        print(js)
        latitude=js[js.find('lat:')+4: js.find('lng:')-2]
        if len(latitude)==1:
           latitude=""
        item["LATITUDE"]=latitude
        longitude=js[js.find('lng:')+4: js.find('nb_annonces:')-2]
        if len(longitude)==1:
           longitude=""
        item["LONGITUDE"]=longitude
        photo=response.xpath("//img/@src[contains(.,'.jpg')]").extract()


        categories_set = set()
        for elem in photo:
            categories_set.add(elem.strip())

        item["PHOTO"]=len(categories_set)+1
        #photo=
        #item["LATITUDE"] = response.css("#ann_lat").xpath(".//@value").extract_first()
        #item["LONGITUDE"] = response.css("#ann_long").xpath(".//@value").extract_first()
        #item["PHOTO"] = response.css("#nb_photos").xpath(".//@value").extract_first()
        # Always for sale because it is new goods
        item["ACHAT_LOC"] = "1"
        #item["CATEGORIE"] = response.css(".blocInfosPhotos h4 strong::text").extract_first()
        try:
            # nbr of row in the table is STOCK_NEUF
            item["STOCK_NEUF"] = str(len(response.xpath('//div[@class="col-5 col-md-4 pl-2 text-capitalize libelle"]').extract()))
        except:
            item["STOCK_NEUF"] = None
	
	'''
	y= response.xpath('//div[@class="libTypePrix"]/strong/text()').extract()
        y1=[str(i).strip() for i in y]
        #y1.remove('')
        #y1.remove('')
        if 'Terrain' in y1:
                res1='Terrain'
        elif 'Maison' in y1:
                res1='Maison'
        else:
                z=response.xpath('//div[@class="libTypePrix"]/strong/span/text()').extract()
                i=0
                if len(y1) ==0:
                        res1='AUTRES'
                else:
                        while i<len(z):
                                i+=1
                                y1.remove('')

                        #res = z[0] +' '+y1[0]+' ' +z[1] +y1[1]
                        res = ['Appartement '+i for i in y1]
                        res2 = ' '.join(res)
			res1=" ".join(re.findall("Appartement T\d",res2))
        item["CATEGORIE"]= res1 
	'''
        
        #categories_td = response.css("table").xpath(".//td/strong/text()").extract()
	'''
        categories_td = response.xpath('//div[@class="libTypePrix"]/strong/text()').extract()
        categories_set = set()
        for i in range(len(categories_td)):
            try:
                categories_set.add(categories_td[i].strip())
            except Exception as e:
                self.logger.error(str(e))
        try:
            item["CATEGORIE"] = " ".join(categories_set)
        except Exception as e:
            self.logger.error(str(e))
        
	'''	

	'''
	#categories_td = response.xpath('//div[@class="libTypePrix"]/strong/text()').extract()
        categories_td = response.xpath('//td[@class="libelle"]/text()').extract()
        categories_td1 = response.xpath('//div[@id="blocInfos"]/h3[3]/strong/text()').extract_first()
          
        categories_set = set()
        for i in range(len(categories_td)):
            try:
                categories_set.add(categories_td[i].strip())

            except Exception as e:
                self.logger.error(str(e))
        try:
            if categories_set:            
                #item["CATEGORIE"] = " ".join(categories_set)
		item["CATEGORIE"] = ' ''Appartement'' '" ".join(categories_set)
            elif 'Terrain' or 'Maison' in categories_set:
                cat = categories_td1
                item["CATEGORIE"] = cat.replace('Appartement','')
            else:
                item["CATEGORIE"]= "AUTRES"
        except Exception as e:
            self.logger.error(str(e))
	'''

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
            #self.logger.error(str(e))


        categories_td = response.xpath('//div[@class="col-5 col-md-4 pl-2 text-capitalize libelle"]/text()').extract()
        categories_td1 = response.xpath('//div[@class="col-5 col-md-4 pl-2 text-capitalize libelle"]/span[@class="d-none d-md-inline text-capitalize"]/text()').extract()
       
        categories_set = set()
        piece_list=[]
        
       # for i in range(len(categories_td1)):
           # if categories_td1[i]  
       
        
        for i in range(len(categories_td)):
            try:
                if 'T1' in str(categories_td[i]) or 'T2' in str(categories_td[i]) or 'T3' in str(categories_td[i]) or 'T4' in str(categories_td[i]) or 'T5' in str(categories_td[i]):
                     categories_set.add("Appartement"+" "+categories_td[i].strip())
                     piece=re.sub('\D','',categories_td[i].strip())
                     log = logging.getLogger("piece1")
                     log.info(piece)
                     piece=int(piece)
                     piece_list.append(piece)
                elif 'appartement' not in categories_td1[i]:
                     categories_set.add(categories_td1[i].strip())

            except Exception as e:
                   self.logger.error(str(e))


          
        if categories_set:
             item["CATEGORIE"]=categories_set
        else:
             item["CATEGORIE"]=response.xpath('//div[@class="description col-9 col-md-12"]/h3[3]/strong/text()').extract()
        if piece_list:
           log = logging.getLogger("liste_piece")
           log.info(piece)
           item["PIECE"]=min(piece_list)

        # sometimes catgeorie is not detailed :
	'''
        if item["CATEGORIE"] == "":
            try:
                #item["CATEGORIE"] = response.css("h4 strong::text").extract_first()
                item["CATEGORIE"] = response.xpath("//td/strong/text()").extract_first()
            except Exception as e:
                print("ICI")
                self.logger.error(str(e))
	'''


	'''
	if item["CATEGORIE"] == "":
		item["CATEGORIE"] = "AUTRES"
	'''


	'''
	piece1 = response.xpath('//div[@class="blocInfosPhotos visible-desktop"]/h4[1]/text()').extract_first()

	#piece1 = response.xpath('//div[@id="blocInfos"]/h3[3]/text()').extract_first()
        piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong[2]/text()')[1]

	#piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text()')[1].extract()
	#piece2 = response.xpath('//div[@id="blocInfos"]/h3/strong/text()')
	if piece1:
		piece1 =''.join([i for i in piece1 if i.isdigit()])
		item["PIECE"] = piece1
	elif piece2:
		piece2 =''.join([i for i in piece2 if i.isdigit()])
		item["PIECE"] = piece2
	else:
		item["PIECE"] = ""
	'''


	'''
	piece1 = response.xpath('//div[@class="blocInfosPhotos visible-desktop"]/h4[1]/text()').extract_first()

	h=response.xpath('//div[2]/section/div/div[4]/div[6]/div[1]/div[2]/h3[3]/strong[2]/text()').extract_first()
       #if not h:
	       #h=piece1
	if h:
		h="".join([i for i in h if i.isdigit()])
	else:
		h=""
	item["PIECE"]=h
	'''

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
                #h= piece1
		#except:
	'''
        try:
            pieces= set()
            for elem in response.xpath('//div[@class="description col-10 col-md-12"]/h3[3]/strong/text').extract():
                if "pièces" in elem.strip():
                    pieces.add(re.sub("\D","",elem.strip()))
            item["PIECE"] = min(pieces)
        except Exception as e:
            self.logger.error(str(e))
        '''
        '''        
        h1=response.xpath("//h3[contains(.,'appartement')]/text()").extract_first()
        h2=response.xpath("//h3[contains(.,'appartement')]/strong[2]/text()").extract_first()
        if h1:
           h1="".join([i for i in h1 if i.isdigit()])
           item["PIECE"]=h1

        if not h1 and h2:
                   
           h2="".join([i for i in h2 if i.isdigit()])
           item["PIECE"]=h2
        else:
           item["PIECE"]=""
        '''
      


       # if not pieces:
          # piece2=response.xpath('//div[@class="description col-10 col-md-12"]/h3[3]/text').extract_first()
          # piece2 =''.join([i for i in piece2 if i.isdigit()])
          # item["PIECE"]=piece2 




        # surface min
        try:
            surfaces = set()
            for elem in response.xpath('//div[@class="col-2 col-md-1"]/text()').extract():
                if "m²" in elem.strip().encode("utf8"):
                    surfaces.add(re.sub("\D","",elem.strip()))
            item["M2_TOTALE"] = min(surfaces)
        except Exception as e:
            self.logger.error(str(e))
        item["NEUF_IND"] = "Y"
        item["NOM"] = response.xpath('//h2[@class="title col-9 col-md-12"]/text()').extract_first()
        # ADRESSE 
        try: 
            #address = " ".join(response.xpath("//h3[span/@class = 'icon-location-pin']/text()").extract()).strip()
            address = " ".join(response.xpath("//h3[@class='desc-line']/span/text()").extract()).strip()
            address_split = re.split("(\d{5})", address)
            # we remove postal code and city
            if len(address_split) >= 3:
                addr = re.sub("\n","",address_split[0])
                re.sub("\r","",addr)
                item["ADRESSE"] = addr.strip()
        except Exception as e:
            self.logger.error(str(e))
            item["ADRESSE"] = None
        item["VILLE"] = response.xpath('//div[@class="col-12 text-center title-div"]/h2[@class="title"]/text').get()
        item["NEUF_IND"] = "Y"
        item["PRO_IND"] = "Y"
        item["SELLER_TYPE"] = "Pro"
        
        try:
            # Find the h3 having a span child with class="euro"
            prix=response.xpath('//*[@id="site-content"]/div[2]/div[2]/div/div[1]/div[2]/div[3]/h3[2]/strong[1]/text()').extract_first()
            prix=prix.strip().replace(' ','')
            item["PRIX"]=prix
        except Exception as e:
            self.logger.error(str(e))
            item["PRIX"] = ''
        
        #try:
            #item["PIECE"] = self.process_cat(item["CATEGORIE"])
        #except Exception as e:
            #self.logger.error(str(e))
            #item["PIECE"] = None
        
        
        try:
            item["CP"] =re.split("-",link)[-2]
            item["DEPARTEMENT"] = item["CP"][:2]
        except:
            item["CP"] = None
            item["DEPARTEMENT"] = None
        item["ANNONCE_TEXT"] = " ".join(response.css(".texte::text").extract()).strip()
        #item["ANNONCE_TEXT"] = annonce_text.replace("\n?\r"," ")
        item["URL_PROMO"] = response.xpath("//meta[@property='og:url']/@content").extract_first()
        if "Date de livraison" in response.body_as_unicode():
            item["SOLD"] = "N"
        item["AGENCE_NOM"] = response.xpath('//h2[@class="client-infos-txt"]/strong/text()').extract_first()
        # try:
        item["AGENCE_ADRESSE"] = response.xpath('//address/h3[1]/text()').get()
        cp_ville = response.xpath('//address/h3[2]/text()').get()
        item["AGENCE_CP"] = re.findall(r'\d+',cp_ville)
        item["AGENCE_VILLE"] = re.sub('\d+','',cp_ville).strip()
       # except:
            #item["AGENCE_ADRESSE"] = None
            #item["AGENCE_CP"] = None
            #item["AGENCE_VILLE"] = None
        try:
            item['AGENCE_DEPARTEMENT'] = item["AGENCE_CP"][0:2]
        except:
            item['AGENCE_DEPARTEMENT'] = None
        item["WEBSITE"] = response.xpath("//a[@class='d-block']/@href").extract_first()
        #tels_extract = response.css(".ctaTelLine").xpath(".//strong[@id]/text()").extract()
	tel_extract = response.xpath('//div[@class="btn btn-tel btn-disabled text-nowrap"]/text()').get()
        tel=str(tel_extract).replace(' ','')
        item["AGENCE_TEL"]=tel 
        
        log = logging.getLogger("my-logger")
        log.info(tel_extract)
 
       # tels = set()
       # for j in range(len(tels_extract)):
           # try:
               # tels.add(re.sub('\D','',tels_extract[j]).strip())
           # except Exception as e:
               # self.logger.error(str(e))
        # While we have phones we pop them
       # if len(tels) >= 1:
           # item["AGENCE_TEL"] = tels.pop()
       # if len(tels) >= 1:
           # item["AGENCE_TEL_2"] = tels.pop()
       # if len(tels) >= 1:
           # item["AGENCE_TEL_3"] = tels.pop()
       # if len(tels) >= 1:
           # item["AGENCE_TEL_4"] = tels.pop()
       # try:
           # item['AGENCE_FAX'] = re.sub('\D','', response.css(".ctaTelLine").xpath(".//strong[not(@id)]/text()").extract_first().strip())
       # except:
           # item['AGENCE_FAX'] = None

        '''
	ville = " ".join(response.xpath("//h3[span/@class = 'icon-location-pin']/text()").extract()).strip()
        ville_split = ville.split(' ')
        item['VILLE']= ville_split[-1]
	'''
        '''
      	ville1 = " ".join(response.xpath("//h3[span/@class = 'icon-location-pin']/text()").extract()).strip()
        ville2 = response.xpath("/html/body/div[2]/section/div[2]/div[1]/div/span[5]/a/span/text()").extract_first()
        if ville1:
        #ville = ville.split(' ')
                ville1 = ville1.split(' ')
                item['VILLE']= ville1[-1]
        elif ville2:
                ville2 = ville2.split(' ')
                item['VILLE']= ville2[0]
        else:
                item['VILLE']= "" 

        '''
       # if not item["VILLE"] or item["VILLE"]=="":
        item["VILLE"]=response.xpath('//div[@class="col-12 text-center title-div"]/h2[@class="title"]/text()').get()
        if item["STOCK_NEUF"]=="0" or item["STOCK_NEUF"]==None :
           item["STOCK_NEUF"]="1"             
        return item


    def process_cat(self,x):
        if "tudio" in x:
            return 1
        elif "aison" in x:
            return None
        elif "errain" in x:
            return None
        elif "ppartement" in x:
            return min(int(s) for s in re.sub("\D","",x).strip())   
        else :
            return ""
