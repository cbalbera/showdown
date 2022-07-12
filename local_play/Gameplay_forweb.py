# Gameplay_forweb.py

"""Controller module for Showdown card game for web app implementation.

This module contains the subcontroller to play a single game of Showdown via a web app.
Instances reflect a single game.  To play a new game, make a new instance of Gameplay.

This subcontroller manages the following and all associated die rolls:
inning number and top/bottom, the score, the current pitcher and batter, at-bats, pitches, swings,
which cards are on which bases & are thus allowed to take which actions, and the aforementioned actions.

TODO: wherever there is a print, instead pass that data to app.py.

TODO: set a timer for pitch to give the opportunity to steal without that causing delay

"""

import random
import ShowdownTeam2
import PlayerCard2
import PlayerCardCreator2
import logging
import sys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.debug('Start of program')
logging.disable(logging.CRITICAL)

# class that handles all gameplay mechanics
class Gameplay:
    # GETTERS AND SETTERS
    
    def getInningNumber(self):
        return self._InningNumber
    
    def setInningNumber(self,value):
        assert isinstance(value,int)
        assert value > 0
        self._InningNumber = value
    
    #output is of type InningType
    def getInningTopBottom(self):
        return self._InningTopBottom
    
    def setInningTopBottom(self,TorB):
        TorB = TorB.upper()
        assert TorB == "TOP" or TorB == "BOTTOM"
        self._InningTopBottom = TorB
        print("It's the "+self.getInningTopBottom().lower()+" of inning number "+str(self.getInningNumber()))
        
    def getInningNumber(self):
        return self._InningNumber
    
    def setInningNumber(self,number):
        assert isinstance(number,int)
        self._InningNumber = number
    
    def getOuts(self):
        return self._numberOuts
    
    def setOuts(self,value):
        assert value <= 2
        self._numberOuts = value
    
    def getHomeScore(self):
        return self._HomeScore
    
    def getAwayScore(self):
        return self._AwayScore

    def setHomeScore(self,score):
        self._HomeScore = score
        
    def setAwayScore(self,score):
        self._AwayScore = score
    
    #do the next four getter functions go here or in a team
    def getHomePitcher(self):
        return self._HomePitcher
    
    def getAwayPitcher(self):
        return self._AwayPitcher
    
    def getTeamPitcher(self,team):
        assert isinstance(team,ShowdownTeam2.Lineup)
        return team.getPitcher()
    
    '''def getHomeBatter(self):
        return self._HomeBatter
    
    def getAwayBatter(self):
        return self._AwayBatter'''
   
    def getActiveBatter(self):
        if self.getInningTopBottom().upper() == "TOP":
            return self.awayLineup.getBatter(self.awayBatterNumber) 
        else:
            return self.homeLineup.getBatter(self.homeBatterNumber)
        
    def getActivePitcher(self):
        if self.getInningTopBottom().upper() == "TOP":
            return self.homeLineup.getPitcher()
        else:
            return self.awayLineup.getPitcher()
    
    #output is of type ShowdownTeam
    def getHomeTeam(self):
        return self._HomeTeam
    
    #output is of type ShowdownTeam
    def getAwayTeam(self):
        return self._AwayTeam
    
    
    #outputs for the three below getters are of type PlayerCard, or are None
    def getFirstBase(self):
        return self._FirstBase
    
    def getSecondBase(self):
        return self._SecondBase
    
    def getThirdBase(self):
        return self._ThirdBase
    
    #inputs for the three below getters are of type PlayerCard
    def setFirstBase(self,player):
        assert isinstance(player, PlayerCard2.PlayerCard) or player == None
        self._FirstBase = player 
    
    def setSecondBase(self,player):
        assert isinstance(player, PlayerCard2.PlayerCard) or player == None
        self._SecondBase = player
        
    def setThirdBase(self,player):
        assert isinstance(player, PlayerCard2.PlayerCard) or player == None
        self._ThirdBase = player
        
    def dieRoll(self):
        return int(input("For testing purposes, input the die roll you'd like to see."))
        #return random.randint(1,20)
    
    def attemptDoublePlay(self,runner):
        speed = runner.getSpeed()
        if self.getInningTopBottom() == "TOP":
            arm = self.homeLineup.getInfieldArm()
        else:
            arm = self.awayLineup.getInfieldArm()
        roll = self.dieRoll()
        logging.debug("The infield arm is "+str(arm)+", the dice roll is "+str(roll)+", and the runner's speed is "+str(speed)+".")
        if arm + roll > speed:
            print("The runner has been thrown out.  Double play!")
            self.batterOut()
            return "Out!"
        else:
            self.nextBatter()
            return "Safe!"
    
    def advanceOnOutfieldPlay(self):
        #TODO: find which base to advance from
        if self.getSecondBase() == None and self.getThirdBase == None:
            #self.nextBatter()
            return None
        else: # self.getSecondBase() != None or self.getThirdBase != None):
            advanceOrNo = None
            while advanceOrNo not in ["YES","NO","Y","N"]:
                advanceOrNo = input("Would you like to attempt to advance the runner? Y/N").upper()
            if advanceOrNo in ["YES","Y"]:
                if self.getThirdBase() != None:
                    runner = self.getThirdBase()
                else:
                    runner = self.getSecondBase()
                speed = runner.getSpeed()
                if self.getInningTopBottom() == "TOP":
                    arm = self.homeLineup.getOutfieldArm()
                else:
                    arm = self.awayLineup.getOutfieldArm()
                roll = self.dieRoll()
                logging.debug("The outfield arm is "+str(arm)+", the dice roll is "+str(roll)+", and the runner's speed is "+str(speed)+".")
                # the below two options are workable but flawed
                if arm + roll > speed:
                    # this is a little too simplististic right now
                    # for ex: if it is 1st & 2nd, the batter hits a single, and the runner is thrown out at home
                    # the runner who went to 2nd doesn't advance to 3rd
                    # move call to this function between advancing runners and putting the hitter on base?
                    print("The runner has been thrown out.")
                    self.tootblan(runner)
                    return "Out!"
                else:
                    # this is a little too simplististic right now
                    # for ex: if a runner scores from 1st on a double, the original batter ends up at 3rd
                    print("The runner advances successfully.")
                    self.scoreRun(self.getThirdBase())
                    self.setThirdBase(self.getSecondBase())
                    self.setSecondBase(None)
                    return "Safe!"
                
    
    # this is the main function that handles every aspect of each play - pitch, swing, advancing runners, choosing to take extra bases, turning double plays... etc.  This is going to be a doozy.
    def atBat(self):
        thePitcher = self.getActivePitcher()
        theBatter = self.getActiveBatter()
        thePitch = self.dieRoll()
        print("The pitch is a "+str(thePitch)+"!")
        OutcomesList = None
        ResultList = None
        atBatResult = None
        if thePitcher.getControl() + thePitch > theBatter.getOnBase():
            print ("Pitcher's advantage!")
            OutcomesList = thePitcher.getPitcherOutcomes()
            ResultList = self.PitcherOutcomes

        else:
            print ("Batter's advantage!")
            OutcomesList = theBatter.getBatterOutcomes()
            ResultList = self.BatterOutcomes
        
        outcomeSum = 0
        theSwing = self.dieRoll()
        print("The swing is a "+str(theSwing)+"!")
        loopCounter = 0
        # sum up the OutcomesList until you exceed the die roll
        while outcomeSum < theSwing:
            outcomeSum += OutcomesList[loopCounter] # add the next outcome
            if outcomeSum >= theSwing: # correct result identified
                atBatResult = ResultList[loopCounter] 
            loopCounter += 1
            
        print ("The result is a "+atBatResult+"!")
        
        #atBatResult section - this is where the fun begins...
        
        if atBatResult == "Out(PU)" or atBatResult == "Out(SO)":
            self.batterOut()
        # this next one is a doozy
        elif atBatResult == "Out(GB)": #TODO: test this
            if self.getOuts() == 2:
                self.batterOut()
            else: # self.getOuts() < 2: # attempt double play
                if self.getFirstBase() != None and self.getSecondBase() != None and self.getThirdBase() != None:
                    #TODO: this could be a bit more thorough (ask which player to throw out? default to 2nd if already 1 out?)
                    self.tootblan(self.getThirdBase()) # get the runner on third out
                    #does this code simply live in self.attemptDoublePlay()?  Possibly.
                    whichBase = input("Which base would you like to throw to - third, second, or first? ").upper()
                    possibleBases = ["FIRST","SECOND","THIRD","1ST","2ND","3RD","1","2","3"]
                    while whichBase not in possibleBases:
                        whichBase = input("Which base would you like to throw to - third, second, or first? Please select a valid option. ").upper()
                    if whichBase in ["FIRST","1ST","1"]:
                        safeOrOut = self.attemptDoublePlay(theBatter)
                        self.setThirdBase(self.getSecondBase())
                        self.setSecondBase(self.getFirstBase())
                        if safeOrOut == 'Safe!':
                            self.setFirstBase(theBatter)
                        else:
                            self.setFirstBase(None)
                    elif whichBase in ["SECOND","2ND","2"]:
                        safeOrOut = self.attemptDoublePlay(self.getFirstBase())
                        self.setThirdBase(self.getSecondBase())
                        if safeOrOut == 'Safe!':
                            self.setSecondBase(self.getFirstBase())
                        else:
                            self.setSecondBase(None)
                        self.setFirstBase(theBatter)       
                    else: # third base
                        safeOrOut = self.attemptDoublePlay(self.getSecondBase())
                        
                        if safeOrOut == 'Safe!':
                            self.setThirdBase(self.getSecondBase())
                        else:
                            self.setThirdBase(None)
                        self.setSecondBase(self.getFirstBase())
                        self.setFirstBase(theBatter)
                elif self.getFirstBase() != None and self.getSecondBase() != None:
                    self.tootblan(self.getSecondBase())
                    whichBase = input("Which base would you like to throw to - second, or first? ").upper()
                    possibleBases = ["FIRST","SECOND","1ST","2ND","1","2"]
                    while whichBase not in possibleBases:
                        whichBase = input("Which base would you like to throw to - second, or first? Please select a valid option. ").upper()
                    if whichBase in ["FIRST","1ST","1"]:
                        safeOrOut = self.attemptDoublePlay(theBatter)
                        self.setSecondBase(self.getFirstBase())
                        if safeOrOut == 'Safe!':
                            self.setFirstBase(theBatter)
                        else:
                            self.setFirstBase(None)
                    else: # second base
                        safeOrOut = self.attemptDoublePlay(self.getFirstBase())
                        if safeOrOut == 'Safe!':
                            self.setSecondBase(self.getFirstBase())
                        else:
                            self.setSecondBase(None)
                        self.setFirstBase(theBatter)
                elif self.getFirstBase() != None:
                    self.tootblan(self.getFirstBase())
                    safeOrOut = self.attemptDoublePlay(theBatter)
                    if safeOrOut == 'Safe!':
                        self.setFirstBase(theBatter)
                    else:
                        self.setFirstBase(None)
                else: # no double play potential, advance runners if fast enough
                    if self.getSecondBase() != None and self.getThirdBase() == None and self.getSecondBase().getSpeed() >= 12:
                        self.batterOut()
                        self.setThirdBase(self.getSecondBase())
                    elif self.getSecondBase() != None and self.getThirdBase() == None and self.getSecondBase().getSpeed() < 12:
                        self.batterOut()
                    if self.getThirdBase() != None and self.getThirdBase().getSpeed() >= 12: # give option to hold the runner
                        throwOrNo = input("Would you like to prevent a run by throwing home, at the expense of getting the batter out? (Y/N)").upper()
                        if throwOrNo in ["Y","YES"]:
                            self.setFirstBase(theBatter)
                        else:
                            self.batterOut()
                            self.scoreRun(self.getThirdBase())
                            self.setThirdBase(None)
                            if self.getSecondBase() != None and self.getSecondBase().getSpeed() >= 12:
                                self.setThirdBase(self.getSecondBase())
                                self.setSecondBase(None)
                    elif self.getThirdBase() != None and self.getThirdBase().getSpeed() < 12:
                        self.batterOut()
                    else: # no runners
                        self.batterOut()
        elif atBatResult == "Out(FB)":
            self.batterOut()
            if self.getSecondBase() != None or self.getThirdBase() != None:
                self.advanceOnOutfieldPlay()
        elif atBatResult == "BB":
            if self.getFirstBase() != None and self.getSecondBase() != None and self.getThirdBase() != None:
                self.scoreRun(self.getThirdBase())
            if self.getFirstBase() != None and self.getSecondBase() != None:
                self.setThirdBase(self.getSecondBase())
            if self.getFirstBase() != None:
                self.setSecondBase(self.getFirstBase())
            self.setFirstBase(theBatter)
            self.nextBatter()
        elif atBatResult == "single":
            self.scoreRun(self.getThirdBase())
            self.setThirdBase(self.getSecondBase())
            self.setSecondBase(self.getFirstBase())
            self.setFirstBase(theBatter)
            self.nextBatter()
            if self.getSecondBase() != None or self.getThirdBase() != None:
                self.advanceOnOutfieldPlay()
        elif atBatResult == "single_plus": # if second base is empty after runners have advanced, advance the original batter to second base
            self.scoreRun(self.getThirdBase())
            self.setThirdBase(self.getSecondBase())
            self.setSecondBase(self.getFirstBase())
            self.nextBatter()
            if self.getSecondBase() == None:
                self.setSecondBase(theBatter)
                if self.getThirdBase() != None:
                    self.advanceOnOutfieldPlay()
            else:
                self.setFirstBase(theBatter)
                if self.getSecondBase() != None or self.getThirdBase() != None:
                    self.advanceOnOutfieldPlay()
        elif atBatResult == "double":
            self.scoreRun(self.getThirdBase())
            self.scoreRun(self.getSecondBase())
            self.setThirdBase(self.getFirstBase())
            self.setSecondBase(theBatter)
            self.setFirstBase(None)
            self.nextBatter()
            if self.getThirdBase() != None:
                    self.advanceOnOutfieldPlay()
            else:
                self.nextBatter()
        # if "single","single_plus","double" then self.attemptTagUp() and (self.getSecondBase != None or self.getThirdBase() != None), as per above
        elif atBatResult == "triple":
            self.scoreRun(self.getThirdBase())
            self.scoreRun(self.getSecondBase())
            self.scoreRun(self.getFirstBase())
            self.setThirdBase(theBatter)
            self.setSecondBase(None)
            self.setFirstBase(None)
            self.nextBatter()
        elif atBatResult == "homerun":
            self.scoreRun(self.getThirdBase())
            self.scoreRun(self.getSecondBase())
            self.scoreRun(self.getFirstBase())
            self.scoreRun(theBatter)
            self.setThirdBase(None)
            self.setSecondBase(None)
            self.setFirstBase(None)
            self.nextBatter()
        
        # on to the next batter, once every possible outcome is calculated!
    
    def incrementInning(self): 
        # check here if game should end
        if self.getInningNumber() >= self.numberInnings:
            if self.getInningTopBottom() == "TOP" and self.getHomeScore() > self.getAwayScore():
                self.activeGame = False
                print ("The home team defeated the away team by a score of "+str(self.getHomeScore())+" to "+str(self.getAwayScore())+" in "+str(self.getInningNumber())+" innings.")
            elif self.getInningTopBottom() == "BOTTOM" and self.getHomeScore() < self.getAwayScore():
                self.activeGame = False
                print ("The away team defeated the home team by a score of "+str(self.getAwayScore())+" to "+str(self.getHomeScore())+" in "+str(self.getInningNumber())+" innings.")

        # otherwise, increment inning
        if self.activeGame:
            if self.getInningTopBottom() == "BOTTOM":
                self.setInningNumber(self.getInningNumber()+1)
                self.setInningTopBottom("TOP")
            else:
                self.setInningTopBottom("BOTTOM")
            self.setOuts(0)
            self.setFirstBase(None)
            self.setSecondBase(None)
            self.setThirdBase(None)
        
    def nextBatter(self):
        if self.getInningTopBottom() == "TOP":
            if self.awayBatterNumber == 9:
                self.awayBatterNumber = 1
            else:
                self.awayBatterNumber += 1
        if self.getInningTopBottom() == "BOTTOM":
            if self.homeBatterNumber == 9:
                self.homeBatterNumber = 1
            else:
                self.homeBatterNumber += 1
    
    def playerOut(self):
        self.getActivePitcher().setInningsPitched(self.getActivePitcher().getInningsPitched()*3+1) # add one out to pitcher's count
        if self._numberOuts == 2:
            self.incrementInning()
        else:
            self._numberOuts += 1
    
    def batterOut(self):
        self.nextBatter()
        self.playerOut()
    
    def tootblan(self,player):
        if self.getFirstBase() == player:
            self.setFirstBase(None)
        elif self.getSecondBase() == player:
            self.setSecondBase(None)
        else: # self.getThirdBase() == player
            self.setThirdBase(None)
        self.playerOut()
            
    def scoreRun(self,player):
        if player != None:
            logging.debug("The pitcher has previously allowed this many runs: "+str(self.getActivePitcher().getRunsAllowed()))
            self.getActivePitcher().setRunsAllowed(1)
            logging.debug("The pitcher has now allowed this many runs: "+str(self.getActivePitcher().getRunsAllowed()))
            if self.getInningTopBottom() == "TOP":
                self.setAwayScore(self.getAwayScore()+1)
            else:
                self.setHomeScore(self.getHomeScore()+1)
    
    # helper for initializer - checks if team is a .txt file, if so moves forward, if not goes thru create team prompt
    def createTeam(self,cards,team=None):
        if team == None:
            lineup = ShowdownTeam2.Lineup(cards)
        else: 
            lineup = ShowdownTeam2.Lineup(cards,Lineup=team)
        return lineup

    # __INITIALIZER__
    def __init__(self,innings=0,homeTeam=None,awayTeam=None,gameDict=None,teams="MLB"):#,HomeTeam,AwayTeam): #saved for later
        self.numberInnings = innings
        while self.numberInnings < 1 or self.numberInnings > 9:
            try:
                self.numberInnings = int(input("Please select how many innings will be played (1-9). ")) # set number of innings to play
                assert isinstance (self.numberInnings, int) and self.numberInnings >= 1 and self.numberInnings <= 9 # if fail here, program crashes, try again
            except ValueError:
                print("You've input something that's not a number.")
            except AssertionError:
                print("Please input a number of innings that is between 1 and 9.")
        
        # now assumes that Gameplay can be passed either a complete team (in which case moves forward as such)
        # or something invalid, in which case go through team creation flow
        cards = ""
        if not gameDict:
            cards = PlayerCardCreator2.createCards()
        else:
            cards = gameDict
        self.homeLineup = self.createTeam(cards,homeTeam)
        self.awayLineup = self.createTeam(cards,awayTeam)
        # ability to create teams by accepting .txt file with args - for testing, not currently in use
        """
        if len(sys.argv) > 4:
            if sys.argv[2].lower == "home":
                with open(sys.argv[1], 'r') as hfile:
                    homeTeam = hfile.read()
                    self.homeLineup = ShowdownTeam2.Lineup(gameDict,Lineup=homeTeam)
                with open(sys.argv[3], 'r') as afile:
                    awayTeam = afile.read()
                    self.awayLineup = ShowdownTeam2.Lineup(gameDict,Lineup=awayTeam)
            else:
                with open(sys.argv[1], 'r') as afile:
                    awayTeam = afile.read()
                    self.awayLineup = ShowdownTeam2.Lineup(gameDict,Lineup=awayTeam)
                with open(sys.argv[3], 'r') as hfile:
                    homeTeam = hfile.read()
                    self.homeLineup = ShowdownTeam2.Lineup(gameDict,Lineup=homeTeam)
        elif len(sys.argv) > 2:
            if sys.argv[2].lower == "home":
                with open(sys.argv[1], 'r') as file:
                    homeTeam = file.read()
                    self.homeLineup = ShowdownTeam2.Lineup(gameDict,Lineup=homeTeam)
                self.awayLineup = ShowdownTeam2.Lineup(gameDict)
            else:
                with open(sys.argv[1], 'r') as afile:
                    awayTeam = afile.read()
                    self.awayLineup = ShowdownTeam2.Lineup(gameDict,Lineup=awayTeam)
                self.homeLineup = ShowdownTeam2.Lineup(gameDict)
        else:
            self.homeLineup = ShowdownTeam2.Lineup(gameDict)
            self.awayLineup = ShowdownTeam2.Lineup(gameDict)
        """

        # awayLineup = awayTeam.getBattingOrder()
        self.PitcherOutcomes = ["Out(PU)","Out(SO)","Out(GB)","Out(FB)","BB","single","double","homerun"]
        self.BatterOutcomes = ["Out(SO)","Out(GB)","Out(FB)","BB","single","single_plus","double","triple","homerun"]
        self.setInningNumber(1)
        self.setInningTopBottom('TOP')
        self.setHomeScore(0)
        self.setAwayScore(0)
        self._numberOuts = 0 # use setter?
        self.awayBatterNumber = 1
        self.homeBatterNumber = 1
        self.setFirstBase(None)
        self.setSecondBase(None)
        self.setThirdBase(None)
        self.activeGame = True

        while self.activeGame:
            # before the pitch
            # log active state
            print(self.getInningTopBottom()+" "+str(self.getInningNumber()))
            print(str(self.getAwayScore())+" - "+str(self.getHomeScore()))
            print(f"Pitcher: {self.getActivePitcher().getName()} ({self.getActivePitcher().getControl()})")
            print(f"Batter: {self.getActiveBatter().getName()} ({self.getActiveBatter().getOnBase()})")
            print ("O: "+str(self.getOuts()*"x"))
            if self.getFirstBase() == None:
                print ("1B:")
            else: print ("1B: "+self.getFirstBase().getLastName()+" ("+str(self.getFirstBase().getSpeed())+")")
            if self.getSecondBase() == None:
                print ("2B:")
            else: print ("2B: "+self.getSecondBase().getLastName()+" ("+str(self.getSecondBase().getSpeed())+")")
            if self.getThirdBase() == None:
                print ("3B:")
            else: print ("3B: "+self.getThirdBase().getLastName()+" ("+str(self.getThirdBase().getSpeed())+")")
            
            # pitcher options - disabled for now for quicker debugging
            pQuestion = None
            while (pQuestion != 'pitch' and pQuestion != 'change pitchers'):
                pQuestion = input("What do you want to do - 'pitch' or 'change pitchers'? ").lower()
                while pQuestion == 'change pitchers':
                    newPitcherName = input("Which pitcher would you like to sub in? ")
                    try:
                        if self.getInningTopBottom() == "TOP":
                            logging.debug("Top of inning, checking")
                            logging.debug(self.homeLineup.getAvailablePlayers()[newPitcherName].getName()+" is the name of the new pitcher")
                            #print(self.getHomeTeam().getAvailablePlayers()[newPitcherName].getName()+" is the name of the new pitcher")
                            # temporary fix in here - eventually replace self.homelineup with self.getHomeTeam (same below for Away)
                            self.homeLineup.pitchingChange(self.getActivePitcher(),self.homeLineup.getAvailablePlayers()[newPitcherName])
                        else:
                            logging.debug("Bottom of inning, checking")
                            logging.debug(self.awayLineup.getAvailablePlayers()[newPitcherName].getName()+" is the name of the new pitcher")
                            #print(self.awaylineup.getAvailablePlayers()[newPitcherName].getName()+" is the name of the new pitcher")
                            self.awayLineup.pitchingChange(self.getActivePitcher(),self.awayLineup.getAvailablePlayers()[newPitcherName])
                    except KeyError:
                        print ("You've entered an invalid pitcher.")
                    pQuestion = input("What do you want to do - 'pitch' or 'change pitchers'? ").lower()
                
            
            # batter options - similar to pitchers', above
            '''if self.getFirstBase() != None:
                self.stealBase(self.getFirstBase(),'second')
            
            if self.getSecondBase() != None:
                self.stealBase(self.getThirdBase(),'third')
            '''
            # call atBat() to handle the pitch, swing, outcome, and all associated changes, including inning increment, and finally bring up the next batter
            logging.debug("The pitcher's control is "+str(self.getActivePitcher().getControl()))
            logging.debug("The control reduction factor is "+str(min(0,self.getActivePitcher().getIP()-self.getActivePitcher().getInningsPitched()-1-self.getActivePitcher().getRunsAllowed()/3)))
            logging.debug("The IP factor is "+str(self.getActivePitcher().getIP()-self.getActivePitcher().getInningsPitched()-1))
            logging.debug("The runs allowed factor is "+str(int(-self.getActivePitcher().getRunsAllowed()/3)))
            logging.debug("The pitcher has allowed this many runs: "+str(-self.getActivePitcher().getRunsAllowed()))
            self.atBat()

            # check for walkoff win - any end of inning checks happen in incrementInning(self)
            # home team wins
            logging.info("We are in the "+self.getInningTopBottom()+" of the "+str(self.getInningNumber())+" inning out of a total of "+str(self.numberInnings)+".")
            logging.info("There are "+str(self.getOuts())+" outs.")
            logging.info("The score is "+str(self.getAwayScore())+" - "+str(self.getHomeScore())+".")
            if (self.getInningNumber() >= self.numberInnings and self.getInningTopBottom() == "BOTTOM" and self.getHomeScore() > self.getAwayScore()):
                self.activeGame = False
                print ("The home team defeated the away team by a score of "+str(self.getHomeScore())+" to "+str(self.getAwayScore())+" via a walk-off in inning "+str(self.getInningNumber())+".")
            
            # away team wins
            # self.getOuts() == 3 isn't hitting here
            '''if (self.getInningNumber() >= self.numberInnings and self.getOuts() == 3 and self.getInningTopBottom() == "BOTTOM" and self.getHomeScore() < self.getAwayScore()):
                self.activeGame = False                
                return ("The away team defeated the home team by a score of "+str(self.getAwayScore())+" to "+str(self.getHomeScore())+" in "+str(self.inning)+" innings.")
            '''
        print ("Game over!")