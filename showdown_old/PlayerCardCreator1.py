# PlayerCardCreator.py
''' This simple program is used to convert player card data in the form used by the web page @ https://github.com/digitgopher/showdown-data/blob/master/showdown/cards-tables.sql
into player cards of type PlayerCard in my user-defined module.'''

import PlayerCard
import pyperclip
import re
import time

# CRITICAL: copy the text BEFORE running this module.  Otherwise, it'll do nothing.

'''# Create a regex for player first names and last names
namesRegex = re.compile(r'[a-zA-Z]+')

# Create a regex for the middle string - Year [4 digits], set [2 letters], card number [1-3 digits], team [3 or more letters] - that will serve as an important delimiter

# Create a regex for the next - super important! - set of inputs, the numerical values that will populate our player cards

# Get text off clipboard
text = pyperclip.paste()

# Extract text using regex
extractedNames = namesRegex.findall(text)'''
# While using re to its fullest here would be cool, the data are already so regular that it renders the cool stuff unnecessary.

NULL = 'Null' # there are a ton of NULL values in there, this is the simplest way to make the program ignore them

# create a regex to separate data out into ordinary strings without newline, indent, etc. characters
playersRegex = re.compile(r'\(.*\)') # find everything between parentheses

# Get text off clipboard
playerList = playersRegex.findall(pyperclip.paste()) # this will store in playerList a list of strings, in which each individual string is a player card in the original format

# TODO: working on a way to add players with more control than a simple card dump
#playerList = playersRegex.findall(input("Please paste in a string that includes all of the cards you would like to use. "))
# time.sleep(1.5)

# now all we need to do is turn those into PlayerCard format cards!

firstLastNameRegex = re.compile(r'\'[a-zA-Z]{2,}')
individualNameRegex = re.compile(r'\'[a-zA-Z]{2,}\s[a-zA-z]{2,}\'') # find name, using fact that it has text, followed by a space in the middle, followed by text, and is separated by a ' on each side
yearRegex = re.compile(r'\d{4}') # 4 consecutive digits, don't actually need this but it's done
playerOutputsRegex = re.compile(r'\d{1,4}')
positionRegex = re.compile(r'\'[A-Z1-3]{1,4}\'') # position will be a 1-4 digit string ("C", "1B", "LFRF"); this will never pull in the year value because 0 is not included in the regex and every year value starts with "20"
pitcherTypeRegex = re.compile(r'Starter|Reliever|Closer')

deckOfCards = {} # dictionary
# listOfCards = []


for player in playerList:
    thisPlayerRegex = playerOutputsRegex.findall(player)
    pitcherType = pitcherTypeRegex.findall(player)
    if pitcherType == []: # the card is a batter
        # tests
        '''print (thisPlayerRegex) # test
        print(thisPlayerRegex[12]) # print the point value of the card as a test
        print(individualNameRegex.findall(player)[0][1:-1])
        print(yearRegex.findall(player)[0])
        print (type(positionRegex.findall(player)[2]))
        print (positionRegex.findall(player)[2][1:3]) # print the position as a test
        print (positionRegex.findall(player)[2] == '2B') # print whether the position, when called using Regex, is equal to '2B'
        print (str(thePosition)) # print the variable's value
        print (thePosition == "2B") # print whether when called using the variable, is equal to '2B'
        # print (thisPlayerRegex[14]) # test fielding
        try: print (int(thisPlayerRegex[14])) # test fielding
        except IndexError: print ("this player is a DH with no fielding.")
        '''
        thePosition = positionRegex.findall(player)[2][1:-1] # assign the position to a variable
        # BatterCard takes the following inputs:(nameFirst,nameLast,PointValue,Position,Fielding,OnBase,Speed,OutSO,OutGB,OutFB,BB,single,single_plus,double,triple,homerun)
        try: card = PlayerCard.BatterCard( #create a BatterCard by parsing the string using re
            firstLastNameRegex.findall(player)[0][1:],firstLastNameRegex.findall(player)[1][1:], # first and last names
            int(thisPlayerRegex[12]),thePosition, # point value, position,
            int(thisPlayerRegex[2]), int(thisPlayerRegex[13]), int(thisPlayerRegex[3]), # onbase, speed, outSO,
            int(thisPlayerRegex[4]), int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), # outGB, outFB, BB
            int(thisPlayerRegex[7]), int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), # single, single_plus, double
            int(thisPlayerRegex[10]), int(thisPlayerRegex[11]),int(thisPlayerRegex[14])) # triple, homerun, Fielding
        except IndexError: # this card has no fielding value at index 14, meaning it's a DH
            card = PlayerCard.BatterCard( #create a BatterCard by parsing the string using re
            firstLastNameRegex.findall(player)[0][1:-1],firstLastNameRegex.findall(player)[1][1:-1], # find first and last names
            int(thisPlayerRegex[12]),thePosition, # point value, position,
            int(thisPlayerRegex[2]), int(thisPlayerRegex[13]), int(thisPlayerRegex[3]), # onbase, speed, outSO,
            int(thisPlayerRegex[4]), int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), # outGB, outFB, BB
            int(thisPlayerRegex[7]), int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), # single, single_plus, double
            int(thisPlayerRegex[10]), int(thisPlayerRegex[11])) # triple, homerun, ** no fielding for DHs **
    
    else: # the card is a pitcher
        # tests
        '''print(yearRegex.findall(player)[0])
        print(thisPlayerRegex[12]) # print the point value of the card as a test
        print(pitcherType)
        print(individualNameRegex.findall(player)[0][1:-1])
        print(yearRegex.findall(player)[0])'''
        # PitcherCard takes the following inputs: (nameFirst,nameLast,PointValue,Position,Control,IP,OutPU,OutSO,OutGB,OutFB,BB,single,double,homerun))
        card = PlayerCard.PitcherCard( #create a PitcherCard by parsing the string using re
        firstLastNameRegex.findall(player)[0][1:],firstLastNameRegex.findall(player)[1][1:], # first and last names
        int(thisPlayerRegex[11]), pitcherType[0], int(thisPlayerRegex[2]), # point value, position, control
        int(thisPlayerRegex[12]), int(thisPlayerRegex[3]), int(thisPlayerRegex[4]), # IP, outPU, outSO
        int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), int(thisPlayerRegex[7]), # outGB, outFB, BB
        int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), int(thisPlayerRegex[10])) # single, double, homerun
    
    # thisCard = [individualNameRegex.findall(player)[0][1:-1]+yearRegex.findall(player)[0],card]
    
    # this works unless there is a period, apostrophe, or other nonalpha character in the player's name, hence the try/except block
    try: deckOfCards.setdefault(individualNameRegex.findall(player)[0][1:-1]+yearRegex.findall(player)[0],card) # Adds to dictionary {nameyear, PlayerCard}
    except: print("we threw an error at "+player)
    
    # listOfCards.append(card)
    
# here is the same thing as a function, because ShowdownTeam.py has a temporary need
def doTheThing():
    # print("I'm doing the thing.")
    for player in playerList:
        thisPlayerRegex = playerOutputsRegex.findall(player)
        pitcherType = pitcherTypeRegex.findall(player)
        if pitcherType == []: # the card is a batter
            # tests
            '''print (thisPlayerRegex) # test
            print(thisPlayerRegex[12]) # print the point value of the card as a test
            print(individualNameRegex.findall(player)[0][1:-1])
            print(yearRegex.findall(player)[0])
            print (type(positionRegex.findall(player)[2]))
            print (positionRegex.findall(player)[2][1:3]) # print the position as a test
            print (positionRegex.findall(player)[2] == '2B') # print whether the position, when called using Regex, is equal to '2B'
            print (str(thePosition)) # print the variable's value
            print (thePosition == "2B") # print whether when called using the variable, is equal to '2B'
            # print (thisPlayerRegex[14]) # test fielding
            try: print (int(thisPlayerRegex[14])) # test fielding
            except IndexError: print ("this player is a DH with no fielding.")
            '''
            thePosition = positionRegex.findall(player)[2][1:-1] # assign the position to a variable
            # BatterCard takes the following inputs:(nameFirst,nameLast,PointValue,Position,Fielding,OnBase,Speed,OutSO,OutGB,OutFB,BB,single,single_plus,double,triple,homerun)
            try: card = PlayerCard.BatterCard( #create a BatterCard by parsing the string using re
                firstLastNameRegex.findall(player)[0][1:],firstLastNameRegex.findall(player)[1][1:], # first and last names
                int(thisPlayerRegex[12]),thePosition, # point value, position,
                int(thisPlayerRegex[2]), int(thisPlayerRegex[13]), int(thisPlayerRegex[3]), # onbase, speed, outSO,
                int(thisPlayerRegex[4]), int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), # outGB, outFB, BB
                int(thisPlayerRegex[7]), int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), # single, single_plus, double
                int(thisPlayerRegex[10]), int(thisPlayerRegex[11]),int(thisPlayerRegex[14])) # triple, homerun, Fielding
            except IndexError: # this card has no fielding value at index 14, meaning it's a DH
                card = PlayerCard.BatterCard( #create a BatterCard by parsing the string using re
                firstLastNameRegex.findall(player)[0][1:-1],firstLastNameRegex.findall(player)[1][1:-1], # find first and last names
                int(thisPlayerRegex[12]),thePosition, # point value, position,
                int(thisPlayerRegex[2]), int(thisPlayerRegex[13]), int(thisPlayerRegex[3]), # onbase, speed, outSO,
                int(thisPlayerRegex[4]), int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), # outGB, outFB, BB
                int(thisPlayerRegex[7]), int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), # single, single_plus, double
                int(thisPlayerRegex[10]), int(thisPlayerRegex[11])) # triple, homerun, ** no fielding for DHs **
        
        else: # the card is a pitcher
            # tests
            '''print(yearRegex.findall(player)[0])
            print(thisPlayerRegex[12]) # print the point value of the card as a test
            print(pitcherType)
            print(individualNameRegex.findall(player)[0][1:-1])
            print(yearRegex.findall(player)[0])'''
            # PitcherCard takes the following inputs: (nameFirst,nameLast,PointValue,Position,Control,IP,OutPU,OutSO,OutGB,OutFB,BB,single,double,homerun))
            card = PlayerCard.PitcherCard( #create a PitcherCard by parsing the string using re
            firstLastNameRegex.findall(player)[0][1:],firstLastNameRegex.findall(player)[1][1:], # first and last names
            int(thisPlayerRegex[11]), pitcherType[0], int(thisPlayerRegex[2]), # point value, position, control
            int(thisPlayerRegex[12]), int(thisPlayerRegex[3]), int(thisPlayerRegex[4]), # IP, outPU, outSO
            int(thisPlayerRegex[5]), int(thisPlayerRegex[6]), int(thisPlayerRegex[7]), # outGB, outFB, BB
            int(thisPlayerRegex[8]), int(thisPlayerRegex[9]), int(thisPlayerRegex[10])) # single, double, homerun
        
        # thisCard = [individualNameRegex.findall(player)[0][1:-1]+yearRegex.findall(player)[0],card]
        # print(thisCard)
        # this works unless there is a period, apostrophe, or other nonalpha character in the player's name, hence the try/except block
        try: deckOfCards.setdefault(individualNameRegex.findall(player)[0][1:-1]+yearRegex.findall(player)[0],card) # Adds to dictionary {nameyear, PlayerCard}
        except: print("we threw an error at "+player)
        # listOfCards.append(thisCard)
    '''for person in listOfCards:
        print(person.getName(), person.getPosition(),listOfCards.index(person))
    '''
    return deckOfCards
