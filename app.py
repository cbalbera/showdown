from flask import Flask, render_template, request#, redirect, session
#import werkzeug
import play_showdown
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from random import randint

app = Flask(__name__) # __name__ refers to name of this file

TEAMS = ['Mets','Athletics', 'Pirates', 'Padres', 'Mariners', 'Giants', 'Cardinals', 'Rays', 'Rangers', 'Blue Jays', 'Twins', 'Phillies', 'Braves', 'White Sox', 'Marlins', 'Yankees', 'Brewers', 'Angels', 'Diamondbacks', 'Orioles', 'Red Sox', 'Cubs', 'Reds', 'Guardians', 'Rockies', 'Tigers', 'Astros', 'Royals', 'Dodgers', 'Nationals']
POSITIONS = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]

db_name = "showdown"
db_pwd = os.environ["PSQL_DB_PASSWORD"]
showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
showdown_cursor = showdown_connection.cursor(cursor_factory=RealDictCursor)
id = randint(1,100000) #ID of this game - to update methodology for storing game lineup data & other data

print("made it to routes")
@app.route("/")
def home():
    return render_template("home.html")

print("made it to setup route")
@app.route("/set_up_teams",methods=["GET","POST"]) #this may need to be two methods
def set_up_teams():
    #if request.method == "POST":
     #   return redirect("new_game.html")
    return render_template("set_up_teams.html",positions=POSITIONS, teams=TEAMS)

print("made it to newgame route")
@app.route("/new_game",methods=["GET","POST"])
def new_game():
    formdata = request.form
    showdown_team_away=""
    showdown_team_home=""
    innings = "1"
    # array: format [positions], [player names], [teams]
    showdown_team_array_away = [["SP"],[],[]]
    showdown_team_array_home = [["SP"],[],[]]

    for key in formdata.keys():
        for value in formdata.getlist(key):
            if key == 'team_a':
                showdown_team_array_away[2].append(value)
            elif key == 'position_a':
                showdown_team_array_away[0].append(value)
            elif key == 'startername_a':
                showdown_team_array_away[1].append(value)
            elif key == 'playername_a':
                showdown_team_array_away[1].append(value)
            elif key == 'team_h':
                showdown_team_array_home[2].append(value)
            elif key == 'position_h':
                showdown_team_array_home[0].append(value)
            elif key == 'startername_h':
                showdown_team_array_home[1].append(value)
            elif key == 'playername_h':
                showdown_team_array_home[1].append(value)
            else: #key == 'innings'
                innings = int(innings)

    # add represented teams to list
    teams_list = []
    teams_list_final = ""
    for team in showdown_team_array_away[2]:
        if team not in teams_list:
            teams_list.append(team)
            #for future use in team_data_scraper, player_data_scraper
    
    occupiedPositions = []
    #validate and transpose submissions
    for i in range(0,10):
        if not showdown_team_array_away[0][i] in TEAMS or not showdown_team_array_away[1][i] or not showdown_team_array_away[2][i] in POSITIONS:
            pass#return render_template("home.html") #return failure template and/or, redirect
        # if multiple players in one position (ideally check this on HTML frontend going fwd)
        if  showdown_team_array_away[2][i] in occupiedPositions:
            pass#return render_template("home.html") #return failure template and/or, redirect
        showdown_team_away = showdown_team_away+showdown_team_array_away[0][i]+", "+showdown_team_array_away[1][i]+" "+showdown_team_array_away[2][i]
        occupiedPositions.append(showdown_team_array_away[2][i])
        if i < 9:
            showdown_team_away = showdown_team_away+", "
    
    print (showdown_team_away)

    # home team

    # add represented teams to list
    for team in showdown_team_array_home[2]:
        if team not in teams_list:
            teams_list.append(team)
            #for future use in team_data_scraper, player_data_scraper

    # convert into string so postgres can handle
    for team in teams_list:
        teams_list_final += team + (", ")
    teams_list_final = teams_list_final[:-2]
    print(teams_list_final)
    
    occupiedPositions = []
    #validate and transpose submissions
    for i in range(0,10):
        if not showdown_team_array_home[0][i] in TEAMS or not showdown_team_array_home[1][i] or not showdown_team_array_home[2][i] in POSITIONS:
            pass#return render_template("home.html") #return failure template and/or, redirect
        # if multiple players in one position (ideally check this on HTML frontend going fwd)
        if  showdown_team_array_home[2][i] in occupiedPositions:
            pass#return render_template("home.html") #return failure template and/or, redirect
        showdown_team_home = showdown_team_home+showdown_team_array_home[0][i]+", "+showdown_team_array_home[1][i]+" "+showdown_team_array_home[2][i]
        occupiedPositions.append(showdown_team_array_home[2][i])
        if i < 9:
            showdown_team_home = showdown_team_home+", "
    
    print (showdown_team_home)
    
    # add both teams to cursor
    showdown_cursor.execute(f"INSERT INTO teamtext VALUES({id},'{teams_list_final}',{innings},'{showdown_team_away}','{showdown_team_home}')")
    showdown_connection.commit()

    #play_showdown.get_cards(teams_list)

    #play_showdown.playBall(home=showdown_team_home,away=showdown_team_away,inning_count=innings)
    return render_template("new_game.html")

print("made it to playball route")
@app.route("/play_ball",methods=["GET","POST"])
def play_ball():
    
    showdown_cursor.execute(f"SELECT teams_list FROM teamtext WHERE id={id}")
    teams_list = showdown_cursor.fetchone()[0]
    play_showdown.get_cards(teams_list)
    showdown_cursor.execute(f"SELECT innings FROM teamtext WHERE id={id}")
    innings = int(showdown_cursor.fetchone()[0])
    showdown_cursor.execute(f"SELECT away_team FROM teamtext WHERE id={id}")
    away_team = showdown_cursor.fetchone()[0]
    showdown_cursor.execute(f"SELECT home_team FROM teamtext WHERE id={id}")
    home_team = showdown_cursor.fetchone()[0]
    play_showdown.playBall(home=home_team,away=away_team,inning_count=innings)

    return render_template("play_ball.html")

showdown_connection.close()
print("made it to end, what's up?")

#app.run(debug=True, host="0.0.0.0", port=5000)

"""TEAMS = ["Arizona Diamondbacks",
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

DROPDOWN_OPTIONS = ["NL East", "NL Central", "NL West", "AL East", "AL Central", "AL West", "AL", "NL", "MLB"]"""