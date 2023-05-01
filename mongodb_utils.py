from pymongo import MongoClient
import pandas as pd
import secret_keys


class MyMongoDbUtils:
  def __init__(self):
    client = MongoClient(secret_keys.MONGO_PATH)
    self.db = client['academicworld']
    
  def get_publication_info(self, publication_id):
    result = self.db.publications.find_one({"id": publication_id})
    return result 