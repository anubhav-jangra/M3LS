# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline

class customImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):

        # Take url from here
        url = request.url.split('###')[-1]
        return url

