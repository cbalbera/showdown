import re
import sys
import statsapi
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.disable(logging.INFO)
logging.debug('Start of team_data_scraper')

#try: teams_list = sys.argv[1] #this would allow easy segmenting of which cards to use (by division?  by league?  by team name? etc.)
teams_list = {'Athletics': 133, "A's":133, 'As': 133,
'Pirates': 134,
'Padres': 135,
'Mariners': 136,
'Giants': 137,
'Cardinals': 138,
'Rays': 139,
'Rangers': 140,
'Blue Jays': 141,
'Twins': 142,
'Phillies': 143,
'Braves': 144,
'White Sox': 145,
'Marlins': 146,
'Yankees': 147,
'Brewers': 158,
'Angels': 108,
'D-backs': 109,'Diamondbacks': 109,
'Orioles': 110,
'Red Sox': 111,
'Cubs': 112,
'Reds': 113,
'Guardians': 114,
'Rockies': 115,
'Tigers': 116,
'Astros': 117,
'Royals': 118,
'Dodgers': 119,
'Nationals': 120,
'Mets': 121}

#for testing #team_IDs = [121, 133, 134]#, 135, 136,137,138,139,140,141,142,143,144,145,146,147,158,108,109,110,111,112,113,114,115,116,117,118,119,120] # moved Mets to the start :)

player_IDs = []

players_per_team_type = 12 #increase for more coverage, reduce for faster speed

#gets PlayerIDs for one Team
def getPlayerIDs(teamName, players_per_team = players_per_team_type):
    logging.debug("Creating list of players...")
    team_ID = teams_list[teamName]
    # look up players_per_team_type number of hitters & pitchers per team
    hitters = statsapi.team_leaders(team_ID,"gamesPlayed",limit=(players_per_team_type+1))
    pitchers = statsapi.team_leaders(team_ID,"inningsPitched",limit=(players_per_team_type+1))

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
    #print("hitters loop")
    for j in hitters:
        # search by name, returning list of players who match name
        players = statsapi.lookup_player(j.rstrip())
        # confirm by checking team
        for player in players:
            if player["currentTeam"]["id"] == team_ID and player["id"] not in player_IDs:
                #add
                player_IDs.append(player["id"])
    
    # same as above, for pitchers
    #print(str(i)+"pitchers loop")
    for j in pitchers:
        players = statsapi.lookup_player(j.rstrip())
        for player in players:
            if player["currentTeam"]["id"] == team_ID and player["id"] not in player_IDs:
                player_IDs.append(player["id"])
    return player_IDs