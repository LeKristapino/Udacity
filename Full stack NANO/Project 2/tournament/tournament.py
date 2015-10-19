#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("An error occured while trying to connect to the database")


def deleteMatches():
    """Remove all the match records from the database."""
    DB, c = connect()
    c.execute("TRUNCATE matches;")
    DB.commit()
    DB.close()

def deletePlayers():
    """Remove all the player records from the database."""
    DB , c= connect()
    c.execute("TRUNCATE players CASCADE;")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB, c = connect()
    c.execute("SELECT count(*) FROM players;")
    count = c.fetchall()
    DB.close()
    return count[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB, c = connect()
    c.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    DB.commit()
    DB.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB, c = connect()
    c.execute("""SELECT p.id, p.name, count(m.winner_id) as wins , count(tm.total_matches) as total_matches
                        FROM players as p
                        LEFT JOIN matches as m
                        ON p.id = m.winner_id
                        LEFT JOIN total_match_count as tm
                        ON p.id = tm.id
                        group by p.id
                        order by wins DESC;
                    """)
    output = c.fetchall()
    DB.close()
    return output


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB, c = connect()
    value = (winner, loser)
    c.execute("INSERT INTO matches  (winner_id, loser_id) VALUES %s", (value,))
    DB.commit()
    DB.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    DB, c = connect()
    c.execute(""" SELECT p.id, p.name, p2.id, p2.name
                        FROM player_rank as p
                        JOIN player_rank as p2
                        ON p.rank +1 = p2.rank
                        WHERE p.rank % 2 =1 ; 
                    """)
    pairings = c.fetchall()
    DB.close()

    return pairings


