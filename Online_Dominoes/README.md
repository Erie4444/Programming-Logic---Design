# ONLINE DOMINOS
## **IMPORTANT**
Please use the files in the V3 Folder, all others are outdated and don't work

Files to run:
 - Dominoes_Client.py
 - Dominoes_Server.py

There is a config.py where you can configure the amount of player and hand limits

By default we play with 2 players with 7 dominos in the starting hand

Run the Dominoes_Server.py first, then run Dominoes_Client.py to add clients

## Screens
### Title
On the title screen, you have 2 buttons, one to start playing, and one for the instructions

### Instructions
This displays the instructions to play the game, press esc to go back to the main title screen

### Game

#### Joining
When you join the server, you can be either a player or spectator. These roles will be automatically assigned based on the amount of players currently in the game

The caption of the pygame screen and the top left text will tell you if you are a player or not

#### How to play
Objective: Get rid of all your dominos (cards)

##### TURN ACTIONS:
 - Place a domino
 - Draw a domino

##### PLACING DOMINOS

  When you place a new domino, you must match the pip count (dots) with 
  one of the 2 sides of the line of dominos on the board
  Ex. [1|2] [2|6] NOT [1|1] [2|2]

##### DRAWING DOMINOS
  You are only permitted to draw dominos when you don't have a valid domino
  to place on the board.
  
##### HOW TO USE THE INTERFACE 
 - Click a domino to select or place it either on the board, or in your hand
 - Use Z or X to turn the domino 90 degrees
 - Click the Draw button if you need to draw a card (it is a little slow)
 - Use the arrow keys to pan across the board

#### Ending the game
When the game ends, just quit out of any player screen and everything will close by itself.
