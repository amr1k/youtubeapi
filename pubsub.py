from google.cloud import pubsub_v1
import json

class Publish:  

  def __init__(self, project_id, topic_id):
    self.topic_path = "projects/"+project_id+"/topics/"+topic_id
    self.publisher = pubsub_v1.PublisherClient()
    print('Publish class init')

  def publish(self, apiResponse):
    data = json.dumps(apiResponse).encode('utf-8')
    future = self.publisher.publish(self.topic_path, data)
    print(f'Message Published {future.result()}')