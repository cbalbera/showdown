# ShowdownTeam.py

"""This module contains all aspects of teams in a Showdown game.
Attributes (members) of a team are all of type PlayerCard & include:
a lineup, starting pitching staff, relief pitching staff, and bench.
A valid team includes the following 20 PlayerCard members:
A lineup of 9 cards, one who plays each position (including DH)
A starting pitching staff of 4 cards
A relief corps of 1-4 cards & a bench of 3-6 cards, totaling 7 cards between the two

One starting pitcher is designated as the active starting pitcher using a boolean value.
"""

import PlayerCard
import pyperclip
import PlayerCardCreator1

# A lineup is a list of 9 batters who each are assigned one position.
# Batting order is stored as a string of PlayerCards
# Each PlayerCard is stored separately in its position
class Lineup(list):
    
    # GETTERS AND SETTERS
    
    def getBattingOrder(self):
        return self._BattingOrder
    
    def getCatcherArm(self): 
        return self.getPositionPlayer("C").getFielding()
    
    def getInfieldArm(self): 
        return (self.getPositionPlayer("1B").getFielding()+self.getPositionPlayer("2B").getFielding()+self.getPositionPlayer("3B").getFielding()+self.getPositionPlayer("SS").getFielding())
    
    def getOutfieldArm(self): 
        return (self.getPositionPlayer("LF").getFielding()+self.getPositionPlayer("CF").getFielding()+self.getPositionPlayer("RF").getFielding()) # getFielding handles pulling fielding value for the appropriate position
    
    def setPitcher(self,thePitcher):
        assert isinstance(thePitcher,PlayerCard.PitcherCard) or thePitcher == None
        if self._Pitcher == None:
            self._Pitcher = thePitcher
        else: # self.getPitcher() != None:
            assert isinstance(thePitcher,PlayerCard.PitcherCard)
            # remove self.getPitcher() from possible new pitchers
            self._Pitcher = thePitcher
        
    def getPitcher(self):
        return self._Pitcher
        
    def getBatter(self,spot):
        assert isinstance(spot, int)
        assert spot >= 1
        assert spot <= 9
        return self.getBattingOrder()[spot-1] # so that batter's number in order follows 1-9 convention while call to list is indexed correctly, e.g. starting with 0
        
    def setPosition(self,position,batter):
        assert position in ["C","1B","2B","3B","SS","LF","CF","RF","DH","P"]
        assert isinstance(batter,PlayerCard.PlayerCard)
        self._Positions.setdefault(position,batter)
        
    def getPositionPlayer(self,position): # output of type PlayerCard.PlayerCard
        assert position in ["C","1B","2B","3B","SS","LF","CF","RF","DH","P"]
        return self._Positions.get(position)
    
    def pitchingChange(self,oldPitcher,newPitcher):
        assert isinstance(newPitcher,PlayerCard.PitcherCard)
        try:
            assert newPitcher.isAvailableToPlay()
            self.setPitcher(newPitcher)
            oldPitcher.takeOutOfGame()
        except AssertionError:
            print("You've tried to put in a pitcher who has already been taken out of the game.")
    
    def getAvailablePlayers(self):
        return self._availablePlayers
    
    def setLineup(self): #critical, as this is the only function called in the initializer
        # important - have the set of cards copied to clipboard before start, otherwise game will crash
        gameDict = PlayerCardCreator1.doTheThing() # dictionary of possible cards
        # temporary - for testing purposes
        self._availablePlayers = gameDict
        """
        # for temporary debugging purposes
        theLineup = [gameDict['Edgar Renteria2004'],gameDict['Juan Pierre2001'],gameDict['Luis Gonzalez2002'],gameDict['Mark Grace2004'],gameDict['Vinny Castilla2002'],gameDict['Eric Young2004'],gameDict['Carl Crawford2003'],gameDict['Toby Hall2003'],gameDict['Harold Baines2000']]
        for player in theLineup:
            # quick check
            print (player.getName())
        self.setPitcher(gameDict['Tom Seaver2004'])
        # quick check
        print (self.getPitcher().getName())
        """
        theLineup = []
        availablePositions = ["C","1B","2B","3B","SS","LF","CF","RF","DH","P"] # at the moment, no pitcher is set whether or not there is a DH
        i = 1
        
        # new way, input a string that is parsed into a list.  Form will be [pitcher name, player name, position, player name, position... 9 times].  This works!
        masterList = input('''Please input your lineup in the form of a comma-separated list.  The player's name
        will be their ID in the set of cards - currently, if using PlayerCardCreator.py, that should be
        the player's first name, a space, their last name, and the year, e.g. 'Tom Seaver2004'.
        The list should start with the ID of the starting pitcher, who does not need a position assigned.
        The list should continue to name all 9 batters, followed by their position. ex:
        Edgar Renteria2004,SS,Luis Gonzalez2002,LF, and so on.  If your pitcher is hitting, simply
        place him 9th in the lineup and assign him the position SP.''').split(",")
        lineupList = []
        positionsList = ["SP"]
        for item in masterList: # separate into players and positions, for ease of parsing
            if masterList.index(item) == 0 or masterList.index(item) % 2 == 1: # first item is SP and then every odd item is a batter
                lineupList.append(item.strip().title())
            else: # every even item after 0 is a position
                theItem = item.strip().upper()
                if theItem in availablePositions and (theItem not in positionsList or (theItem == 'SP' and theItem not in positionsList[1:])): # allows for SP to be placed in lineup
                    positionsList.append(theItem)
                else: raise Exception("The position passed is either not a valid position, or has been assigned to more than one player.")
        
        for player in lineupList:
            if lineupList.index(player) == 0:
                selectedPitcher = gameDict[player] # if KeyError here, your pitcher is not in the gameDict
                self.setPitcher(selectedPitcher)
                self.setPosition("P",selectedPitcher)
                pitcherBats = input("Will your pitcher be hitting today? ") # there is a bug here
                if pitcherBats == True or pitcherBats.upper() == "YES":
                    availablePositions.remove("DH")
                    print("The DH has been removed. Please remember to place this pitcher in the batting order.")
                    #TODO: when pitcher is placed at bat, check that it is indeed this pitcher
                    # will build this functionality later
                else:
                    print ("pitcher's not hitting.")
            else: # lineupList.index(player) > 1
                playerPos = positionsList[lineupList.index(player)]
                print (player+", "+playerPos)
                # figure out how to give appropriate error messages if either of the below two lines fail
                selectedBatter = gameDict[player] # if KeyError here, the current batter is not in the gameDict
                selectedBatter.setCurrentPosition(playerPos) # if ValueError here, player has been assigned a position he can't play
                availablePositions.remove(playerPos) # if error here, position has been double-assigned, shouldn't happen because separation for loop above should handle this
                theLineup.append(selectedBatter) # add batter to lineup
                self.setPosition(playerPos,selectedBatter) # add batter's position to _Positions dictionary
        
        
        '''
        # old way, requiring repeated inputs
        while i < 10:
            # First thing's first: set the pitcher.  Should happen one time and one time only.
            if i == 1 and self.getPitcher() == None:
                selectedPitcherName = input("Please select a starting pitcher. ").title()
                try: selectedPitcher = gameDict[selectedPitcherName]
                except KeyError:
                    print("You've entered a player who is not in the list of valid players.  Please try again!")
                    continue # if this block hits, restart loop at current i without incrementing
                self.setPitcher(selectedPitcher)
                pitcherBat = input("Will your pitcher be hitting today? ")
                if pitcherBat == True or pitcherBat.upper() == "YES":
                    availablePositions.remove("DH")
                    print("The DH has been removed. Please remember to place this pitcher in the batting order.")
                    #TODO: when pitcher is placed at bat, check that it is indeed this pitcher
                    # will build this functionality later
            # Set the batter
            selectedBatterName = input("Please place a batter in the "+str(i)+" spot. ").title() # ask "which batter would you like to place in the "+i+" spot in the lineup?"
            try: selectedBatter = gameDict[selectedBatterName]
            except KeyError:
                print("You've entered a player who is not in the list of valid players.  Please try again!")
                continue # if this block hits, restart loop at current i without incrementing
            selectedBatterPosition = input("Please select a position for this player. ").upper()
            
            # the below two segments work individually, but should be done at once in order to avoid removing the position from the availablePositions list or placing the batter in the lineup unless both conditions are satisfied
            
            #TODO: make this into its own "assign position" function, as this will have to be redone when making subs

            if isinstance(selectedBatter,PlayerCard.PlayerCard):
                try: selectedBatter.setCurrentPosition(selectedBatterPosition) # if both the if statement and the try statement pass, assign batter to this position
                # this may not need to assign the batter a position (to save memory) - may only need to check that he is playing there.  Leaving here for now.
                except ValueError:
                    print("You've assigned this batter to a position he can't legally play.  Please try again!")
                    continue # if this block hits, restart loop at current i without incrementing
                try: # if both the if statement, the above try statement, and this try statement pass, do both things
                    availablePositions.remove(selectedBatterPosition) # if both the if statement, the above try statement, and this try statement pass, remove selected position from availablePositions
                except ValueError: # print statement on following line is self-explanatory
                    print("You've either already placed someone in that position, or the position you've selected is invalid.  Please try again!")
                    continue # if this block hits, restart loop at current i without incrementing
                # so the batter knows what position he is playing and checks to see whether this is valid
                
                theLineup.append(selectedBatter) # if all of the if statement and the two try statements pass, place batter in lineup                
                
                # make it so the lineup knows what position the batter is playing for the purposes of calculating fielding
                #TODO: implement me
                
            else:
                print("The batter you've selected is not a valid PlayerCard.")
                continue # if passed an invalid PlayerCard, restart loop at current i without incrementing
            i += 1
            '''
        self._BattingOrder = theLineup
    
    #__INITIALIZER__

    def __init__(self): # initializing as empty, appending done subsequently
        self._Pitcher = None
        self._Positions = {}
        self._availablePlayers = {}
        self.setLineup() # this function handles lineup setting

class ShowdownTeam: # not strictly necessary for basic operation but will be eventually
    
    # GETTERS AND SETTERS
      
    #__INITIALIZER__
    def __init__(self,lineup,rotation,bullpen,bench):
        assert isinstance(lineup,Lineup)
        assert len(lineup) == 9
        assert isinstance(rotation,list)
        assert len(rotation) == 4
        assert isinstance(bullpen,list)
        assert len(bullpen) >= 1 and len(bullpen) <= 4
        assert isinstance(bench,list)
        assert len(bench) >= 3 and len(bench) <= 6
        assert len(bullpen) + len(bench) == 7
                    
        for b in rotation:
            assert isinstance(b,PlayerCard.PitcherCard)
            assert b.getPosition() == "Starter"
            
        for c in bullpen:
            assert isinstance(c,PlayerCard.PitcherCard)
            assert c.getPosition() == "Reliever" or c.getPosition() == "Closer"
            
        for d in bench:
            assert isinstance(d,PlayerCard.BatterCard)