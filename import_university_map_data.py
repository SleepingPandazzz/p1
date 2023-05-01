import csv
import secret_keys
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    secret_keys.NEO4J_PATH, auth=(secret_keys.NEO4J_USERNAME, secret_keys.NEO4J_PASSWORD), database=secret_keys.NEO4J_DATABASE)

with open('universities.csv', newline='') as csvfile:
    render = csv.DictReader(csvfile)
    for row in render:
        with driver.session() as session:
            result = session.run("MATCH (n:INSTITUTE {id: $id}) SET n.latitude = $latitude, n.longitude = $longitude",
                                 id="i" + row['university_id'],
                                 latitude=float(row['latitude']),
                                 longitude=float(row['longitude']))
