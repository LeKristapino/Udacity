-- Table definitions for the tournament project.
--

--table for players
create table players(
	id serial primary key,
	name varchar(100)
);
--table for matches
create table matches(
	winner_id int references players(id),
	loser_id int references players(id),
);

--view wih player id, name and wins
create view player_wins as
	SELECT p.id, p.name, count(m.winner_id) as wins
	FROM players as p
	LEFT JOIN matches as m
	ON p.id = m.winner_id
	group by p.id;
--view wih player id, name and wins and total matches played
create view total_match_count as
	select p.id, count(m) as total_matches
	from players as p join matches as m
	on p.id = m.winner_id or p.id = m.loser_id
	group by p.id;


