print("importing play")
import team_data_scraper
print("Imported team,trying player")
import player_data_scraper
print("imported player, trying gameplay")
import Gameplay_forweb

print("imported modules")

def get_cards(teams):
    # create list of player IDs
    ids = team_data_scraper.getPlayerIDs(teams)
    print("done scraping team data")
    # push player data to postgres
    player_data_scraper.scrape_data(ids)
    print("player data scraped")

def playBall(home,away,inning_count):
    print("about to call Gameplay")
    Gameplay_forweb.Gameplay(homeTeam=home,awayTeam=away,innings=inning_count)

print("all imported in play")
''' start! This calls the initializer.  What should happen now:

1. The players are prompted to input how many innings they will play.
2. The home team is prompted to add its lineup (see ShowdownTeam2.py for details).
3. The away team is prompted to add its lineup.
4. The scoreboard is set to 0-0 in the top of the 1st inning with 0 outs.
5. The first batter is set to be due up next for each team.

'''