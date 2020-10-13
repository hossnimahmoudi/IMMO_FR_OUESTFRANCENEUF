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
    #name = 'ouestfranceneuf_201808'
    #name = 'ouestfranceneuf_201809'
    #name = 'ouestfranceneuf201810'
    #name = 'ouestfranceneuf201811'
    name='ouestfranceneuf201812'
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

    def parse(self, response):
        self.logger.info("My IP is ============> " + str(response.meta["bindaddress"]))
        self.logger.info("My USER AGENT is ============> " + str(response.request.headers['User-Agent']))
        item = ImmoItem()
        item["ANNONCE_LINK"] = response.xpath("//meta[@property='og:url']/@content").extract_first()
        item["FROM_SITE"] = response.xpath("//meta[@property='og:site_name']/@content").extract_first()
        item["ID_CLIENT"] = response.css("#ann_id").xpath(".//@value").extract_first()
        item["PAYS_AD"] = "FR"
        # if ID_CLIENT is empty, we drop the ad
        if len(item["ID_CLIENT"]) == 0:
            return None
        item["LATITUDE"] = response.css("#ann_lat").xpath(".//@value").extract_first()
        item["LONGITUDE"] = response.css("#ann_long").xpath(".//@value").extract_first()
        item["PHOTO"] = response.css("#nb_photos").xpath(".//@value").extract_first()
        # Always for sale because it is new goods
        item["ACHAT_LOC"] = "1"
        #item["CATEGORIE"] = response.css(".blocInfosPhotos h4 strong::text").extract_first()
        try:
            # nbr of row in the table is STOCK_NEUF
            item["STOCK_NEUF"] = str(len(response.css("table").xpath(".//tr").extract()))
        except:
            item["STOCK_NEUF"] = None
        categories_td = response.css("table").xpath(".//td/strong/text()").extract()
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

	if item["CATEGORIE"] == "":
		item["CATEGORIE"] = "AUTRES"

        # surface min
        try:
            surfaces = set()
            for elem in response.css("table").xpath(".//td/text()").extract():
                if "m²" in elem.strip().encode("utf8"):
                    surfaces.add(re.sub("\D","",elem.strip()))
            item["M2_TOTALE"] = min(surfaces)
        except Exception as e:
            self.logger.error(str(e))
        item["NEUF_IND"] = "Y"
        item["NOM"] = response.css("#blocInfos h2::text").extract_first()
        # ADRESSE 
        try: 
            #address = " ".join(response.xpath("//h3[span/@class = 'icon-location-pin']/text()").extract()).strip()
            address = " ".join(response.xpath("//h3[span/@class = 'icon-location-pin']/text()").extract()).strip()
            address_split = re.split("(\d{5})", address)
            # we remove postal code and city
            if len(address_split) >= 3:
                addr = re.sub("\n","",address_split[0])
                re.sub("\r","",addr)
                item["ADRESSE"] = addr.strip()
        except Exception as e:
            self.logger.error(str(e))
            item["ADRESSE"] = None
        item["VILLE"] = response.css(".blocInfosPhotos h3::text").extract_first()
        item["NEUF_IND"] = "Y"
        item["PRO_IND"] = "Y"
        item["SELLER_TYPE"] = "Pro"
        try:
            # Find the h3 having a span child with class="euro"
            item["PRIX"] = re.sub('\D','', response.xpath("//h3[span/@class = 'euro']/strong/text()").extract_first())
        except Exception as e:
            self.logger.error(str(e))
            item["PRIX"] = None
        try:
            item["PIECE"] = self.process_cat(item["CATEGORIE"])
        except Exception as e:
            self.logger.error(str(e))
            item["PIECE"] = None
        try:
            item["CP"] = re.search("(?<=cp=).*?(?=&)", response.body_as_unicode()).group(0).strip()
            item["DEPARTEMENT"] = item["CP"][:2]
        except:
            item["CP"] = None
            item["DEPARTEMENT"] = None
        item["ANNONCE_TEXT"] = " ".join(response.css(".texte::text").extract()).strip()
        #item["ANNONCE_TEXT"] = annonce_text.replace("\n?\r"," ")
        item["URL_PROMO"] = response.xpath("//meta[@property='og:url']/@content").extract_first()
        if "Date de livraison" in response.body_as_unicode():
            item["SOLD"] = "N"
        item["AGENCE_NOM"] = response.css(".blocAgence h2::text").extract_first()
        try:
            item["AGENCE_ADRESSE"] = response.css(".blocAgence h3::text").extract()[0]
            cp_ville = response.css(".blocAgence h3::text").extract()[1]
            item["AGENCE_CP"] = re.sub('\D','',cp_ville).strip()
            item["AGENCE_VILLE"] = re.sub('\d+','',cp_ville).strip()
        except:
            item["AGENCE_ADRESSE"] = None
            #item["AGENCE_CP"] = None
            item["AGENCE_VILLE"] = None
        try:
            item['AGENCE_DEPARTEMENT'] = item["AGENCE_CP"][0:2]
        except:
            item['AGENCE_DEPARTEMENT'] = None
        item["WEBSITE"] = response.xpath("//a[@title='Voir le site']/@href").extract_first()
        tels_extract = response.css(".ctaTelLine").xpath(".//strong[@id]/text()").extract()
        tels = set()
        for j in range(len(tels_extract)):
            try:
                tels.add(re.sub('\D','',tels_extract[j]).strip())
            except Exception as e:
                self.logger.error(str(e))
        # While we have phones we pop them
        if len(tels) >= 1:
            item["AGENCE_TEL"] = tels.pop()
        if len(tels) >= 1:
            item["AGENCE_TEL_2"] = tels.pop()
        if len(tels) >= 1:
            item["AGENCE_TEL_3"] = tels.pop()
        if len(tels) >= 1:
            item["AGENCE_TEL_4"] = tels.pop()
        try:
            item['AGENCE_FAX'] = re.sub('\D','', response.css(".ctaTelLine").xpath(".//strong[not(@id)]/text()").extract_first().strip())
        except:
            item['AGENCE_FAX'] = None
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
