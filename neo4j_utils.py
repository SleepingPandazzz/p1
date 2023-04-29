from neo4j import GraphDatabase

class Neo4jDbUtils:
  def __init__(self):
    self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "HelloWorld123!"), database="academicworld")