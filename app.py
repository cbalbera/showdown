from flask import Flask, render_template, g, request#, redirect, session
#import werkzeug
import play_showdown
import psycopg2
from psycopg2 import pool # https://stackoverflow.com/questions/54638374/psycopg2-flask-tying-connection-to-before-request-teardown-appcontext
import os
from psycopg2.extras import RealDictCursor
from random import randint

app = Flask(__name__) # __name__ refers to name of this file

TEAMS = ['Mets','Athletics', 'Pirates', 'Padres', 'Mariners', 'Giants', 'Cardinals', 'Rays', 'Rangers', 'Blue Jays', 'Twins', 'Phillies', 'Braves', 'White Sox', 'Marlins', 'Yankees', 'Brewers', 'Angels', 'Diamondbacks', 'Orioles', 'Red Sox', 'Cubs', 'Reds', 'Guardians', 'Rockies', 'Tigers', 'Astros', 'Royals', 'Dodgers', 'Nationals']
POSITIONS = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]

db_name = "showdown"
db_pwd = os.environ["PSQL_DB_PASSWORD"]
#showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
#showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=localhost password={db_pwd}")
#showdown_cursor = showdown_connection.cursor(cursor_factory=RealDictCursor)

postgres_pool = psycopg2.pool.SimpleConnectionPool(1,10,user='postgres',password=db_pwd,host='localhost',port='5432',database=db_name)

def get_db():
    if 'db' not in g:
        g.db = postgres_pool.getconn()
    return g.db

@app.teardown_appcontext
def close_conn(e):
    db = g.pop('db', None)
    if db is not None:
        postgres_pool.putconn(db)

id = randint(1,100000) #ID of this game - to update methodology for storing game lineup data & other data

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/set_up_teams",methods=["GET","POST"]) #this may need to be two methods
def set_up_teams():
    #if request.method == "POST":
     #   return redirect("new_game.html")
    return render_template("set_up_teams.html",positions=POSITIONS, teams=TEAMS)

@app.route("/new_game",methods=["GET","POST"])
def new_game():
    formdata = request.form
    showdown_team_away=""
    showdown_team_home=""
    innings = 6
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
            elif key == 'innings':
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
    
    # for test purposes
    showdown_team_away = "SP, Carlos Carrasco Mets, 1B, Pete Alonso Mets, 2B, Jeff McNeil Mets, SS, Francisco Lindor Mets, 3B, Eduardo Escobar Mets, LF, Mark Canha Mets, CF, Brandon Nimmo Mets, RF, Starling Marte Mets, DH, Luis Guillorme Mets, C, Willson Contreras Cubs"

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

    # for test purposes
    teams_list_final = "Mets, Cubs"

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
    
    # for test purposes
    showdown_team_home = "SP, David Peterson Mets, 1B, Pete Alonso Mets, 2B, Jeff McNeil Mets, SS, lindor Mets, 3B, escobar Mets, LF, canha Mets, CF, nimmo Mets, RF, marte Mets, DH, guillorme Mets, C, contreras Cubs"

    print (showdown_team_home)

    #print("getting db connect")
    db = get_db()
    #print("getting cursor")
    showdown_cursor = db.cursor()
    #print("before insert into cursor")
    showdown_cursor.execute(f"INSERT INTO teamtext VALUES({id},'{teams_list_final}',{innings},'{showdown_team_away}','{showdown_team_home}')")
    #print("added to cursor - tbd if this works (previously had committed via connection, not db)")
    db.commit()
    #print("committed")
    #print("getting teams list")
    #play_showdown.get_cards(teams_list)

    #play_showdown.playBall(home=showdown_team_home,away=showdown_team_away,inning_count=innings)
    return render_template("new_game.html")

#print("made it to playball route")
@app.route("/play_ball",methods=["GET","POST"])
def play_ball():
    print("getting db connect")
    db = get_db()
    print("getting cursor")
    showdown_cursor = db.cursor()
    print("before insert into cursor")
    print(f"query is: SELECT * FROM teamtext WHERE id={id}")
    showdown_cursor.execute(f"SELECT * FROM teamtext WHERE id={id}")
    print("first select successful")
    data = showdown_cursor.fetchall()
    showdown_cursor.close()
    print(data)
    teams_list = data[0][1]
    print(f"about to call get_cards for teams {teams_list}")
    #play_showdown.get_cards(teams_list)
    innings = data[0][2]
    away_team = data[0][3]
    home_team = data[0][4]
    """print("getting innings")
    showdown_cursor.execute(f"SELECT innings FROM teamtext WHERE id={id}")
    innings = int(showdown_cursor.fetchone()[0])
    print("getting away_team lineup")
    showdown_cursor.execute(f"SELECT away_team FROM teamtext WHERE id={id}")
    away_team = showdown_cursor.fetchone()[0]
    print("getting home_team lineup")
    showdown_cursor.execute(f"SELECT home_team FROM teamtext WHERE id={id}")
    home_team = showdown_cursor.fetchone()[0]
    print("calling playBall")"""
    play_showdown.playBall(home=home_team,away=away_team,inning_count=innings)

    return render_template("play_ball.html")

#showdown_connection.close()
#print("made it to end")

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