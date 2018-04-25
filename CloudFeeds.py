from sqlalchemy import create_engine, select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean

class CloudFeed:
    def __init__(self, db):
        self.engine = create_engine(db)
        self.metadata = MetaData(bind=self.engine)
        self.feeds = Table('oc_news_feeds', self.metadata, autoload = True)
        self.items = Table('oc_news_items', self.metadata, autoload = True)
        #print(self.memory["last_pub"])

    def get_posts(self, since = 0):
        connection = self.engine.connect();
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
        ret = list([ dict(post) for post in result ])
        connection.close()
        return ret

if  __name__ =='__main__':
    data = CloudFeed();
    result = data.get_feeds()
    print("Count: "+str(len(result)))
    #for row in result:
    #    print(row);
        

