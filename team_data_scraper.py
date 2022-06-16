import re
import sys
import statsapi
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.disable(logging.INFO)
logging.debug('Start of team_data_scraper')


#try: teams_list = sys.argv[1] #this would allow easy segmenting of which cards to use (by division?  by league?  by team name? etc.)

team_IDs = [121, 133, 134]#, 135, 136,137,138,139,140,141,142,143,144,145,146,147,158,108,109,110,111,112,113,114,115,116,117,118,119,120] # moved Mets to the start :)

player_IDs = []

players_per_team_type = 9 #increase for more coverage, reduce for better speed

def getPlayerIDs():
    logging.debug("Creating list of players...")
    for i in team_IDs:
        logging.debug(f"team id {i}")
        # look up players_per_team_type number of hitters & pitchers per team
        hitters = statsapi.team_leaders(i,"gamesPlayed",limit=(players_per_team_type+1))
        pitchers = statsapi.team_leaders(i,"inningsPitched",limit=(players_per_team_type+1))

        # parse hitters using re
        # break out most of list, separated by number > space > newline > number > space
        hitters = re.split("\d{1,}\s{1,}\n\s{1,}\d{1,}\s{1,}",hitters)
        # break out first hitter, whose text includes some additional info at front that isn't parsed in the above
        hitter1 = re.split("1\s{1,}",hitters[0])[1]

        # remove first hitter's entry with all of the additional info; to be re-added later
        del hitters[0]

        # remove last hitter, whose entry includes extra information; this is why we add 1 to players_per_team_type above
        del hitters[-1]

        # add back first hitter
        hitters.append(hitter1)

        # parse pitchers using re - same as above
        pitchers = re.split("\d{1,}.\d\s{1,}\n\s{1,}\d{1,}\s{1,}",pitchers)
        pitcher1 = re.split("1\s{1,}",pitchers[0])[1]
        del pitchers[0]
        del pitchers[-1]
        pitchers.append(pitcher1)

        # confirm this is the correct instance of the hitter by checking team, then add
        #print(str(i)+"hitters loop")
        for j in hitters:
            # search by name, returning list of players who match name
            players = statsapi.lookup_player(j.rstrip())
            # confirm by checking team
            for player in players:
                if player["currentTeam"]["id"] == i and player["id"] not in player_IDs:
                    #add
                    player_IDs.append(player["id"])
        
        # same as above, for pitchers
        #print(str(i)+"pitchers loop")
        for j in pitchers:
            players = statsapi.lookup_player(j.rstrip())
            for player in players:
                if player["currentTeam"]["id"] == i and player["id"] not in player_IDs:
                    player_IDs.append(player["id"])
    return player_IDs