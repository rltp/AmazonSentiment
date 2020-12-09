import os
import logging
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

class amazonScrapper:
    
    def get_product_html(self, product_url, driver_path):
        '''
            Get HTML from product web page and parse it.
    
            :param product_url: link of the webpage we want to scrap
            :type page_link: string
            :return: BeautifulSoup object (HTML parsed)
            :rtype: bs4.BeautifulSoup
        '''
        driver = webdriver.Chrome(executable_path=driver_path)
        driver.get(product_url)
        time.sleep(2)
        html = driver.page_source
        driver.close()
        soup_product = BeautifulSoup(html, 'html.parser')
        
        return soup_product
    
    def extract_product_info(self, soup_product):
        '''
            Extract product infos from URL PRODUCT HTML
        
            :param product_html: BeautifulSoup Element that contains book infos
            :type product_html: bs4.element.Tag
            :return:
                - product_name : name of the product
                - product_price: price of the product
                - nbr_reviews : number of reviews for the product
                - description: description of the product
            :rtype: tuple(string, string, string, string)
        '''
        
        product_name = soup_product.find('span', {'id':'productTitle'}).text.replace("\n", "")
        product_price = soup_product.find('span', {'class':'a-color-price'}).text.replace("\n", "")
        nbr_reviews = soup_product.find('span', {'id':'acrCustomerReviewText'}).text.replace(" ratings", "")
        try:
            description = soup_product.find('div', {'id':'productDescription'}).text.replace("\n", "")
        except:
            description = "No description"
        mean_note = soup_product.find('span', {'data-hook':'rating-out-of-text'}).text.replace(" out of 5", "")
        
        for img in soup_product.findAll('img', {'id': "landingImage"}):
            img_url = img.get('src')
        
        return { 'name' : product_name, 'img': img_url ,'desc' : description, 'price' : product_price, 'note' :  mean_note, 'reviews' : nbr_reviews }
        
    def reviews_crawler(self, soup_product, max_page_number):
        '''
            Crawl into the reviews pages from the choosen product
        
            :param soup_product: BeautifulSoup Element that contains product infos
            :type product_html: bs4.element.Tag
            :param max_page_number: number of review's pages that we want to crawl
            :type max_page_number: int
            :return: start_urls : list of all reviews urls to crawl
            :rtype: list(string)
        '''
        
        start_urls=[]
        for link in soup_product.findAll("a", {"data-hook":"see-all-reviews-link-foot"}):
            reviews = link["href"]
            reviews_url = "https://www.amazon.in" + reviews
            for i in range(1, max_page_number):
                start_urls.append(reviews_url + "&pageNumber=" + str(i))
        return start_urls
        
    def get_soup_from_url(self, url_list):
        '''
            Get the html page for each review page
        
            :param url_list: list of all reviews urls to crawl
            :type url_list: list(string)
            :return: soup_amazon : list of all review's BeautifulSoup objects
            :rtype: list(bs4.element.Tag)
        '''
        soup_amazon = []
        for url in url_list:
            html = requests.get(url).text
            time.sleep(1)
            soup = BeautifulSoup(html, 'html.parser')
            soup_amazon.append(soup)
        return soup_amazon
    

    def get_user_data(self, soup_list):
        '''
            Extract the data for each user comment
        
            :param soup_list: list of all review's BeautifulSoup objects
            :type soup_list: list(bs4.element.Tag)
            :return:
                - user : name of the user
                - comment_all: price of the product
                - comment_title : number of reviews for the product
                - user_score: description of the product
            :rtype: tuple(string, string, string, string)
        '''
        user = []
        comment_all = []
        comment_title = []
        user_score = []
        for soup in soup_list:
            for reviews in soup.findAll('div', {'id':"cm_cr-review_list"}):
                for username in reviews.findAll('span', {"class": "a-profile-name"}):
                    user.append(username.text.replace("\n", ""))
                for content in reviews.findAll('span', {"data-hook": "review-body"}):
                    comment_all.append(content.text.replace("\n", ""))
                for title in reviews.findAll('a', {'data-hook':"review-title"}):
                    comment_title.append(title.text.replace("\n", ""))
                for user_sc in reviews.findAll('i', {"data-hook": "review-star-rating"}): 
                    score_user = user_sc.text.replace(" out of 5 stars", "")
                    user_score.append(score_user)

        return user, user_score, comment_title, comment_all 

    def __init__(self, url, maxpages, driver_path):
        soup_product = self.get_product_html(url, driver_path)
        self.product_data = self.extract_product_info(soup_product)
        url_list = self.reviews_crawler(soup_product, maxpages)
        soup_list = self.get_soup_from_url(url_list)
        self.user_data = self.get_user_data(soup_list)
        
    def get_product_data(self):
        return self.product_data

    def get_reviews(self):
        user, user_score, comment_title, comment_text = self.user_data
        return  pd.DataFrame(list(zip(user, user_score, comment_title, comment_text)), columns =['Username', 'Score', 'Comment Title', 'Comment'])