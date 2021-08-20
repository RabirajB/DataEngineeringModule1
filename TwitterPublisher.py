from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sys
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.futures import Future

class TwitterPublisher(StreamListener):
    def __init__(self, project_id, topic_id):
        self.project_id = project_id
        self.topic_id = topic_id
        self.batch_settings = pubsub_v1.types.BatchSettings(max_messages = 100, max_bytes = 1024)
        self.publisher = pubsub_v1.PublisherClient(self.batch_settings)
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        self.publish_futures = []
        self.i = 0
        self.l = []

    #These are the listener methods for tweepy class
    def on_data(self, raw_data):
        '''
        This method streams the data collected from the Twitter via the Tweepy API
        :param raw_data:
        :return:
        '''
        json_data = json.loads(raw_data)
        extracted_data = {"id": json_data['id'], "text":json_data['text']}
        print(extracted_data)
        self.publish_to_topic(extracted_data)

    def on_error(self, status_code):
        if status_code == 420:
            return False
    def get_callback(self, publish_future, data):
        def callback(publish_future):
            try:
                    # Wait 60 seconds for the publish call to succeed.
                print(publish_future.result(timeout=60))
            except futures.TimeoutError:
                print(f"Publishing {data} timed out.")

        return callback

    def publish_to_topic(self, data):
        if self.i == 100:
            s_data = json.dumps(self.l)
            publish_future = self.publisher.publish(self.topic_path, data = s_data.encode('utf-8'))
            print(type(publish_future))
            publish_future.add_done_callback(self.get_callback(publish_future, data))
            self.publish_futures.append(publish_future)
            self.i = 0
            self.l = []
            return
        else:
            self.i += 1
            self.l.append(data)
            return



# Setting up the variables

ckey = "jqOVBR0ssy0F2q808tuL753qr"
csecret = "y6fyjKNPloSPdXWtZWiZniuaDMB8YeMyH1CGIkaveN2j6NeOig"
atoken = "1345873364561309697-rQNgI83Ui84KXUDUSvrpTq2sYFMt4h"
asecret = "qCrnuNfAaxOYoYGRLibYv7ksdGLivLwuyGqkGO4SV6ZNz"
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
project_id = sys.argv[1]
topic_id = sys.argv[2]
twitterStream = Stream(auth, TwitterPublisher(project_id, topic_id))
twitterStream.filter(track=["car"], languages=["en"])


