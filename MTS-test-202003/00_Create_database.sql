.open MTS-test-202003.db

CREATE TABLE location (
	id INTEGER PRIMARY KEY
	,name NVARCHAR(1000)
	,country_cd CHAR(2)
	,UNIQUE (name, country_cd)
);

CREATE TABLE tweet (
	id INTEGER PRIMARY KEY
	,created_at TIMESTAMP NOT NULL
	,name VARCHAR(15) NOT NULL
	,tweet_text NVARCHAR(280) NOT NULL
	,lang CHAR(2) NOT NULL
	,location_id INTEGER
	,tweet_sentiment FLOAT
	,FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE TABLE url (
	tweet_id INTEGER NOT NULL
	,display_url NVARCHAR(1000) NOT NULL
	,type_cd VARCHAR(32) NOT NULL
	,FOREIGN KEY (tweet_id) REFERENCES tweet(id)
	,UNIQUE(tweet_id, display_url)
);

.quit
