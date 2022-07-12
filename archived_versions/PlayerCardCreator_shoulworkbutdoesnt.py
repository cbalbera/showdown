# module for creating PlayerCards from mlb player data
# while this module is in Python, my goal is to store in SQL for faster access

import psycopg2
import math
import PlayerCard2
from psycopg2.extras import RealDictCursor
import sys
import player_data_scraper


db_name = "postgres" #input("What is your database name?")
try: 
    db_pwd = sys.argv[-1]
    showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
except: 
    db_pwd = input("What is your database password?")
    showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
showdown_cursor = showdown_connection.cursor(cursor_factory=RealDictCursor)

#create cards tables - id primary key is one-to-one with id primary key in stats table, so using same value
try: showdown_cursor.execute("CREATE TABLE hitter_cards (id int PRIMARY KEY, team text, firstname text, lastname text, pointvalue int, position1 text, onbase int, speed int, outso int, outgb int, outfb int, bb int, single int, single_plus int, double int, triple int, home_run int, fielding1 int)")
except psycopg2.ProgrammingError: 
    showdown_cursor.execute("ROLLBACK")
    showdown_connection.commit()

try: showdown_cursor.execute("CREATE TABLE pitcher_cards (id int PRIMARY KEY, team text, firstname text, lastname text, pointvalue int, position1 text, control int, ip int, outpu int, outso int, outgb int, outfb int, bb int, single int, double int, home_run int)")
except psycopg2.ProgrammingError: 
    showdown_cursor.execute("ROLLBACK")
    showdown_connection.commit()

# pitcher cards
def createCards():

    #refresh to ensure fresh cursor
    showdown_cursor.execute("ROLLBACK")
    print("rolled back")
    showdown_connection.commit()
    print("committed rollback")
    showdown_cursor.execute("SELECT * FROM pitcher_stats") #WHERE team like 'New York Mets'") # use Mets only for testing
    print("selected stats")

    for i in showdown_cursor: #iterable!
        # transform data into showdown cards!
        # from pitcher init, need: (nameFirst,nameLast,PointValue,Position,Control,IP,OutPU,OutSO,OutGB,OutFB,BB,single,double,homerun)

        # easy ones
        nameFirst = i["firstname"]
        nameLast = i["lastname"]

        Position = i["position"]
        
        # total outs: generally 18+ for stars, 16-17 for great pitchers

        #print(f"{nameFirst} {nameLast}")
        # Total Pitcher Outs
        sumPitcherOuts = i["strikeouts"]+i["groundouts"]+i["flyouts"]
        #print(f"sumPitcherOuts is {sumPitcherOuts}")
        # % of at-bats resulting in outs, adjusted for 20-sided die AND increased 5% (via *21) to account for
        # fact that most pitchers need to have little double and no home run on their advantage to balance
        #print(f"player name is {nameFirst} {nameLast}")
        TotalPitcherOuts = round((sumPitcherOuts/i["abs_against"])*21)
        #print(f"TotalPitcherOuts is {TotalPitcherOuts}")

        # OutPU - the data set doesn't really provide this, so I am not going to set this for now
        OutPU = 0

        # OutSO
        OutSO = round((i["strikeouts"]/sumPitcherOuts)*TotalPitcherOuts)
        #print(f"i[strikeouts] is {i['strikeouts']}")
        #print(f"OutSo is {OutSO}")

        # OutGB
        OutGB = round((i["groundouts"]/sumPitcherOuts)*TotalPitcherOuts)
        #print(f"OutGB is {OutGB}")

        # OutFB
        OutFB = round((i["flyouts"]/sumPitcherOuts)*TotalPitcherOuts)
        #print(f"OutFB is {OutFB}")

        if (OutSO + OutGB + OutFB) > TotalPitcherOuts:
            #print(f"unbalance - more individual outs {(OutSO + OutGB + OutFB)} than total outs {TotalPitcherOuts}")
            if OutSO <= max(OutGB, OutFB):
                OutSO -= 1
                #print(f"reduced SO to {OutSO}")
            elif OutGB <= max(OutSO, OutFB):
                OutGB -= 1
                #print(f"reduced GB to {OutGB}")
            else:
                OutFB -= 1
                #print(f"reduced FB to {OutFB}")
        elif (OutSO + OutGB + OutFB) < TotalPitcherOuts:
            #print(f"unbalance - fewer individual outs {(OutSO + OutGB + OutFB)} than total outs {TotalPitcherOuts}")
            if OutSO >= max(OutGB, OutFB):
                OutSO += 1
                #print(f"increased SO to {OutSO}")
            elif OutGB >= max(OutSO, OutFB):
                OutGB += 1
                #print(f"increased GB to {OutGB}")
            else:
                OutFB += 1
                #print(f"increased FB to {OutFB}")

        # BB
        BB = round(i["walks"]/(i["walks"]+i["hits"])*(20-TotalPitcherOuts))
        #print(f"BB is {BB}")

        # Single
        single = round((i["hits"]-i["non_hr_xbh"]-i["home_runs"])/(i["walks"]+i["hits"])*(20-TotalPitcherOuts))
        #print(f"single is {single}")

        # Double
        double = round(i["non_hr_xbh"]/(i["walks"]+i["hits"])*(20-TotalPitcherOuts))
        #print(f"double is {double}")

        # Home Run
        home_run = round(i["home_runs"]/(i["walks"]+i["hits"])*(20-TotalPitcherOuts))
        #print(f"home_run is {home_run}")

        TotalOfOutcomes = OutPU + OutSO + OutGB + OutFB + BB + single + double + home_run
        #print(f"total of outcomes is {TotalOfOutcomes}")
        if not TotalOfOutcomes == 20:
            while TotalOfOutcomes > 20:
                if single > BB:
                    BB -= 1
                    TotalOfOutcomes -=1
                else:
                    single -= 1
                    TotalOfOutcomes -=1
            while TotalOfOutcomes < 20:
                if single > BB:
                    single -= 1
                    TotalOfOutcomes +=1
                else:
                    single += 1
                    TotalOfOutcomes +=1
                

        # Control - number 1 through 6, generally 5+ for great control, 3-4 for average, 2 for below average, 1 for well below average
        # s/o to Fangraphs (https://library.fangraphs.com/pitching/rate-stats/) among others for help here
        Control = 3 #base
        k_9 = (i["strikeouts"]/i["inningspitched"])*9
        bb_9 = (i["walks"]/i["inningspitched"])*9
        #k_bb = i["strikeouts"]/i["walks"]
        if k_9 > 10:
            Control += 2
        elif k_9 > 9:
            Control += 1.4
        elif k_9 > 8:
            Control += 1
        elif k_9 < 7:
            Control -= 1
        elif k_9 < 6:
            Control -= 1.4
        elif k_9 < 5:
            Control -= 2
        
        if bb_9 < 1.5:
            Control += 2
        elif bb_9 < 2:
            Control += 1.4
        elif bb_9 < 2.5:
            Control += 1
        elif bb_9 > 3.2:
            Control -= 1
        elif bb_9 > 3.5:
            Control -= 1.4
        elif bb_9 > 4:
            Control -= 2
        
        Control = min(max(round(Control),1),6)
        #print(f"control is {Control}")

        # IP
        IP = round(i["inningspitched"]/i["games"])
        if IP < 3 and Control >= 1 and Control < 4:
            IP -= 1
        IP = max(1,IP)
        #print(f"IP is {IP}")

        # PointValue - last
        PointValue = 200
        if TotalPitcherOuts > 15:
            PointValue += 50*(TotalPitcherOuts % 15)
        else:
            PointValue -= 50*(15 % TotalPitcherOuts)
        if Control > 3:
            PointValue += 75*(Control % 3)
        else:
            PointValue -= 75*(3 % Control)
        """
        print(f"Control is {Control}")
        print(f"IP is {IP}")
        print(f"total outs is {OutSO + OutGB + OutFB}")
        print(f"OutSO is {OutSO}")
        print(f"OutGB is {OutGB}")
        print(f"OutFB is {OutFB}")
        print(f"BB is {BB}")
        print(f"single is {single}")
        print(f"double is {double}")
        print(f"home_run is {home_run}")
        print(f"total of outcomes is {TotalOfOutcomes}")
        """
        team = i["team"].split(" ")[-1]

        # add card to SQL database
        try: 
            showdown_cursor.execute(f"INSERT INTO pitcher_cards VALUES({i['id']},'{team}','{nameFirst}','{nameLast}',{PointValue},'{Position}',{Control},{IP},{OutPU},{OutSO},{OutGB},{OutFB},{BB},{single},{double},{home_run})")
        except psycopg2.IntegrityError:
            # roll back failure
            showdown_cursor.execute("ROLLBACK")
            # commit rollback
            showdown_connection.commit()
            # remove existing data
            showdown_cursor.execute(f"DELETE FROM pitcher_cards WHERE id = {i['id']}")
            # commit remove
            showdown_connection.commit()
            # now, add player
            showdown_cursor.execute(f"INSERT INTO pitcher_cards VALUES({i['id']},'{team}','{nameFirst}','{nameLast}',{PointValue},'{Position}',{Control},{IP},{OutPU},{OutSO},{OutGB},{OutFB},{BB},{single},{double},{home_run})")
        showdown_connection.commit()

    # hitter cards
    showdown_cursor.execute("SELECT * FROM hitter_stats")# WHERE team like 'New York Mets'")
    for i in showdown_cursor:
        # transform data into showdown cards!
        # from hitter init, need: (nameFirst,nameLast,PointValue,Position1,OnBase,Speed,OutSO,OutGB,OutFB,BB,single,single_plus,double,triple,homerun,Fielding1 = -1):

        # easy ones
        nameFirst = i["firstname"]
        nameLast = i["lastname"]
        Position1 = i["position"]

        #print(f"{nameFirst} {nameLast}")

        # Speed
        Speed = 10
        triples_ratio = i["triples"] / i["at_bats"]
        if triples_ratio  > 0.015:
            Speed += 4
        elif triples_ratio > 0.0075:
            Speed += 2
        sb_attempts_ratio = max(0.25,i["sb_attempts"] / (i["walks"] + i["hits"]))
        Speed += round(3*sb_attempts_ratio)
        if i["sb_attempts"] > 3:
            Speed += round(5*float(i["sb_percentage"]))

        # Total Hitter Outs
        sumHitterOuts = i["strikeouts"]+i["groundouts"]+i["flyouts"]
        # % of at-bats resulting in outs, adjusted for 20-sided die AND reduced 50% to account for
        # fact that most hitters need to have 4-8 outs on their advantage for balance
        TotalHitterOuts = round((sumHitterOuts/i["at_bats"])*8)

        # OutSO
        OutSO = round(i["strikeouts"]/sumHitterOuts*TotalHitterOuts)
        #print(f"OutSo is {OutSO}")

        # OutGB
        OutGB = round(i["groundouts"]/sumHitterOuts*TotalHitterOuts)
        #print(f"OutGB is {OutGB}")

        # OutFB
        OutFB = round(i["flyouts"]/sumHitterOuts*TotalHitterOuts)
        #print(f"OutFB is {OutFB}")

        # BB
        BB = round(i["walks"]/(i["walks"]+i["hits"])*(20-TotalHitterOuts))
        #print(f"BB is {BB}")

        # Single
        singles = (i["hits"]-i["doubles"]-i["triples"]-i["home_runs"])
        single = round(singles/(i["walks"]+i["hits"])*(20-TotalHitterOuts))
        #print(f"single is {single}")

        # Single Plus
        single_plus = 0
        if Speed >= 20 and single >= 2:
            single -= 2
            single_plus = 2
        elif Speed >= 15 and single >= 1:
            single -= 1
            single_plus = 1
        #print(f"single_plus is {single_plus}")

        # Double
        double = round(i["doubles"]/(i["walks"]+i["hits"])*(20-TotalHitterOuts))
        #print(f"double is {double}")

        # Triple
        triple = round(i["triples"]/(i["walks"]+i["hits"])*(20-TotalHitterOuts))
        #print(f"triple is {triple}")

        # Home Run
        home_run = round(i["home_runs"]/(i["walks"]+i["hits"])*(20-TotalHitterOuts))
        #print(f"home_run is {home_run}")

        TotalOfOutcomes = OutSO + OutGB + OutFB + BB + single + single_plus + double + triple + home_run
        #print(f"total of outcomes is {TotalOfOutcomes}")
        if not TotalOfOutcomes == 20:
            while TotalOfOutcomes > 20:
                if single > BB:
                    BB -= 1
                    TotalOfOutcomes -=1
                else:
                    single -= 1
                    TotalOfOutcomes -=1
            while TotalOfOutcomes < 20:
                if single > BB:
                    single += 1
                    TotalOfOutcomes +=1
                else:
                    single += 1
                    TotalOfOutcomes +=1
        # On Base
        # for balance, goal is to have this be around 10 for an average hitter, 12 for a good player, 14+ for a star
        #print(f"walks is {i['walks']} and hits is {i['hits']}, at bats is {i['at_bats']}")
        on_base_percentage = (i["walks"]+i["hits"])/(i["at_bats"]+i["walks"])
        slugging_percentage = (singles+2*i["doubles"] + 3*i["triples"] + 4*i["home_runs"])/i["at_bats"]
        OPS = on_base_percentage + slugging_percentage
        #print(f"on base is {on_base_percentage} OPS is {OPS}")
        
        on_base_adjust = 0
        on_base_threshold_high = 0.350
        on_base_threshold_low = 0.325
        #print(f"on base modulo threshold is {(on_base_percentage * 1000) % (on_base_threshold_high * 1000)}")
        if on_base_percentage > on_base_threshold_high:
            #print(f"on base adder is {round(((on_base_percentage * 1000) % (on_base_threshold_high * 1000))/40)}")
            on_base_adjust = min(3,round(((on_base_percentage * 1000) % (on_base_threshold_high * 1000))/40))
        elif on_base_percentage < on_base_threshold_low:
            on_base_adjust = -min(1,round(((on_base_threshold_low * 1000) % (on_base_percentage * 1000))/40))
        
        OPS_adjust = 0
        OPS_threshold_high = 0.700
        OPS_threshold_low = 0.650
        #print(f"OPS modulo threshold is {((OPS * 1000) % (OPS_threshold_high * 1000))}")
        if OPS > OPS_threshold_high:
            #print(f"OPS adder is {round(((OPS * 1000) % (OPS_threshold_high * 1000))/40)}")
            OPS_adjust = min(3,round(((OPS * 1000) % (OPS_threshold_high * 1000))/40))
        elif OPS < OPS_threshold_low:
            OPS_adjust = -min(1,round(((OPS_threshold_low*1000) % (OPS * 1000))/40))
        
        OnBase = 10 + on_base_adjust + OPS_adjust
        """
        print(f"OnBase is {OnBase}")
        print(f"OutSO is {OutSO}")
        print(f"OutGB is {OutGB}")
        print(f"OutFB is {OutFB}")
        print(f"BB is {BB}")
        print(f"single is {single}")
        print(f"single_plus is {single_plus}")
        print(f"double is {double}")
        print(f"triple is {triple}")
        print(f"home_run is {home_run}")
        print(f"speed is {Speed}")
        print(f"total of outcomes is {TotalOfOutcomes}")
        """
        
        # Fielding - differs by position
        field_percent = float(i["field_percentage"])
        #range_factor_9 = float(i["range_factor"])
        if Position == "1B":
            if field_percent > .985:
                Fielding = 1
        if Position == "2B":
            if field_percent > .990:
                Fielding = 4
            elif field_percent > .985:
                Fielding = 3
            elif field_percent > .980:
                Fielding = 2
            elif field_percent > .975:
                Fielding = 1
            else:
                Fielding = 0
        if Position == "SS":
            if field_percent > .980:
                Fielding = 4
            elif field_percent > .974:
                Fielding = 3
            elif field_percent > .968:
                Fielding = 2
            elif field_percent > .962:
                Fielding = 1
            else:
                Fielding = 0
        if Position == "3B":
            if field_percent > .985:
                Fielding = 3
            elif field_percent > .970:
                Fielding = 2
            elif field_percent > .955:
                Fielding = 1
            else:
                Fielding = 0
        if Position == "LF" or Position == "RF":
            if field_percent > .985:
                Fielding = 2
            elif field_percent > .965:
                Fielding = 1
            else:
                Fielding = 0
        if Position == "CF":
            if field_percent > .995:
                Fielding = 3
            elif field_percent > .985:
                Fielding = 2
            elif field_percent > .965:
                Fielding = 1
            else:
                Fielding = 0
        if Position == "C":
            if field_percent > .999:
                Fielding = 12
            elif field_percent > .997:
                Fielding = 10
            elif field_percent > .995:
                Fielding = 8
            elif field_percent > .990:
                Fielding = 6
            elif field_percent > .980:
                Fielding = 5
            elif field_percent > .970:
                Fielding = 4
            else:
                Fielding = 3



        # PointValue - last
        PointValue = 200
        if TotalHitterOuts < 6:
            PointValue += 50*(TotalHitterOuts % 6)
        else:
            PointValue -= 50*(6 % TotalHitterOuts)
        if OnBase > 11:
            PointValue += 75*(OnBase % 11)
        else:
            PointValue -= 75*(11 % OnBase)
        if (double + triple + home_run) >= 1:
            PointValue += 25*((double + triple + home_run) % 1)
            PointValue += 25*(home_run % 1)
        PointValue = max(10,PointValue)

        team = i["team"].split(" ")[-1]

        #print(f"player is {nameFirst} {nameLast}, on base is {OnBase}, outs is {TotalHitterOuts}, and point value is {PointValue}")
        #print("creating card: ")

        # add card to SQL database
        try: 
            showdown_cursor.execute(f"INSERT INTO hitter_cards VALUES({i['id']},'{team}','{nameFirst}','{nameLast}',{PointValue},'{Position1}',{OnBase},{Speed},{OutSO},{OutGB},{OutFB},{BB},{single},{single_plus},{double},{triple},{home_run},{Fielding})")
        except psycopg2.IntegrityError:
            # roll back failure
            showdown_cursor.execute("ROLLBACK")
            # commit rollback
            showdown_connection.commit()
            # remove existing data
            showdown_cursor.execute(f"DELETE FROM hitter_cards WHERE id = {i['id']}")
            # commit remove
            showdown_connection.commit()
            # now, add player
            showdown_cursor.execute(f"INSERT INTO hitter_cards VALUES({i['id']},'{team}','{nameFirst}','{nameLast}',{PointValue},'{Position1}',{OnBase},{Speed},{OutSO},{OutGB},{OutFB},{BB},{single},{single_plus},{double},{triple},{home_run},{Fielding})")
        showdown_connection.commit()

def createDeck(teamName): #for testing purposes
    deckOfCards = {}
    createCards()
    #pitchers
    showdown_cursor.execute(f"SELECT * FROM pitcher_cards WHERE team like {teamName}")
    for i in showdown_cursor:
        card = PlayerCard2.PitcherCard(i['firstname'],i['lastname'],i['pointvalue'],i['position'],i['control'],i['ip'],i['outpu'],i['outso'],i['outgb'],i['outfb'],i['bb'],i['single'],i['double'],i['home_run'])
        deckOfCards.setdefault(i['firstname'] +" "+ i['lastname']+ " " + i['team'],card) # Adds to dictionary {name+team, PlayerCard}
    #hitters
    showdown_cursor.execute(f"SELECT *, double + triple + home_run AS xbh FROM hitter_cards WHERE team like {teamName} ORDER BY onbase DESC, speed DESC, xbh DESC")
    for i in showdown_cursor:
        card = PlayerCard2.BatterCard(i['firstname'],i['lastname'],i['pointvalue'],i['position1'],i['onbase'],i['speed'],i['outso'],i['outgb'],i['outfb'],i['bb'],i['single'],i['single_plus'],i['double'],i['triple'],i['home_run'],i['fielding'])
        deckOfCards.setdefault(i['firstname'] +" "+ i['lastname']+ " " + i['team'],card) # Adds to dictionary {name+team+position, PlayerCard}
    return deckOfCards