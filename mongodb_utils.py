from pymongo import MongoClient


class MyMongoDbUtils:
  def __init__(self):
    client = MongoClient(
        'mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb')
    self.db = client['academicworld']

    def get(self, collection_name, query):
      collection = self.db[collection_name]
      documents = collection.find(query)