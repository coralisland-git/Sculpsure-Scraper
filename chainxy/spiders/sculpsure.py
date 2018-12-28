# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from scrapy import signals

from scrapy.xlib.pydispatch import dispatcher

from lxml import etree

from lxml import html

import time

import pdb

import random


class Sculpsure(scrapy.Spider):

	name = 'sculpsure'

	domain = 'https://www.sculpsure.com/'

	history = []

	output = []

	request_log = []

	def __init__(self):

		script_dir = os.path.dirname(__file__)

		file_path = script_dir + '/US_Zipcode.json'

		with open(file_path) as data_file:    

			self.location_list = json.load(data_file)

		script_dir = os.path.dirname(__file__)

		file_path = script_dir + '/proxies.txt'

		with open(file_path, 'rb') as text:

			self.proxy_list =  [ "http://" + x.strip() for x in text.readlines()]

	
	def start_requests(self):

		treatment_list = ['33', '116']

		for location in self.location_list[3690:]:

			for treatment in treatment_list:

				url = 'https://www.sculpsure.com/results/?campaign-code=default&session-id=default&source=Other&country=us&treatment='+treatment+'&zipcode='+str(location['zipcode'])+'&proximity=300'

				yield scrapy.Request(url, callback=self.parse, meta={'proxy' : random.choice(self.proxy_list)})


	def parse(self, response):

		provider_list = response.xpath('//ul[@class="provider-list"]//a[@class="provider-card__logo"]/@href').extract()

		for provider in provider_list:

			if provider not in self.history:

				self.history.append(provider)

				yield scrapy.Request(provider, callback=self.parse_detail, meta={'proxy' : random.choice(self.proxy_list)})


	def parse_detail(self, response):

		try:

			email_section = self.validate(''.join(response.xpath('//div[@class="provider-form provider-form--left-aligned"]//script//text()').extract()))

			name = email_section.split('"providerName":')[1].split(',')[0].strip().replace('"','').strip()

			email_list = email_section.split('"providersemail":')[1].split(',})')[0].strip().replace('"','').strip().split(';')

			website = response.xpath('//a[@class="sjcyno-website-link"]//@href').extract_first()

			detail_list = response.xpath('//ul[@class="provider-contact__details"]//div[@class="provider-contact__location"]')

			address = '  '

			phone = '  '

			for detail in detail_list:

				detail = ''.join(self.eliminate_space(detail.xpath('.//text()').extract()))

				if 'Phone:' in detail:

					addr_temp = detail.split('Phone:')[0]

					if addr_temp not in address:
						
						address += addr_temp + ' | '

					p_temp = detail.split('Phone:')[1]

					if p_temp not in phone:				

						phone += p_temp + ' | '

				else:

					if detail not in address:
						
						address += detail + ' | '


			for email in email_list:

				if email != '' and name != '' :

					item = ChainItem()

					item['name'] = name

					item['email'] = email

					item['phone'] = phone[:-2].strip()

					item['website'] = website

					item['address'] = address[:-2].strip()

					item['url'] = response.url

					yield item

		except:

			pass


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp

	def count(self, item, arr):

		num = 0

		for tmp in arr:

			if tmp == item:

				num += 1

		return num