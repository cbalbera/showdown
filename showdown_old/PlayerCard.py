# PlayerCard.py

"""This module contains the aspects of batter and pitcher Showdown Cards.
Attributes include point value, position, control (pitchers only), on-base (batters only), and outcome ranges.
Outcome ranges for pitchers include Out(PU), Out(SO), Out(GB), Out(FB), BB, 1B, 2B, and HR.
Outcome ranges for pitchers include Out(SO), Out(GB), Out(FB), BB, 1B, 1B+ 2B, 3B and HR.

TODO: pull live data from a source & turn that data into a card.

TODO: create attribute "photo" that just pulls a photo for display
"""

class PlayerCard: # nothing should ever be of class PlayerCard, & all cards should use the PitcherCard or BatterCard subtypes; as such, there is no initializer
    # GETTERS AND SETTERS
    
    def getPointValue(self):
        return self._PointValue
    
    def getPosition1(self): 
        return self._Position1
    
    def getPosition2(self):
        return self._Position2
    
    def getSpeed(self):
        return self._Speed
    
    def setCurrentPosition(self,position):
        positions = ["C","1B","2B","3B","SS","LF","RF","CF","P","DH"]
        assert position.upper() in positions
        #TODO: check that the batterCard can play the position to which he is passed
        # figure out what error this throws if not, so the try/except block in setLineup() under class Lineup can work correctly
        self._CurrentPosition = position
    
    def getCurrentPosition(self):
        return self._CurrentPosition
    
    def setName(self,first,last):
        self._nameFirst = first
        self._nameLast = last
    
    def getName(self):
        return self._nameFirst+" "+self._nameLast
    
    def getLastName(self):
        return self._nameLast
    
    def takeOutOfGame(self):
        self._canPlay = False
        
    def isAvailableToPlay(self):
        return self._canPlay
    
class PitcherCard(PlayerCard):
    # GETTERS AND SETTERS

    def getControl(self):
        return int(self._Control+min(0,int(self.getIP()-self.getInningsPitched()-1)-int(self.getRunsAllowed()/3)))
    
    def getPitcherOutcomes(self):
        return self._PitcherOutcomes
    
    def getIP(self):
        return self._IP
    
    def getInningsPitched(self):
        return self._outsRecorded/3
    
    def setInningsPitched(self,numberOutsRecorded):
        self._outsRecorded = numberOutsRecorded
        
    def getRunsAllowed(self):
        return self._runsAllowed
    
    def setRunsAllowed(self,number):
        self._runsAllowed += number
    
    #__INITIALIZER__
    # Awards to be added later
    def __init__(self,nameFirst,nameLast,PointValue,Position,Control,IP,OutPU,OutSO,OutGB,OutFB,BB,single,double,homerun):
        assert isinstance(nameFirst, str)
        assert isinstance(nameLast, str)
        assert Position.title() == "Starter" or Position.title() == "Reliever" or Position.title() == "Closer"
        assert isinstance(Control, int)
        assert Control >= 0
        assert Control <= 6
        assert isinstance(IP,int)
        assert IP >= 1
        assert IP <= 9
        # the input values are the size of each range
        # TODO: add error messages to each assertion
        assert isinstance(OutPU, int) and OutPU >= 0
        assert isinstance(OutSO, int) and OutSO >= 0
        assert isinstance(OutGB, int) and OutGB >= 0
        assert isinstance(OutFB, int) and OutFB >= 0
        assert isinstance(BB, int) and BB >= 0
        assert isinstance(single, int) and single >= 0
        assert isinstance(double, int) and double >= 0
        assert isinstance(homerun, int) and homerun >= 0
        
        self.setName(nameFirst,nameLast)
        self._PointValue = PointValue
        self._Position = Position
        self._Control = Control
        self._IP = IP
        self._Speed = 10
        self._outsRecorded = 0
        self._runsAllowed = 0
        self._canPlay = True
        
        self._PitcherOutcomes = (OutPU,OutSO,OutGB,OutFB,BB,single,double,homerun)
        
    
class BatterCard(PlayerCard):
    # GETTERS AND SETTERS

    def getOnBase(self):
        return self._OnBase
    
    def getBatterOutcomes(self):
        return self._BatterOutcomes
    
    def checkPosition(self,currentPos,playersPos): # to account for cases where currentPosition is not exactly equal to but means Position (e.g. LF/RF == LF)
        # output is of type bool
        if currentPos == "C":
            return playersPos == "C"
        elif currentPos == "1B":
            return playersPos in ["1B","IF","1B/3B",] # not yet accounting for "anyone can play 1B" factor
        elif currentPos == "2B":
            return playersPos in ["2B","2B/SS","2B/3B","IF"]
        elif currentPos == "3B":
            return playersPos in ["3B","IF","2B/3B","1B/3B",]
        elif currentPos == "SS":
            return playersPos in ["SS","2B/SS","IF"] # although this is a common set of positions people play, there is no "3B/SS" because their fielding almost always is materially different enough for these to be set as _Position1 and _Position2.  Could maybe add later if there is a use case.
        elif currentPos == "LF":
            return playersPos in ["LF","LF/RF","LFRF","OF"]
        elif currentPos == "CF":
            return playersPos in ["CF","OF"]
        elif currentPos == "RF":
            return playersPos in ["RF","LF/RF","LFRF","OF"]
        elif currentPos == "P":
            return playersPos in ["SP","RP","CP"]
        else: # currentPos == DH
            return True
    
    def getFielding(self): # must account for cases where currentPosition is not exactly equal to but means Position (e.g. LF/RF == LF)
        if self.checkPosition(self.getCurrentPosition(),self.getPosition1()):
            return self._Fielding1
        else: #self.checkPosition(self.getCurrentPosition(),self.getPosition2(), I hope! If not, I deserve an error here.
            return self._Fielding2
        # prepared a bit for the eventuality that this function will increase in complexity to account for players playing multiple positions
    
    #__INITIALIZER__
    # Awards to be added later
    # Secondary position to be added later
    def __init__(self,nameFirst,nameLast,PointValue,Position1,OnBase,Speed,OutSO,OutGB,OutFB,BB,single,single_plus,double,triple,homerun,Fielding1 = -1):
        #TODO: add error messages to each assertion
        assert isinstance(nameFirst, str)
        assert isinstance(nameLast, str)
        # the below line currently allows Position to be only 'LF', which I'll accept for now to mean LF/RF.
        assert Position1 == "C" or Position1 == "1B" or Position1 == "2B" or Position1 == "3B" or Position1 == "SS" or Position1 == "LF/RF" or Position1 == "CF" or Position1 == "OF" or Position1 == "IF" or Position1 == "2B/SS" or Position1 == "2B/3B" or Position1 == "-" or Position1 == "LFRF" or Position1 == "DH" or Position1 == "LF" or Position1 == "RF", "Position1 was passed "+str(Position1)+" for "+nameFirst+" "+nameLast+", which caused a fail."
        assert isinstance(Fielding1, int)
        assert Fielding1 >= -1
        assert Fielding1 <= 12
        #assert Fielding2 >= -1 # will be needed eventually
        #assert Fielding2 <= 12 # will be needed eventually
        assert isinstance(Speed,int)
        assert Speed >= 8
        assert Speed <= 28
        assert isinstance(OutSO, int) and OutSO >= 0
        assert isinstance(OutGB, int) and OutGB >= 0
        assert isinstance(OutFB, int) and OutFB >= 0
        assert isinstance(BB, int) and BB >= 0
        assert isinstance(single, int) and single >= 0
        assert isinstance(single_plus, int) and single_plus >= 0
        assert isinstance(double, int) and double >= 0
        assert isinstance(triple, int) and triple >= 0
        assert isinstance(homerun, int) and homerun >= 0
        
        self.setName(nameFirst,nameLast)
        self._PointValue = PointValue
        self._Position1 = Position1
        self._Fielding1 = Fielding1
        self._Position2 = None # will be needed later
        self._Fielding2 = None # will be needed later
        self._OnBase = OnBase
        self._Speed = Speed
        self._canPlay = True
        
        self._BatterOutcomes = (OutSO,OutGB,OutFB,BB,single,single_plus,double,triple,homerun)
        
        self._CurrentPosition = None
