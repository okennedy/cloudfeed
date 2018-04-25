from CloudFeeds import CloudFeed
from mastodon import Mastodon
import json
from os import environ, path
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

CONFIG_FILE = environ["HOME"] + "/.cloudfeed"
CONFIG = {
    'last_pub' : 0
}
LANGUAGE = 'english'

if path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, mode="r") as f:
        CONFIG.update(json.load(f))

feed = CloudFeed(
    db = CONFIG['database']
)
mastodon = Mastodon(
    client_id = CONFIG['client_id'],
    client_secret = CONFIG['client_secret'],
    access_token = CONFIG['access_token'],
    api_base_url = CONFIG['mastodon_url']
)
summarizer = LexRankSummarizer(Stemmer(LANGUAGE))
summarizer.stop_words = get_stop_words(LANGUAGE)

new_posts = feed.get_posts(
    since = CONFIG['last_pub']
)
if len(new_posts) > 0:
    CONFIG["last_pub"] = max([ post["pub_date"] for post in new_posts ])
    for post in new_posts:
        summary = summarizer(
            HtmlParser.from_string(post['body'], post['url'], Tokenizer("english")).document,
            1
        )
        post["summary"] = summary[0]
        message = "{feed}: {title}\n{url}\n\n{summary}".format(**post)
        mastodon.toot(message)
        

with open(CONFIG_FILE, mode="w+") as f:
    json.dump(CONFIG, f)
