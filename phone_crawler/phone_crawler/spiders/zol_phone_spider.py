#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @author LeoWang
# @date 2023/5/22
import scrapy
from phone_crawler.items import PhoneSkuItem
from loguru import logger
import datetime


class ZolSpider(scrapy.Spider):
    name = "PhoneBaseSpider"
    allowed_domains = ["detail.zol.com.cn"]
    custom_settings = {
        # 设置使用的管道
        'ITEM_PIPELINES': {
            'phone_crawler.pipelines.BrandImagePipeline': 200,
            'phone_crawler.pipelines.MysqlPipeline'     : 300,
        },
    }
    start_urls = [
        f"https://detail.zol.com.cn/cell_phone_index/subcate57_0_list_3500-100000_0_1_2_0_{_}.html"
        for _ in range(1, 18)
    ]

    def parse(self, response, **kwargs):
        # 爬虫起始点, 先爬取手机列表页
        for start_url in self.start_urls:
            yield scrapy.Request(start_url, callback=self.parse_page)

    @logger.catch
    def parse_page(self, response, **kwargs):
        # 爬取手机列表页
        # 爬取class为pic-mode-box的div下的所有包含data-follow-id属性的li标签
        for product in response.css('.pic-mode-box li[data-follow-id]'):
            item = PhoneSkuItem()
            _id = product.css('li::attr(data-follow-id)').get()
            item['id'] = _id[1:] if _id else None
            _name = product.css('li h3 a::text').get().strip()
            item['name'] = _name.strip() if _name else None
            item['intro'] = product.css('li h3 a span::text').get()
            _price = product.css('.price-type::text').get()
            item['price'] = _price if _price != '暂无报价' else None
            item['score'] = product.css('.score::text').get()
            _url = product.css('li a[title]::attr(href)').get()
            item['url'] = r"https://detail.zol.com.cn" + _url
            item['img_url'] = product.css('img').re_first(r'src="(.+?)"')
            comments_num = product.css('.comment-num::text').re_first(r'\d+')
            item['comments_num'] = comments_num if comments_num else '0'
            item['last_modify'] = datetime.datetime.now()
            yield item
