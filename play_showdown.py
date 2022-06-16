import player_data_scraper
import Gameplay2

"""
teams = input("Which teams would you like to play with? Please place the home team first & separate with commas.")

teams_list = teams.split(teams,",")
"""
#check there are two teams

#otherwise, re-input/reject

"""for team in teams_list:
    # pulls all new data, updating cards where necessary
    player_data_scraper.getPlayerData(team)
    #create cards from data

    #prompt to create lineup from cards"""

player_data_scraper.scrape_data()

Gameplay2.Gameplay(homeTeam="testLineup.txt",awayTeam="testLineup.txt",innings=3)
''' start! This calls the initializer.  What should happen now:

1. The players are prompted to input how many innings they will play.
2. The home team is prompted to add its lineup (see ShowdownTeam2.py for details).
3. The away team is prompted to add its lineup.
4. The scoreboard is set to 0-0 in the top of the 1st inning with 0 outs.
5. The first batter is set to be due up next for each team.

'''