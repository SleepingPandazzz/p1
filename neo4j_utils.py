from neo4j import GraphDatabase
import pandas as pd
import mysql_utils
import university
import secret_keys

class Neo4jDbUtils:
  def __init__(self):
    self.mysql = mysql_utils.MysqlUtils()
    self.driver = GraphDatabase.driver(secret_keys.NEO4J_PATH, 
                                       auth=(secret_keys.NEO4J_USERNAME, secret_keys.NEO4J_PASSWORD), 
                                       database=secret_keys.NEO4J_DATABASE)
    self.university = university.University()

  def get_keywords(self):
    with self.driver.session() as session:
      results = session.run(
          "MATCH (k:KEYWORD) RETURN k.name AS name ORDER BY k.name")
      data = results.data()
      keywords = []
      for (keyword) in data:
        keywords.append(keyword.get('name').title())
    return keywords
  
  def filter_university_map(self, keyword):
    university_ids = self.university.get_university_ids_by_keyword(keyword, 1)
    with self.driver.session() as session:
      results = session.run(
        "MATCH(i:INSTITUTE) WHERE i.id IN $university_ids RETURN i.id AS university_id, i.latitude AS latitude, i.longitude AS longitude, i.name AS name", university_ids=university_ids
      )
      data = results.data()
    df = pd.DataFrame([dict(record) for record in data])
    return df