import sys
import peruse as ps

r_server = ps.r_server;

# Make a single call
query = 'python'
key = 'Tweets'
numTweets = 50
limit = 250

# Take user input into account
# Search query
if(len(sys.argv) > 1):
    query = sys.argv[1]

# Number of tweets to take into account
if(len(sys.argv) > 2):
    limit = int(sys.argv[2])

# Start by deleting the old key
ps.deleteKey(r_server, key)

# Move on to getting tweets
ps.pagingCall(r_server, query, key, numTweets, limit)
tweets_text = ps.getTweetsList(r_server, key)

ps.generateWordCloud(''.join(tweets_text))

# sentimentComparison(r_server)
