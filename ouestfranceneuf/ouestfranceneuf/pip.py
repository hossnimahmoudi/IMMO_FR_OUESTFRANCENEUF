# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from csv import QUOTE_ALL
from scrapy.mail import MailSender
import datetime
from scrapy.utils.project import get_project_settings
import socket
import logging
from twisted.python.failure import Failure
from scrapy.utils.request import referer_str
import time
import pprint

class OuestfranceneufPipeline(object):

    def __init__(self):
        self.files = {}
    @classmethod
    def from_crawler(cls, crawler):
       pipeline = cls()
       crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
       crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)


       return pipeline

    def spider_opened(self, spider):
       mailer = MailSender()
       settings = get_project_settings()
       hostname = socket.gethostname()
       body='''-Crawl name: {0}\n-Cache directory: {1}\n-Hostname : {2} \n -Crawler_name: ONS DRIDI'''.format(settings.get('BOT_NAME'),settings.get('HTTPCACHE_DIR'),hostname,
       )
       mailer.send(to=["o.dridi@autobiz.com"], subject="The crawl of %s is %s " % (spider.name, "launched"), body=body )
       file = open('%s.csv' % spider.name, 'w+b')
       self.files[spider] = file
       self.exporter = CsvItemExporter(file, delimiter=';', quotechar='"', quoting=QUOTE_ALL)
       self.exporter.start_exporting()

    
    def spider_closed(self, spider, reason):
        mailer = MailSender()
        pige = 1324
        intro = "Summary stats from Scrapy spider: \n\n"
        stats = spider.crawler.stats.get_stats()
        comptage = stats.get('item_scraped_count')
        pourcentage = comptage * 100 /pige
        body = intro +"Finish reason : " + reason +"\n" + "Item scraped count : " + str(comptage) +"\n" +"Le comptage a atteint " + str(pourcentage) +"%\n"
        mailer.send(to=["o.dridi@autobiz.com"], subject="The crawl of %s is %s " % (spider.name, reason), body=body )
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
    
    def process_item(self, item, spider):
       self.exporter.export_item(item)
       return item
