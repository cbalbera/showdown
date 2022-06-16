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

import PlayerCard2
import pyperclip
import PlayerCardCreator2

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
        print(f'left field is {self.getPositionPlayer("LF").getName()}')
        print(f'arm is {self.getPositionPlayer("LF").getFielding()}')
        print(f'center field is {self.getPositionPlayer("CF").getName()}')
        print(f'arm is {self.getPositionPlayer("CF").getFielding()}')
        print(f'right field is {self.getPositionPlayer("RF").getName()}')
        print(f'arm is {self.getPositionPlayer("RF").getFielding()}')

        return (self.getPositionPlayer("LF").getFielding()+self.getPositionPlayer("CF").getFielding()+self.getPositionPlayer("RF").getFielding()) # getFielding handles pulling fielding value for the appropriate position
    
    def setPitcher(self,thePitcher):
        assert isinstance(thePitcher,PlayerCard2.PitcherCard) or thePitcher == None
        if self._Pitcher == None:
            self._Pitcher = thePitcher
        else: # self.getPitcher() != None:
            assert isinstance(thePitcher,PlayerCard2.PitcherCard)
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
        assert isinstance(batter,PlayerCard2.PlayerCard)
        self._Positions.setdefault(position,batter)
        
    def getPositionPlayer(self,position): # output of type PlayerCard.PlayerCard
        assert position in ["C","1B","2B","3B","SS","LF","CF","RF","DH","P"]
        return self._Positions.get(position)
    
    def pitchingChange(self,oldPitcher,newPitcher):
        assert isinstance(newPitcher,PlayerCard2.PitcherCard)
        try:
            assert newPitcher.isAvailableToPlay()
            self.setPitcher(newPitcher)
            oldPitcher.takeOutOfGame()
        except AssertionError:
            print("You've tried to put in a pitcher who has already been taken out of the game.")
    
    def getAvailablePlayers(self):
        return self._availablePlayers
    
    def setLineup(self,gameDict,lineup=None): #critical, as this is the only function called in the initializer
        # important - have the set of cards copied to clipboard before start, otherwise game will crash
        #gameDict = PlayerCardCreator2.createCards() # dictionary of possible cards
        # temporary - for testing purposes
        self._availablePlayers = gameDict

        theLineup = []
        availablePositions = ["C","1B","2B","3B","SS","LF","CF","RF","DH","P"] # at the moment, no pitcher is set whether or not there is a DH
        i = 1
        masterList = []
        if not lineup:
            # new way, input a string that is parsed into a list.  Form will be [pitcher name, player name, position, player name, position... 9 times].  This works!
            masterList = input('''Please input your lineup in the form of a comma-separated list.  The player's name
            will be their ID in the set of cards - currently, if using PlayerCardCreator2.py, that should be
            the player's first name, a space, their last name, a space, and their team (e.g. "Pete Alonso Mets").
            The list should start with the ID of the starting pitcher, who does not need a position assigned.
            The list should continue to name all 9 batters, followed by their position. ex:
            "CF, Brandon Nimmo Mets, SS, Francisco Lindor Mets," and so on.  If your pitcher is hitting, simply
            place him 9th in the lineup and assign him the position SP.''').split(",")
        else:
            masterList = lineup.split(",")

        lineupList = []
        occupiedPositionsList = ["SP"]
        for item in masterList: # separate into players and positions, for ease of parsing
            #print(item)
            if masterList.index(item) == 0 or masterList.index(item) % 2 == 0: # first item is SP and then every even item is a batter
                lineupList.append(item.strip())
            else: # every odd item after is a position
                theItem = item.strip().upper()
                if theItem in availablePositions and (theItem not in occupiedPositionsList or (theItem == 'SP' and theItem not in occupiedPositionsList[1:])): # allows for SP to be placed in lineup
                    occupiedPositionsList.append(theItem)
                else: raise Exception("The position passed is either not a valid position, or has been assigned to more than one player.")
        
        for player in lineupList:
            if lineupList.index(player) == 0:
                selectedPitcher = gameDict[player] # if KeyError here, your pitcher is not in the gameDict
                self.setPitcher(selectedPitcher)
                self.setPosition("P",selectedPitcher)
                pitcherBats = input("Will your pitcher be hitting today? ") # there may be a bug here.  for now, use DH
                if pitcherBats == True or pitcherBats.upper() == "YES":
                    availablePositions.remove("DH")
                    print("The DH has been removed. Please remember to place this pitcher in the batting order.")
                    #TODO [low priority]: when pitcher is placed at bat, check that it is indeed this pitcher
                    # will build this functionality in later
                else:
                    print ("pitcher's not hitting.")
            else: # lineupList.index(player) > 1
                playerPos = occupiedPositionsList[lineupList.index(player)]
                print (player+", "+playerPos)
                # TODO: - update error messages if either of the below two lines fail
                try: 
                    selectedBatter = gameDict[player]
                except KeyError:
                    print("The selected batter is not in the available list of cards. Please restart & try again.")
                try:
                    selectedBatter.setCurrentPosition(playerPos)
                except AssertionError:
                    print("You've either assigned an invalid position or assigned a player to a position he can't play. Please restart & try again.")
                availablePositions.remove(playerPos) # if error here, position has been double-assigned, shouldn't happen because separation for loop above should handle this
                theLineup.append(selectedBatter) # add batter to lineup
                self.setPosition(playerPos,selectedBatter) # add batter's position to _Positions dictionary
        
        self._BattingOrder = theLineup
    
    #__INITIALIZER__

    def __init__(self,cards,Lineup=None): # initializing as empty, appending done subsequently
        self._Pitcher = None
        self._Positions = {}
        self._availablePlayers = {}
        if Lineup:
            self.setLineup(cards,Lineup) # this function handles lineup setting
        else:
            self.setLineup(cards)

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
            assert isinstance(b,PlayerCard2.PitcherCard)
            assert b.getPosition() == "SP"
            
        for c in bullpen:
            assert isinstance(c,PlayerCard2.PitcherCard)
            assert c.getPosition() == "RP" or c.getPosition() == "CP"
            
        for d in bench:
            assert isinstance(d,PlayerCard2.BatterCard)