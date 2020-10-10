from scrapy import signals

class proxies(object):
        def process_request(self, request, spider):
                request.meta['proxy'] = 'https://5.135.3.16-23'
