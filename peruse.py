# Headers
from threading import Thread
import urllib
import json
import redis
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
import prettypandas as pp

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from TwitterAPI import TwitterAPI, TwitterRestPager, TwitterRequestError, TwitterConnectionError
from keys import consumer_key, consumer_secret, access_token_key, access_token_secret

# Instantiate the database
r_server = redis.Redis("localhost")

# Print all the values for a key
def printValues(server, key):
    print server.lrange(key, 0, -1)

# One time results
def singleCall(query='blockchain', count = 50):
    r = api.request('search/tweets', {'q':query, 'count':count })
    for item in r.get_iterator():
        if 'text' in item:
            print item['text']
    return

# Paging the results
def pagingCall(server, query='blockchain', key='Tweets', count = 200, limit = 200):
    # Keep tabs on the number of entries
    numEntries = 1

    r = TwitterRestPager(api, 'search/tweets', {'q':query, 'count':count})
    for item in r.get_iterator():
        if 'text' in item:
            # Pass-in tweets into a list
            server.rpush(key, re.sub(r"http\S+", "", item['text']))

            if(numEntries % 100 == 0):
                print 'Entries so far', numEntries
                #printValues(server, key)
            if(numEntries == limit):
                break

            # Move on to the next entry
            numEntries += 1

        elif 'message' in item and item['code'] == 88:
            print 'SUSPEND, RATE LIMIT EXCEEDED: %s\n' % item['message']
            break

    return

def iterateTweets(sentiment, server, pager):
    count = 0
    for tweet in pager.get_iterator():
        count += 1
        if 'text' in tweet:
            server.rpush(sentiment, re.sub(r"http\S+", "", item['text']))

            # Print progress periodically
            if(count % 100 == 0):
                print sentiment, count

def joinAndEncode(wordList):
    return urllib.quote_plus(''.join(wordList))

# Paging sentiment comparison
def sentimentComparison(server, query1 = 'python', query2 = 'javascript', count = 50):
    # Keep tabs on the number of entries
    numEntries = 1

    positiveSentiment = ' :)'
    negativeSentiment = ' :('

    h_plus = TwitterRestPager(api, 'search/tweets', {'q':joinAndEncode([query1, positiveSentiment]), 'count':count})
    h_minus = TwitterRestPager(api, 'search/tweets', {'q':joinAndEncode([query1, negativeSentiment]), 'count':count})
    d_plus = TwitterRestPager(api, 'search/tweets', {'q':joinAndEncode([query2, positiveSentiment]), 'count':count})
    d_minus = TwitterRestPager(api, 'search/tweets', {'q':joinAndEncode([query2, negativeSentiment]), 'count':count})

    tweets_list = [h_plus, h_minus, d_plus, d_minus]
    tweets_titles = ['h+', 'h-', 'd+', 'd-']
    tweets_lengths = []

    t1 = Thread(target=iterateTweets, args=(tweets_titles[0], r_server, h_plus))
    t2 = Thread(target=iterateTweets, args=(tweets_titles[1], r_server, h_minus))
    t3 = Thread(target=iterateTweets, args=(tweets_titles[2], r_server, d_plus))
    t4 = Thread(target=iterateTweets, args=(tweets_titles[3], r_server, d_minus))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    print 'sentimentComparison() complete!'

    return

def generateWordCloud(text):
    # read the mask / color image
    # taken from http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
    d = path.dirname(__file__)

    cloud_coloring = np.array(Image.open(path.join(d, "us-mask-white.png")))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(background_color="black", max_words=2000, mask=cloud_coloring,
                   stopwords=stopwords, max_font_size=40, random_state=42)
    # generate word cloud
    wc.generate(text)

    # create coloring from image
    image_colors = ImageColorGenerator(cloud_coloring)

    # show
    plt.imshow(wc)
    plt.axis("off")
    plt.show()

def generateTable(text):
    # Start by getting a frequency dictionary
    d = path.dirname(__file__)

    cloud_coloring = np.array(Image.open(path.join(d, "us-mask-white.png")))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(background_color="black", max_words=2000, mask=cloud_coloring,
                   stopwords=stopwords, max_font_size=40, random_state=42)

    frequenciesDict = wc.process_text(text)
    frequencies = pd.Series(frequenciesDict)
    frequencies.index.name = 'Word'

    print frequencies.index

    # Make table
    (pp.PrettyPandas(frequencies))

def getTweetsList(server, key):
    # Returns all tweets
    return server.lrange(key, 0, -1)

def getVal(server, key):
    return server.get(key)

def clearList(server, key):
    server.ltrim(key, -1, 0)
    return

def deleteKey(server, key):
    server.delete(key)
    return

api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret, 'oAuth2')
