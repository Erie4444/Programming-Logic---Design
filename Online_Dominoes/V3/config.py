import math
TILE_DIMENSIONS = (50, 50)
DOMINO_DIMENSIONS = (TILE_DIMENSIONS[0] * 2, TILE_DIMENSIONS[1]) ##horizontal by default
PIP_DIAMETER = 10

SCREEN_DIMENSIONS = (20,10)
DASHBOARD_DIMENSIONS = 200
DASHBOARD_DOMINO_SPACING = 10
DASHBOARD_MAX_DOMINOES_HORIZONTAL = math.floor((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0]-DASHBOARD_DOMINO_SPACING)/(DOMINO_DIMENSIONS[0]+DASHBOARD_DOMINO_SPACING))
DASHBOARD_MAX_DOMINOES_VERTICAL = math.floor((DASHBOARD_DIMENSIONS-DASHBOARD_DOMINO_SPACING)/(DOMINO_DIMENSIONS[1]+DASHBOARD_DOMINO_SPACING))
DASHBOARD_COLOR = '#333333'

PLAYER_HAND_LIMIT = 1

HOST = 'localhost'
PORT = 12347
NUM_PLAYERS = 2
CAPACITY = 10
SLEEP_TIME = 1

BOARD_EMPTY = ' '

TITLE_COORDS = (SCREEN_DIMENSIONS[0]*TILE_DIMENSIONS[0]/2, 50)
TITLE_BUTTON_COORDS = (SCREEN_DIMENSIONS[0]*TILE_DIMENSIONS[0]/2, SCREEN_DIMENSIONS[1]*TILE_DIMENSIONS[1]/2)
TITLE_BUTTON_DIMENSIONS = (200, 100)
TITLE_BUTTON_COLOR = '#333333'
TITLE_BUTTON_OFFSET = 200

DRAW_BUTTON_DIMENSIONS = (50,50)
DRAW_BUTTON_COORDINATES = (SCREEN_DIMENSIONS[0]*TILE_DIMENSIONS[0]-DRAW_BUTTON_DIMENSIONS[0]/2,SCREEN_DIMENSIONS[1]*TILE_DIMENSIONS[1]-DRAW_BUTTON_DIMENSIONS[1]/2)
DRAW_BUTTON_COLOR = '#333333'

TURN_TEXT_POSITION = (50,10)


INSTRUCTIONS = '''INSTRUCTIONS
Objective: Get rid of all your dominos (cards)
Turn Actions:
 - Place a domino
 - Draw a domino

PLACING DOMINOS
  When you place a new domino, you must match the pip count (dots) with 
  one of the 2 sides of the line of dominos on the board
  Ex. [1|2] [2|6] NOT [1|1] [2|2]

DRAWING DOMINOS
  You are only permitted to draw dominos when you don't have a valid domino
  to place on the board.
  
HOW TO USE THE INTERFACE 
 - Click a domino to select or place it either on the board, or in your hand
 - Use Z or X to turn the domino 90 degrees
 - Click the Draw button if you need to draw a card
 - Use the arrow keys to pan across the board

 Have fun playing! (press esc to go back to the titlescreen)'''