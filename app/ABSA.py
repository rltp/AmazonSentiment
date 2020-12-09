import os
import re
import nltk
import string
from textblob import TextBlob
import pandas as pd

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')


class AspectsBased:

    def cleanTokenize(self):
        punctuations = list(string.punctuation) + ['’', '..', '...']
        stopwords = nltk.corpus.stopwords.words("english") + punctuations
        tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()

        tokenized = [tokenizer.tokenize(line.lower()) for line in self.serie]
        self.tokenize = [[[word.strip("".join(punctuations)) for word in nltk.word_tokenize(
            sentence) if word not in stopwords and len(word) > 3] for sentence in line] for line in tokenized]

    def posTagging(self):
        self.posTag = [[nltk.pos_tag(sentence) for sentence in line] for line in self.tokenize]

    def aspectExtraction(self):
        prevWord = ''
        prevTag = ''
        currWord = ''
        aspectList = []
        outputDict = {}
        # Extracting Aspects
        for line in self.posTag:
            for sentence in line:
                for word, tag in sentence:
                    if(tag == 'NN' or tag == 'NNP'):
                        if(prevTag == 'NN' or prevTag == 'NNP'):
                            currWord = prevWord + ' ' + word
                        else:
                            aspectList.append(prevWord.upper())
                            currWord = word
                    prevWord = currWord
                    prevTag = tag

        # Eliminating aspect count less than 5
        for aspect in aspectList:
            if aspectList.count(aspect) > 5 and outputDict.keys() != aspect:
                outputDict[aspect] = aspectList.count(aspect)

        self.aspects = sorted(outputDict.items(), key=lambda x: x[1], reverse=True)

    def identifyOpinions(self):
        output = dict()
        for aspect, num in self.aspects:

            polarities = {'positive': 0, 'neutral': 0, 'negative': 0}

            total = 0
            for sentence in self.tokenize:
                for word in sentence:
                    if aspect in str(word).upper():
                        total += 1
                        textblob = TextBlob(str(word))
                        output.setdefault(
                            aspect, {"sentiments": [0, 0, 0], "percentage": [0, 0, 0]})
                        polarity = textblob.sentiment.polarity

                        if polarity > 0:
                            polarities['positive'] += 1
                            output[aspect]["sentiments"][0] += polarity
                        elif polarity < 0:
                            polarities['negative'] += 1
                            output[aspect]["sentiments"][2] += polarity
                        else:
                            polarities['neutral'] += 1
                            output[aspect]["sentiments"][1] += polarity

            index = 0
            for p in polarities.keys():
                if polarities[p] > 0:
                    output[aspect]["sentiments"][index] = round(
                        output[aspect]["sentiments"][index] / polarities[p], 1)
                    output[aspect]["percentage"][index] = round(
                        (polarities[p]/total) * 100, 1)
                index += 1

            total = sum(x[1] for x in self.aspects)
            for w in list(map(lambda x: (x[0], round((x[1]/total)*100, 1)), self.aspects)):
                if w[0] in output.keys():
                    output[w[0]] = {**output[w[0]], 'weight': w[1]}
        return output

    def __init__(self, serie):
        self.serie = serie
        self.cleanTokenize()
        self.posTagging()
        self.aspectExtraction()
