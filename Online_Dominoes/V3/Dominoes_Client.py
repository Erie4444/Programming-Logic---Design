"""========RUN THIS FOR THE CLIENT========="""

from config import *
from Socket_Client import SocketClient
from Dominoes_Logic import *
from threading import Thread
from util import *
import sys
from Dominoes_UI import *
import pygame

class DominoesClient:
    '''
    The Client code that is run
    '''
    def __init__(self):
        ##initializing values
        pygame.init()
        self.socket = SocketClient()
        self.status = "started"
        self.running = True
        self.boardLeft = None
        self.boardRight = None
        self.playerNum = None
        self.waitingForResponse = False
        self.logic = None
        self.board = None
        self.boardOrigin = None
        self.lastPlacedDomino = None
        self.waitingForPlayers = True
        self.canDraw = True
        self.viewingOrigin = (0,0)
        self.UIBoard = pygame.sprite.GroupSingle()
        self.UIDashboard = pygame.sprite.GroupSingle()
        self.selectedDomino = pygame.sprite.GroupSingle()
        self.titleScreen = pygame.sprite.GroupSingle()
        self.waitingScreen = pygame.sprite.GroupSingle()
        self.drawButton = pygame.sprite.GroupSingle()
        self.turnText = pygame.sprite.GroupSingle()
        self.alert = pygame.sprite.GroupSingle()
    
    def startApplication(self):
        ##starts the application
        self.name = input("Enter your name: ")
        self.initScreen()
        self.titleScreen.add(UITitleScreen())
        self.status = "title"
    
    def joinGame(self):
        ##joins the game
        self.status = "joining"
        self.socket.connect()
        Thread(target=self.listenToServer, daemon=True).start()
        waitUntil(lambda: self.status != "joining") ##waits until it recieved a confirmation message
        ##based on your status, join as different roles
        if self.status == "player":
            self.joinPlayer()
        elif self.status == "spectator":
            self.joinSpectator()
        elif self.status == "denied":
            self.close()

        print("Joined!")

        ##starting UI
        self.waitingScreen.empty()
        self.waitingScreen.add(UIWaitingScreen("Connected!"))
        if self.status == "spectator":
            self.waitingScreen.empty()
            self.UIBoard.add(UIBoard())
            self.turnText.add(UIText("Spectating",TURN_TEXT_POSITION,(100,20),15))

    def initScreen(self):
        ##initializes the UI screen
        self.screen  = pygame.display.set_mode((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
        self.clock = pygame.time.Clock() 

    def draw(self):
        ##drawing all sprites
        self.screen.fill('#000000')
        self.UIBoard.draw(self.screen)
        self.UIDashboard.draw(self.screen)
        self.selectedDomino.draw(self.screen)
        self.drawButton.draw(self.screen)
        self.turnText.draw(self.screen)
        self.titleScreen.draw(self.screen)
        self.waitingScreen.draw(self.screen)
        self.alert.draw(self.screen)
    
    def updateDisplay(self):
        ##updates the display
        self.alert.update() ##decrements alert, destroying it if time is up
        self.selectedDomino.update() ##draws the selected domino
        ##updates the boards and dashboard
        if self.board and self.boardOrigin:
            self.UIBoard.update(self.board,self.boardOrigin)
            self.UIDashboard.update()

        self.draw()
        pygame.display.update()
    
    def updateLoop(self):
        '''
        Main loop
        '''
        while self.running:
            if self.waitingForPlayers and self.status == "player":
                self.waitingForPlayersScreen()
            elif self.status == "title":
                self.titleUpdate()
            elif self.status == "instructions":
                self.instructionUpdate()
            elif self.status == "start":
                self.joinGame()
            elif self.status == "player":
                self.playerUpdate()
            elif self.status == "spectator":
                self.spectatorUpdate()
            elif self.status == "end":
                self.end()
            self.updateDisplay()
            self.clock.tick(60)
        self.close()
    
    def end(self):
        ##run at the end of the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
    
    def waitingForPlayersScreen(self):
        ##run while waiting for other players
        self.waitingScreen.empty()
        self.waitingScreen.add(UIWaitingScreen("Waiting For Other Players..."))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()

    def titleUpdate(self):
        ##run at the title screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                ##starts game if clicked start button
                if self.titleScreen.sprite.isHoveringStart(event.pos):
                    self.status = "start"
                    self.titleScreen.empty()
                    self.waitingScreen.add(UIWaitingScreen("Joining Game..."))
                
                ##goes to instructions if clicked instructions
                elif self.titleScreen.sprite.isHoveringInstruction(event.pos):
                    self.status = "instructions"
                    self.titleScreen.empty()
                    self.waitingScreen.add(UIWaitingScreen(INSTRUCTIONS,15))
    
    def instructionUpdate(self):
        ##runs on the instruction page
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            
            ##goes back to the title if esc is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.status = "title"
                    self.waitingScreen.empty()
                    self.titleScreen.add(UITitleScreen())

    def playerUpdate(self):
        ##run in the actual game state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.shutdown()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.selectedDomino.sprite:##if you're currently selecting a domino
                    if self.UIDashboard.sprite.isHovering(event.pos): ##if over the dashboard
                        ##place back in hand
                        self.selectedDomino.sprite.resetDirection()
                        self.UIDashboard.sprite.dominoes.add(self.selectedDomino.sprite)
                        self.selectedDomino.empty()
                    else: ##else, it's over the board
                        self.lastPlacedDomino = self.logic.getLogicDomino(self.selectedDomino.sprite.getPips()) ##getting the logic domino equivalent
                        self.lastPlacedDomino.angle = self.selectedDomino.sprite.angle
                        cell = getLeftPipDominoCell(event.pos[0],event.pos[1],self.lastPlacedDomino) ##finding the cell they're placing in
                        cell = (cell[0]-self.UIBoard.sprite.origin[0],cell[1]-self.UIBoard.sprite.origin[1]) ##adjusting for scrolling
                        self.lastPlacedDomino.placeLeft(cell[0],cell[1]) ##adjusting the domino positions
                        self.sendGameMessage("place",self.lastPlacedDomino.deconstruct()) ##sending the place message
                
                elif self.drawButton.sprite.isHovering(event.pos):## clicked draw
                    self.canDraw = True
                    self.sendGameMessage("requestBoardPips","")
                    self.waitingForResponse = True
                    waitUntil(lambda:self.waitingForResponse == False or self.running == False) ##waits until the server responds
                    ##canDraw will be false if we have dominos when the server responds
                    ##checking if we have dominos
                    if not self.logic.hand.hasDominoWithPip(self.boardLeft) and not self.logic.hand.hasDominoWithPip(self.boardRight) and self.canDraw:
                        self.sendGameMessage("draw","")
                        self.waitingForResponse = True
                    else:
                        self.alert.add(UIAlert("You Have Valid Dominos",(500,100),30,60))
                
                    ##not selecting a domino nor draw button
                else:
                    self.selectedDomino.add(self.UIDashboard.sprite.getHovering(event.pos)) ##get the domino you are trying to select
                    if self.selectedDomino.sprite:
                        self.selectedDomino.sprite.setAbsPos(event.pos) ##setting its position at your mouse position
                        self.UIDashboard.sprite.removeDomino(self.selectedDomino.sprite) ##remove the domino from the dashboard

            if event.type == pygame.MOUSEMOTION:
                ##move the selected domino to your mouse
                if self.selectedDomino.sprite:
                    self.selectedDomino.sprite.setAbsPos(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if self.selectedDomino.sprite:
                    if event.key == pygame.K_z: ##rotate selected domino counter clockwise
                        self.selectedDomino.sprite.rotateCounterclockwise()
                    
                    if event.key == pygame.K_x: ##rotate selected domino clockwise
                        self.selectedDomino.sprite.rotateClockwise()
                    
                ##scrolling keys
                if event.key == pygame.K_DOWN:
                    self.UIBoard.sprite.scrollUp()
                if event.key == pygame.K_UP:
                    self.UIBoard.sprite.scrollDown()
                if event.key == pygame.K_RIGHT:
                    self.UIBoard.sprite.scrollLeft()
                if event.key == pygame.K_LEFT:
                    self.UIBoard.sprite.scrollRight()

        if self.logic: ##if there is logic, check if we win
            self.checkWin()

    def spectatorUpdate(self):
        ##Just has quit and scroll features
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.UIBoard.sprite.scrollUp()
                if event.key == pygame.K_UP:
                    self.UIBoard.sprite.scrollDown()
                if event.key == pygame.K_RIGHT:
                    self.UIBoard.sprite.scrollLeft()
                if event.key == pygame.K_LEFT:
                    self.UIBoard.sprite.scrollRight()

    def joinPlayer(self):
        ##requests to join as player
        # print("Client: You are a player")
        # input("Press Enter to join the game...")
        pygame.display.set_caption(f"Dominoes: {self.name}")
        self.socket.sendMessage("join", {"type": "player", "name": self.name})
    
    def joinSpectator(self):
        ##requests to join as spectator
        # print("Client: You are a spectator")
        # input("Press Enter to spectate the game...")
        pygame.display.set_caption("Dominoes: Spectator")
        self.socket.sendMessage("join", {"type": "spectator"})
    
    def sendGameMessage(self,action,content):
        ##sends a in-game message to the server
        if isinstance(content,Domino):
            content = content.deconstruct()
        self.socket.sendMessage("game",{"num":self.playerNum} | {"action":action,"content":content})

    def listenToServer(self):
        while self.socket.state == "connected":
            message = self.socket.receiveMessage()
            if message:
                if message["type"] == "connectedPlayer": ##connected as a player
                    self.status = "player"

                elif message["type"] == "connectedSpectator": ##connected as a spectator
                    self.status = "spectator"

                elif message["type"] == "denyConnection": ##when server is at max capacity
                    print("Server at max capacity")
                    self.status = "denied"

                elif message["type"] == "confirm": ##confirmed join
                    if message["content"] != "": ##joined as player
                        # print(f"Client: Server confirmation, you are player {message['content']['playerCount']}")
                        if not self.playerNum: ##setting player number
                            self.playerNum = int(message['content']['playerCount'])
                        
                        ##assigning UI elements
                        self.UIBoard.add(UIBoard())
                        self.UIDashboard.add(UIDashboard())
                        self.drawButton.add(UIButton("Draw",DRAW_BUTTON_COORDINATES,DRAW_BUTTON_DIMENSIONS,DRAW_BUTTON_COLOR,15))
                        self.turnText.add(UIText("",TURN_TEXT_POSITION,(100,20),15))

                    else: ## joined as spectator
                        # print("Client: Server confirmation, you are a spectator")
                        pass
                
                elif message["type"] == "gameStart":
                    ##all players have joined, game has started
                    self.waitingForPlayers = False
                    self.waitingScreen.empty()

                elif message["type"] == "shutdown" or message["type"] == "close":
                    ##when the server closes
                    # print("Client: Disconnecting...")
                    self.running = False

                elif message["type"] == "hand":
                    ##gets a hand from the server
                    deconstructedHand = message["content"]
                    reconstructedHand = []
                    ##reconstructs the hand
                    for domino in deconstructedHand:
                        temp = Domino(0,0)
                        temp.reconstruct(domino)
                        reconstructedHand.append(temp)
                    
                    ##instantiates the logic and dashboard with the hand
                    hand = Hand(reconstructedHand)
                    self.logic = ClientLogic(hand)
                    self.UIDashboard.sprite.setDominoes(reconstructedHand)
                    self.waitingScreen.empty()
                    
                elif message["type"] == "placementFailure": ##failure to place
                    self.waitingForResponse = False
                    self.lastPlacedDomino = None
                    
                elif message["type"] == "placementSuccess": ##placement is a success
                    self.waitingForResponse = False
                    self.logic.hand.removeDomino(self.lastPlacedDomino) ##remove domino from hand
                    self.selectedDomino.empty() ##not selecting a domino anymore
                
                elif message["type"] == "draw": ##drew a domino
                    recvDomino = message["content"]
                    temp = Domino(0,0) ##reconstruct the drew domino
                    temp.reconstruct(recvDomino)

                    ##adds the domino to the hands (logic and dashboard)
                    self.logic.hand.addDomino(temp)
                    self.UIDashboard.sprite.addDomino(temp) 
                    self.waitingForResponse = False
                    
                elif message["type"] == "drawFailure": ##no more dominos in the pile
                    print("Nothing to draw from")
                    self.alert.add(UIAlert("Deck Empty",(500,100),30,60))
                    self.waitingForResponse = False

                elif message["type"] == "notYourTurn": ##playing out of turn
                    self.alert.add(UIAlert("Not Your Turn",(500,100),30,60))
                    self.waitingForResponse = False
                
                elif message["type"] == "pips": ##when the server sends the left and right pips of the board when you try to draw
                    self.boardLeft = message["content"]["left"]
                    self.boardRight = message["content"]["right"]
                    self.waitingForResponse = False
                
                elif message["type"] == "noPips": ##when there is nothing placed on the board when trying to draw a domino
                    self.canDraw = False
                    self.alert.add(UIAlert("You Can Play a Domino",(500,100),30,60))
                    self.waitingForResponse = False
                
                elif message["type"] == "gameEnd": ##sends the score over after game ends
                    self.sendGameMessage("playerScore",{"name":self.name,"score":self.logic.getScore()})

                elif message["type"] == "gameInfo":
                    ##updates UI stuff when game info comes
                    self.board = message["content"]["board"]
                    self.boardOrigin = message["content"]["origin"]
                    if self.playerNum == message["content"]["currentPlayer"]:
                        self.turnText.sprite.changeText("Your Turn")
                    else:
                        self.turnText.sprite.changeText("Not Your Turn")
                    if self.status == "spectator":
                        self.turnText.sprite.changeText("Spectating")
                    # for row in self.board:
                    #     print([str(i) for i in row])
                
                ##===general messages===
                elif message["type"] == "gameResult":
                    ##clears everything and displays the outcome
                    self.status = "end"
                    self.UIBoard.empty()
                    self.UIDashboard.empty()
                    self.selectedDomino.empty()
                    self.drawButton.empty()
                    self.titleScreen.empty()
                    self.turnText.empty()
                    scores = list(message["content"].keys())
                    scores.sort()
                    endString = ""
                    endString+="==========GAME OUTCOME==========\n"
                    for placement,score in enumerate(scores):
                        endString+=f"{placement+1} - {message["content"][score]}\n"
                    endString+="Thanks for playing!"
                    self.waitingScreen.add(UIWaitingScreen(endString))
                    self.waitingForResponse = False

    def checkWin(self):
        ##checks if hand length is 0, if yes send hand empty
        waitUntil(lambda : self.waitingForResponse == False)
        if self.status == "player":
            if self.logic.hand:
                if len(self.logic.hand.getList()) == 0:
                    self.waitingForResponse = True
                    self.sendGameMessage("emptyHandNotif","")
                    self.status = "waitingForResult"

    def textGUI(self):
        ##used for debug, trying to test internet fusion with logic
        action = input("action >> ")
        if action == "place":
            dominoIndex = int(input("index >> "))
            side = input("side >> ")
            angle = int(input("angle >> "))
            coord = input("coord >> ").split(",")
            self.lastPlacedDomino = self.logic.hand.getList()[dominoIndex]
            self.lastPlacedDomino.angle = angle
            if side == "left":
                self.lastPlacedDomino.placeLeft(int(coord[0]),int(coord[1]))
            else:
                self.lastPlacedDomino.placeRight(int(coord[0]),int(coord[1]))

            domino = self.lastPlacedDomino.deconstruct()
            self.sendGameMessage("place",domino)
            self.waitingForResponse = True
        
        elif action == "draw":
            self.sendGameMessage("requestBoardPips","")
            self.waitingForResponse = True
            waitUntil(lambda:self.waitingForResponse == False)
            if not self.logic.hand.hasDominoWithPip(self.boardLeft) and not self.logic.hand.hasDominoWithPip(self.boardRight):
                self.sendGameMessage("draw","")
                self.waitingForResponse = True
            else:
                print("You have playable dominos")

    def shutdown(self):
        ##when shutting down
        self.socket.sendMessage("disconnectClient","")
        self.close()
        
    def close(self):
        ##shuts down without sending the message as the server is closed
        print("closing")
        self.running = False
        pygame.quit()
        self.status = "disconnected"
        self.socket.state = "disconnected"
        self.socket.close()
        sys.exit()

client = DominoesClient()
client.startApplication()
client.updateLoop()