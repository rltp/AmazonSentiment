# pylint: disable=invalid-name
import os
import platform
from flask import Flask
from flask import render_template, request
import pandas as pd

from app.ABSA import AspectsBased
from app.scrapper import amazonScrapper

app = Flask(__name__)

EXTERNALS_DIR = os.path.realpath(os.path.join( __file__, '..', 'externals' ))

DRIVER_PATH = {
    'Linux' : EXTERNALS_DIR + '/chromdriver.unix',
    'Darwin' : EXTERNALS_DIR + '/chromedriver.mac',
    'Windows' : EXTERNALS_DIR + '\\chromedriver.exe'
}[platform.system()]

@app.route("/predict", methods=['POST'])
def predict():
    url = request.json['url']
    maxPages = request.json['maxPages']
    scrapper = amazonScrapper(url=url, maxpages=maxPages, driver_path=DRIVER_PATH)
    
    product = scrapper.get_product_data()
    reviews = scrapper.get_reviews()
    ABSA = AspectsBased(serie=reviews['Comment'])
    opinions = ABSA.identifyOpinions()
    print(ABSA.aspects, len(reviews))
    return {**product, 'opinions': opinions}

@app.route("/")
def render():
    return render_template('templates/index.html')


if __name__ == "__main__":
    app.run()
