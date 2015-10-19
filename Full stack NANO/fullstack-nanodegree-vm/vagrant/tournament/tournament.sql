-- Table definitions for the tournament project.

-- setting up and connection to the database
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE "tournament";
\c tournament
--table for players
CREATE TABLE players(
	id SERIAL PRIMARY KEY,
	name VARCHAR
);
--table for matches
CREATE TABLE matches(
	id SERIAL PRIMARY KEY,
	winner_id INT REFERENCES players(id),
	loser_id INT REFERENCES players(id)
);

--view wih player id, name and wins
CREATE VIEW player_rank AS
	SELECT p.id, p.name, row_number() OVER (order by COUNT(m.winner_id) DESC) AS rank
	FROM players AS p
	LEFT JOIN matches AS m
	ON p.id = m.winner_id
	GROUP BY p.id;
	
--view wih player id, name and wins and total matches played
CREATE VIEW total_match_count AS
	SELECT p.id, COUNT(m) AS total_matches
	FROM players AS p JOIN matches AS m
	ON p.id = m.winner_id OR p.id = m.loser_id
	GROUP BY p.id;

