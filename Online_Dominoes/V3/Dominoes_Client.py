from config import *
from Socket_Client import SocketClient
from Dominoes_Logic import *
from threading import Thread
from util import *
import sys
from Dominoes_UI import *
import pygame

class DominoesClient:
    def __init__(self):
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
        self.viewingOrigin = (0,0)
        self.UIBoard = pygame.sprite.GroupSingle()
        self.UIDashboard = pygame.sprite.GroupSingle()
        self.selectedDomino = pygame.sprite.GroupSingle()
        self.titleScreen = pygame.sprite.GroupSingle()
        self.waitingScreen = pygame.sprite.GroupSingle()
        self.drawButton = pygame.sprite.GroupSingle()
        self.turnText = pygame.sprite.GroupSingle()
    
    def startApplication(self):
        self.name = input("Enter your name: ")
        self.initScreen()
        self.titleScreen.add(UITitleScreen())
        self.status = "title"
    
    def joinGame(self):
        self.status = "joining"
        self.socket.connect()
        Thread(target=self.listenToServer, daemon=True).start()
        waitUntil(lambda: self.status != "joining")
        if self.status == "player":
            self.joinPlayer()
        elif self.status == "spectator":
            self.joinSpectator()
        elif self.status == "denied":
            self.close()
        print("Joined!")
        self.waitingScreen.empty()
        self.waitingScreen.add(UIWaitingScreen("Connected!"))
        if self.status == "spectator":
            self.waitingScreen.empty()
            self.UIBoard.add(UIBoard())
            self.turnText.add(UIText("Spectating",TURN_TEXT_POSITION,15))

    def initScreen(self):
        self.screen  = pygame.display.set_mode((SCREEN_DIMENSIONS[0] * TILE_DIMENSIONS[0], SCREEN_DIMENSIONS[1] * TILE_DIMENSIONS[1]+DASHBOARD_DIMENSIONS))
        self.clock = pygame.time.Clock() 

    def draw(self):
        self.screen.fill('#000000')
        self.UIBoard.draw(self.screen)
        self.UIDashboard.draw(self.screen)
        self.selectedDomino.draw(self.screen)
        self.drawButton.draw(self.screen)
        self.turnText.draw(self.screen)
        self.titleScreen.draw(self.screen)
        self.waitingScreen.draw(self.screen)
    
    def updateDisplay(self):
        self.selectedDomino.update()
        if self.board and self.boardOrigin:
            self.UIBoard.update(self.board,self.boardOrigin)
            self.UIDashboard.update()
        self.draw()
        pygame.display.update()
    
    def updateLoop(self):
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
    
    def waitingForPlayersScreen(self):
        self.waitingScreen.empty()
        self.waitingScreen.add(UIWaitingScreen("Waiting For Other Players..."))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()

    def titleUpdate(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.titleScreen.sprite.isHoveringStart(event.pos):
                    self.status = "start"
                    self.titleScreen.empty()
                    self.waitingScreen.add(UIWaitingScreen("Joining Game..."))
                
                elif self.titleScreen.sprite.isHoveringInstruction(event.pos):
                    self.status = "instructions"
                    self.titleScreen.empty()
                    self.waitingScreen.add(UIWaitingScreen(INSTRUCTIONS,15))
    
    def instructionUpdate(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.status = "title"
                    self.waitingScreen.empty()
                    self.titleScreen.add(UITitleScreen())

    def playerUpdate(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.shutdown()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.selectedDomino.sprite:
                    if self.UIDashboard.sprite.isHovering(event.pos):
                        self.selectedDomino.sprite.resetDirection()
                        self.UIDashboard.sprite.dominoes.add(self.selectedDomino.sprite)
                        self.selectedDomino.empty()
                    else:
                        print(self.selectedDomino.sprite.getPips())
                        self.lastPlacedDomino = self.logic.getLogicDomino(self.selectedDomino.sprite.getPips())
                        self.lastPlacedDomino.angle = self.selectedDomino.sprite.angle
                        cell = getLeftPipDominoCell(event.pos[0],event.pos[1],self.lastPlacedDomino)
                        cell = (cell[0]-self.UIBoard.sprite.origin[0],cell[1]-self.UIBoard.sprite.origin[1])
                        print(f"cell: {cell}")
                        self.lastPlacedDomino.placeLeft(cell[0],cell[1])
                        self.sendGameMessage("place",self.lastPlacedDomino.deconstruct())
                
                elif self.drawButton.sprite.isHovering(event.pos):
                    print("clicked draw")
                    self.sendGameMessage("requestBoardPips","")
                    self.waitingForResponse = True
                    waitUntil(lambda:self.waitingForResponse == False or self.running == False)
                    if not self.logic.hand.hasDominoWithPip(self.boardLeft) and not self.logic.hand.hasDominoWithPip(self.boardRight):
                        self.sendGameMessage("draw","")
                        self.waitingForResponse = True
                    else:
                        print("You have playable dominos")
                        print(f"hand: {self.logic.hand}")
                else:
                    self.selectedDomino.add(self.UIDashboard.sprite.getHovering(event.pos))
                    if self.selectedDomino.sprite:
                        self.selectedDomino.sprite.setAbsPos(event.pos)
                        self.UIDashboard.sprite.removeDomino(self.selectedDomino.sprite)

            if event.type == pygame.MOUSEMOTION:
                if self.selectedDomino.sprite:
                    self.selectedDomino.sprite.setAbsPos(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if self.selectedDomino.sprite:
                    if event.key == pygame.K_z:
                        self.selectedDomino.sprite.rotateCounterclockwise()
                    
                    if event.key == pygame.K_x:
                        self.selectedDomino.sprite.rotateClockwise()
                    
                if event.key == pygame.K_UP:
                    self.UIBoard.sprite.scrollUp()
                if event.key == pygame.K_DOWN:
                    self.UIBoard.sprite.scrollDown()
                if event.key == pygame.K_LEFT:
                    self.UIBoard.sprite.scrollLeft()
                if event.key == pygame.K_RIGHT:
                    self.UIBoard.sprite.scrollRight()

        if self.logic:
            self.checkWin()

    def spectatorUpdate(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()

    def joinPlayer(self):
        # print("Client: You are a player")
        # input("Press Enter to join the game...")
        pygame.display.set_caption("Dominoes: Player")
        self.socket.sendMessage("join", {"type": "player", "name": self.name})
    
    def joinSpectator(self):
        # print("Client: You are a spectator")
        # input("Press Enter to spectate the game...")
        pygame.display.set_caption("Dominoes: Spectator")
        self.socket.sendMessage("join", {"type": "spectator"})
    
    def sendGameMessage(self,action,content):
        """
        Possible game messages from client:
         - sending over domino to place
        """
        if isinstance(content,Domino):
            content = content.deconstruct()
        self.socket.sendMessage("game",{"num":self.playerNum} | {"action":action,"content":content})

    def listenToServer(self):
        while self.socket.state == "connected":
            message = self.socket.receiveMessage()
            if message:
                if message["type"] == "connectedPlayer":
                    self.status = "player"

                elif message["type"] == "connectedSpectator":
                    self.status = "spectator"

                elif message["type"] == "denyConnection":
                    print("Server at max capacity")
                    self.status = "denied"

                elif message["type"] == "confirm":
                    if message["content"] != "":
                        # print(f"Client: Server confirmation, you are player {message['content']['playerCount']}")
                        if not self.playerNum:
                            self.playerNum = int(message['content']['playerCount'])
                        self.UIBoard.add(UIBoard())
                        self.UIDashboard.add(UIDashboard())
                        self.drawButton.add(UIButton("Draw",DRAW_BUTTON_COORDINATES,DRAW_BUTTON_DIMENSIONS,DRAW_BUTTON_COLOR,15))
                        self.turnText.add(UIText("",TURN_TEXT_POSITION,15))
                    else:
                        # print("Client: Server confirmation, you are a spectator")
                        pass
                
                elif message["type"] == "gameStart":
                    self.waitingForPlayers = False
                    self.waitingScreen.empty()

                elif message["type"] == "shutdown" or message["type"] == "close":
                    # print("Client: Disconnecting...")
                    self.running = False

                elif message["type"] == "hand":
                    deconstructedHand = message["content"]
                    reconstructedHand = []
                    for domino in deconstructedHand:
                        temp = Domino(0,0)
                        temp.reconstruct(domino)
                        reconstructedHand.append(temp)
                    hand = Hand(reconstructedHand)
                    self.logic = ClientLogic(hand)
                    self.UIDashboard.sprite.setDominoes(reconstructedHand)
                    self.waitingScreen.empty()
                    
                elif message["type"] == "placementFailure":
                    self.waitingForResponse = False
                    print("Failed to place")
                    self.lastPlacedDomino = None
                    
                elif message["type"] == "placementSuccess":
                    self.waitingForResponse = False
                    self.logic.hand.removeDomino(self.lastPlacedDomino)
                    self.selectedDomino.empty()
                    print("Placement success")
                
                elif message["type"] == "draw":
                    recvDomino = message["content"]
                    temp = Domino(0,0)
                    temp.reconstruct(recvDomino)
                    self.logic.hand.addDomino(temp)
                    self.UIDashboard.sprite.addDomino(temp)
                    self.waitingForResponse = False
                    
                elif message["type"] == "drawFailure":
                    print("Nothing to draw from")
                    self.waitingForResponse = False

                elif message["type"] == "notYourTurn":
                    print("It is not your turn")
                    self.waitingForResponse = False
                
                elif message["type"] == "pips":
                    self.boardLeft = message["content"]["left"]
                    self.boardRight = message["content"]["right"]
                    self.waitingForResponse = False
                
                elif message["type"] == "noPips":
                    print("There are no dominos placed on the board")
                    self.waitingForResponse = False
                
                elif message["type"] == "gameEnd":
                    self.sendGameMessage("playerScore",{"name":self.name,"score":self.logic.getScore()})

                elif message["type"] == "gameInfo":
                    self.board = message["content"]["board"]
                    self.boardOrigin = message["content"]["origin"]
                    if self.playerNum == message["content"]["currentPlayer"]:
                        print(self.turnText.sprite)
                        self.turnText.sprite.changeText("Your Turn")
                    else:
                        self.turnText.sprite.changeText("Not Your Turn")
                    if self.status == "spectator":
                        self.turnText.sprite.changeText("Spectating")
                    # for row in self.board:
                    #     print([str(i) for i in row])
                
                ##===general messages===
                elif message["type"] == "gameResult":
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
        waitUntil(lambda : self.waitingForResponse == False)
        if self.status == "player":
            if self.logic.hand:
                if len(self.logic.hand.getList()) == 0:
                    self.waitingForResponse = True
                    self.sendGameMessage("emptyHandNotif","")
                    self.status = "waitingForResult"

    def textGUI(self):
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
        self.socket.sendMessage("disconnectClient","")
        self.close()
        
    def close(self):
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