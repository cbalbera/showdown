import statsapi
import psycopg2
from math import floor
from psycopg2.extras import RealDictCursor
import sys
import team_data_scraper
from clear_postgres import clear
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.disable(logging.INFO)
logging.debug('Start of player_data_scraper')

db_name = "postgres" #input("What is your database name?")
try: db_pwd = sys.argv[1]
except: db_pwd = input("What is your database password?")
showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
showdown_cursor = showdown_connection.cursor(cursor_factory=RealDictCursor)
if len(sys.argv) == 3: 
    if sys.argv[2].lower() == "clear":
        clear(showdown_cursor,showdown_connection)
logging.debug("creating tables")
try: showdown_cursor.execute("CREATE TABLE pitcher_stats (id int PRIMARY KEY, team text, firstname text, lastname text, position text, throws char, bats char,inningspitched int,abs_against int, strikeouts int, groundouts int, flyouts int, walks int, hits int, non_hr_xbh int, home_runs int, games int, starts int, earned_runs int, save_chances int) ")
except psycopg2.ProgrammingError: 
    showdown_cursor.execute("ROLLBACK")
    showdown_connection.commit()
try: showdown_cursor.execute("CREATE TABLE hitter_stats (id int PRIMARY KEY, team text, firstname text, lastname text, position text, throws char, bats char,at_bats int, strikeouts int, groundouts int, flyouts int, walks int, hits int, doubles int, triples int, home_runs int, sb_attempts int, sb_percentage text, field_percentage text, range_factor text) ")
except psycopg2.ProgrammingError: 
    showdown_cursor.execute("ROLLBACK")
    showdown_connection.commit()

TEAMS = ["Arizona Diamondbacks",
"Atlanta Braves",
"Baltimore Orioles",
"Boston Red Sox",
"Chicago White Sox",
"Chicago Cubs",
"Cincinnati Reds",
"Cleveland Guardians",
"Colorado Rockies",
"Detroit Tigers",
"Houston Astros",
"Kansas City Royals",
"Los Angeles Angels",
"Los Angeles Dodgers",
"Miami Marlins",
"Milwaukee Brewers",
"Minnesota Twins",
"New York Yankees",
"New York Mets",
"Oakland Athletics",
"Philadelphia Phillies",
"Pittsburgh Pirates",
"San Diego Padres",
"San Francisco Giants",
"Seattle Mariners",
"St. Louis Cardinals",
"Tampa Bay Rays",
"Texas Rangers",
"Toronto Blue Jays",
"Washington Nationals"]

#testIDs = [605135,471911,621242,607625,493603,656849,592741,592836,621512,605204,592192,656941,572287,624413,500871,641645,643446,596019,516782,607043,592450,670541,502671,608070,669203,543037,663556,605397,571578,608566,518735,595879,600869,453286,645261]
logging.debug("before calling getPlayerIDs")

# gets player data, with primary key ID (from mlb stats API), for all players on teams listed in teams_list
def getPlayerData(team):
    player_IDs = team_data_scraper.getPlayerIDs(team)

    print("Preparing list of players for processing...")

    for i in player_IDs: #range(600303,625000): #reduced for testing
        try: player_stats = statsapi.player_stat_data(i)
        except: continue
        #if not player_stats["active"]: continue
        #print("id is "+str(i)+" and player is "+player_stats["first_name"] +" "+player_stats["last_name"])
        team = player_stats["current_team"]
        #if not team in TEAMS: continue #exclude MiLB, sorry guys
        if player_stats["stats"] == []: continue #exclude no MLB stats

        # set basics
        id = player_stats["id"]
        first_name = player_stats["first_name"].replace("'","")
        last_name = player_stats["last_name"].replace("'","")
        pos = player_stats["position"]
        pitch_hand = player_stats["pitch_hand"][0]
        bat_side = player_stats["bat_side"][0]

        # naive handling of some edge cases that may exist
        if pos == "IF": pos = "2B"
        if pos == "OF": pos = "CF"

        # pitchers - set placeholders for loop usage
        if pos == "P":
            inningspitched = 0
            abs_against = 0
            strikeouts = 0
            groundouts = 0
            flyouts = 0
            walks = 0
            hits = 0
            non_hr_xbh = 0
            home_runs = 0
            games = 0
            starts = 0
            earned_runs = 0
            save_chances = 0

            # loop to set all stat values
            for j in player_stats["stats"]:
                #print("adding a pitcher")
                if j["group"] == "pitching":
                    inningspitched = floor(j["stats"]["outs"] / 3)
                    abs_against = j["stats"]["atBats"]
                    strikeouts = j["stats"]["strikeOuts"]
                    groundouts = j["stats"]["groundOuts"]
                    flyouts = j["stats"]["airOuts"]
                    walks = j["stats"]["baseOnBalls"] + j["stats"]["hitByPitch"]
                    hits = j["stats"]["hits"]
                    non_hr_xbh = j["stats"]["doubles"] + j["stats"]["triples"]
                    home_runs = j["stats"]["homeRuns"]
                    games = j["stats"]["gamesPlayed"]
                    starts = j["stats"]["gamesStarted"]
                    earned_runs = j["stats"]["earnedRuns"]
                    save_chances = j["stats"]["saveOpportunities"]
            
            # pitcher type setting
            if games < starts * 1.2:
                pos = "SP"
            else:
                if save_chances > 5:
                    pos = "CP"
                else:
                    pos = "RP"
            
            # add to DB
            try: 
                print(f"adding {first_name} {last_name}")
                showdown_cursor.execute(f"INSERT INTO pitcher_stats (id, team, firstname, lastname, position, throws, bats,inningspitched,abs_against, strikeouts, groundouts, flyouts, walks, hits, non_hr_xbh, home_runs, games, starts, earned_runs, save_chances) VALUES({id}, '{team}','{first_name}','{last_name}','{pos}','{pitch_hand}','{bat_side}',{inningspitched},{abs_against},{strikeouts}, {groundouts}, {flyouts}, {walks}, {hits}, {non_hr_xbh}, {home_runs}, {games}, {starts}, {earned_runs}, {save_chances})") # add to SQL database
            except psycopg2.IntegrityError:
                # roll back failure
                showdown_cursor.execute("ROLLBACK")
                # commit rollback
                showdown_connection.commit()
                # remove existing data
                showdown_cursor.execute(f"DELETE FROM pitcher_stats WHERE id = {id}")
                # commit remove
                showdown_connection.commit()
                # now, add player  
                showdown_cursor.execute(f"INSERT INTO pitcher_stats (id, team, firstname, lastname, position, throws, bats,inningspitched,abs_against, strikeouts, groundouts, flyouts, walks, hits, non_hr_xbh, home_runs, games, starts, earned_runs, save_chances) VALUES({id}, '{team}','{first_name}','{last_name}','{pos}','{pitch_hand}','{bat_side}',{inningspitched},{abs_against},{strikeouts}, {groundouts}, {flyouts}, {walks}, {hits}, {non_hr_xbh}, {home_runs}, {games}, {starts}, {earned_runs}, {save_chances})") # add to SQL database

        else: #non-pitchers - need hitting and primary fielding
            # set placeholders for hitter loop usage
            at_bats = 0
            strikeouts = 0
            groundouts = 0
            flyouts = 0
            walks = 0
            hits = 0
            doubles = 0
            triples = 0
            home_runs = 0
            sb_attempts = 0
            sb_percentage = 0
            field_percentage = 0
            range_factor = 0

            # loop to set all stat values
            for j in player_stats["stats"]:
                #print("adding a hitter")

                # hitting stats
                if j["group"] == "hitting":
                    at_bats = j["stats"]["atBats"]
                    strikeouts = j["stats"]["strikeOuts"]
                    groundouts = j["stats"]["groundOuts"]
                    flyouts = j["stats"]["airOuts"]
                    walks = j["stats"]["baseOnBalls"] + j["stats"]["hitByPitch"]
                    hits = j["stats"]["hits"]
                    doubles = j["stats"]["doubles"]
                    triples = j["stats"]["triples"]
                    home_runs = j["stats"]["homeRuns"]
                    sb_attempts = j["stats"]["stolenBases"] + j["stats"]["caughtStealing"]
                    sb_percentage = j["stats"]["stolenBasePercentage"]
                
                # fielding stats for main position - will eventually consider having a 2nd position
                elif j["group"] == "fielding" and field_percentage != 0:
                    field_percentage = j["stats"]["fielding"]
                    range_factor = j["stats"]["rangeFactorPer9Inn"]
            
            # add to DB
            try: 
                print(f"adding {first_name} {last_name}")
                showdown_cursor.execute(f"INSERT INTO hitter_stats VALUES({id},'{team}','{first_name}','{last_name}','{pos}','{pitch_hand}','{bat_side}',{at_bats},{strikeouts}, {groundouts}, {flyouts}, {walks}, {hits}, {doubles},{triples},{home_runs}, {sb_attempts}, '{sb_percentage}', '{field_percentage}', '{range_factor}')") # add to SQL database
            except psycopg2.IntegrityError:
                # roll back failure
                showdown_cursor.execute("ROLLBACK")
                # commit rollback
                showdown_connection.commit()
                # remove existing data
                showdown_cursor.execute(f"DELETE FROM hitter_stats WHERE id = {id}")
                # commit remove
                showdown_connection.commit()
                # now, add player
                showdown_cursor.execute(f"INSERT INTO hitter_stats VALUES({id},'{team}','{first_name}','{last_name}','{pos}','{pitch_hand}','{bat_side}',{at_bats},{strikeouts}, {groundouts}, {flyouts}, {walks}, {hits}, {doubles},{triples},{home_runs}, {sb_attempts}, '{sb_percentage}', '{field_percentage}', '{range_factor}')") # add to SQL database
        # commit this player to DB
        showdown_connection.commit()