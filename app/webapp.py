# pylint: disable=invalid-name
import os
import platform
from flask import Flask
from flask import render_template, request, send_from_directory
from flask_cors import CORS
import pandas as pd

from app.ABSA import AspectsBased
from app.scrapper import amazonScrapper

EXTERNALS_DIR = os.path.realpath(os.path.join(__file__, '..', 'externals'))

app = Flask(__name__, static_folder="./templates/build/static", template_folder="./templates/build")
CORS(app)

DRIVER_PATH = {
    'Linux' : EXTERNALS_DIR + '/chromdriver.unix',
    'Darwin' : EXTERNALS_DIR + '/chromedriver.mac',
    'Windows' : EXTERNALS_DIR + '\\chromedriver.exe'
}[platform.system()]

@app.route("/test", methods=['POST'])
def test():
    return send_from_directory(EXTERNALS_DIR, 'predict.json')


@app.route("/predict", methods=['POST'])
def predict():
    url = request.json['url']
    maxPages = request.json['maxPages']

    scrapper = amazonScrapper(url=url, maxpages=maxPages, driver_path=DRIVER_PATH)
    
    product = scrapper.get_product_data()
    reviews = scrapper.get_reviews()

    ABSA = AspectsBased(serie=reviews['Comment'])
    opinions = ABSA.identifyOpinions()
    
    return {**product, 'opinions': opinions}


@app.route("/")
def render():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
