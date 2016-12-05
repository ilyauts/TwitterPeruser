![Alt text](TwP.png?raw=true)

# TwitterPeruser
Peruse Twitter, maybe discover something!

# Instructions
Twitter Peruser relies on a couple of external libraries and databases:
* TwitterAPI
* Redis

To install:

1) Install TwitterAPI:

    pip install TwitterAPI

2) Install Redis:

    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make

3) Start the Redis server:

    redis-server

4) In a new terminal tab, test Redis (should expect a PONG response):

    redis-cli ping

5) Install wordcloud:

    pip install wordcloud

6) Copy keys.template and call it keys.py. Replace bracketed values in that file with your secret Twitter keys

7) Run example which uses the module:

    python peruseDriver.py [query in quotes] [number of tweets to be used]
