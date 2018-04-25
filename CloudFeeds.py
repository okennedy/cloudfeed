from sqlalchemy import create_engine, select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean
import pickle
from os import environ, path

class CloudFeed:
    def __init__(self):
        self.engine = create_engine('postgresql://xthemage:@/cloud')
        self.metadata = MetaData(bind=self.engine)
        self.feeds = Table('oc_news_feeds', self.metadata, autoload = True)
        self.items = Table('oc_news_items', self.metadata, autoload = True)
        self.memory_file = environ["HOME"] + "/.cloudfeed"
        if path.exists(self.memory_file):
            with open(self.memory_file, mode="rb") as f:
                self.memory = pickle.load(f)
        else:
            self.memory = {
                'last_pub' : 0
            }
        #print(self.memory["last_pub"])

    def get_feeds(self, since = None):
        connection = self.engine.connect();
        if since == None:
            since = self.memory['last_pub']
        result = connection.execute(
            select([
                self.feeds.c.title.label('feed'),
                self.items.c.title,
                self.items.c.url,
                self.items.c.author,
                self.items.c.body,
                self.items.c.pub_date
            ]).select_from(
                self.feeds.join(self.items, self.feeds.c.id == self.items.c.feed_id)
            )
            .order_by(self.items.c.pub_date.desc())
            .where(self.items.c.pub_date > since)
        )
        ret = list(result)
        if len(ret) > 0:
            last_pub_date = max([ row["pub_date"] for row in ret ])
            #print("LAST PUB: "+str(last_pub_date))
            with open(self.memory_file, mode="wb+") as f:
                pickle.Pickler(f, pickle.HIGHEST_PROTOCOL).dump({
                    'last_pub' : last_pub_date
                })
        connection.close()
        return ret

if __is_main__:
    data = CloudFeed();
    result = data.get_feeds()
    print("Count: "+str(len(result)))
    #for row in result:
    #    print(row);
        

