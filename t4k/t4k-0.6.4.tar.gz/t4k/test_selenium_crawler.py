#!/usr/bin/env python
from selenium_crawler import SeleniumCrawler, uses_selenium


class TestCrawler(SeleniumCrawler):

	HOMEPAGE = 1
	ERROR_PAGE = 2

	@uses_selenium
	def crawl(self):

		# For a demo, let's get a couple web pages 
		urls = ['http://ubuntu.com', 'http://ubuntu.com/fake']
		for url in urls:

			# Use delay() to avoid making requests too often
			self.delay()

			# Get a web page
			print '\nfetching %s' % url
			self.driver.get(url)

			# Recognize the kind of page 
			page_type = self.wait(self.recognize_page)
			if page_type == self.HOMEPAGE:
				print 'got the home page'
			elif page_type == self.ERROR_PAGE:
				print 'got a 404 page'

			# Get the page source
			print "here's a snippet of page source:"
			print self.get_page_source()[:100]

		print '\nDone!'


	def recognize_page(self):

		# Is it a profile page?
		try:
			self.driver.find_element_by_class_name('homepage')
			return self.HOMEPAGE
		except self.NoSuchElementException:
			pass

		# Is it a 404 page?
		try:
			self.driver.find_element_by_class_name('error404')
			return self.ERROR_PAGE
		except self.NoSuchElementException:
			pass

		return False

if __name__ == '__main__':
	crawler = TestCrawler()
	crawler.crawl()
