Title: Explore Keywords

Purpose: The application is designed to help students who are looking for Master/PhD programs to find a faculty that fits their interests and goals.

Demo: 


Installation:

1. Create secret_keys.py, which stores DB secrets
MONGO_PATH='mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb'

MYSQL_DB_HOST = 'localhost',
MYSQL_DB_USER = 'root',
MYSQL_DB_PASSWORD = '...',
MYSQL_DB_DATABASE = 'academicworld'

NEO4J_PATH = 'bolt://localhost:7687'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = '...'
NEO4J_DATABASE = 'academicworld'

2. Import datasets (data expension)
run `python3 import_university_map_data.py`

3. Add favorite_faculty table in MySQL db
CREATE TABLE favorite_faculty (
 	faculty_id int NOT NULL,
     comment text,
     deleted bool DEFAULT false,
     PRIMARY KEY(faculty_id)
  );

Usage:
1. Start the REST API server
run `python3 rest_api.py`

2. Start the Dash Plotly Web server
run `python3 app.py`

Design & Implementation:
+---------------------------------+
|             Frontend            |
|       (Dash Plotly app)         |
+---------------------------------+
              |-------------------------------------------------------------
              |                                                            |
              v                                                            v
+---------------------------------+                     +--------------------------------------+
|           Flask API             |                     |     Monogo | MySQL | Neo4j           |
|    (interacts with MySQL)       |                     |    (interacts with 3 databases)      |
+---------------------------------+                     +--------------------------------------+

The Dash Plotly app is responsible for user interface and handling user interactions. It is served by a Flask REST API, which interacts with a MYSQL database to retrieve data. It also interacts with 3 different databaes (MongoDB, MySQL, and Neo4j) to retrive, store, and update data.
My website contains three tabs, each of which is controlled by the same dropdown - keyword. The first tab includes a map of the top 15 universities as well as a table of their rankings. The second tab displays a table of the top 15 faculties and allows you to pick one to get more details. It also lets you mark facilities as favorites and make notes about them. The third page displays a table of the top 15 publications, with the option to pick one for further information.


Database Techniques:
1. Constraint
# add constraint to favorite_faculty's comment to prevent XSS attack
ALTER TABLE favorite_faculty ADD CONSTRAINT comment_check CHECK (comment NOT REGEXP '[<>\'\&"]');
# add constraint to faculty's name to make sure name is not null
ALTER TABLE faculty ADD constraint name_not_null CHECK (name IS NOT NULL);
# add constraint to faculty_keyword's score to make sure scoll is always present
ALTER TABLE faculty_keyword ADD constraint faculty_keyword_score_value_not_null CHECK (score IS NOT NULL);
# add constraint to keywrod's name to make sure name is always not null
ALTER TABLE keyword ADD constraint keyword_name_not_null CHECK (name IS NOT NULL);
# add constraint to university's name to make sure name is always not null
ALTER TABLE university ADD constraint university_name_not_null CHECK (name IS NOT NULL);
# add constraint to publication's title to make sure title is not null
ALTER TABLE publication ADD constraint publication_title_not_null CHECK (title IS NOT NULL);
# add constraint to publication's num_citations to make sure value is alwasys bigger or equal to 0
ALTER TABLE publication ADD constraint publication_num_citations_non_negative CHECK (num_citations >= 0);
# add constraint to publication_keyword's score to make sure score is always present
ALTER TABLE publication_keyword ADD constraint publication_keyword_score_not_null CHECK (score IS NOT NULL);

2. Added REST API for accessing MySQL DB
Added Flask REST API to allow us to pull faculty, publication and university data

3. Index
CREATE INDEX idx_faculty_name ON faculty(name);
CREATE INDEX idx_publication_title ON publication(title);
CREATE INDEX idx_university_name ON university(name);

4. Trigger
Added a trigger to delete corresponding records when delete a faculty

DELIMITER $$
CREATE TRIGGER delete_faculty_corresponding_records
AFTER DELETE ON faculty FOR EACH ROW
BEGIN
	DELETE FROM faculty_keyword 
		WHERE (faculty_keyword.faculty_id = OLD.id);
  DELETE FROM faculty_publication 
		WHERE faculty_publication.faculty_id = OLD.id;
  DELETE FROM favorite_faculty 
		WHERE favorite_faculty.faculty_id = OLD.id;
END$$
DELIMITER ;

Extra-Credit Capabilities:
1. Data Expansion
# Added the latitude and longitude of universities in Neo4j to enable their location on the map.

2. External Data sourcing:
# Utilized an external API to retrieve and display quotes every minute

3, Multi-database querying:
# Implmented a function to query from two databases. The function pulls university ids from MySQL db first, and then use the result to query university's location from Neo4j.

Contributions:
# I'm the only contributor and I've invested around 40 hours on this.