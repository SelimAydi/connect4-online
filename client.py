import turtle
from socket import *
import threading
import pickle
import config
import keyboard  # Using module keyboard

request_lock = threading.Lock()

config = config.Config()

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.can_start = False
        self.player_num = 0
        self.client_id = 0

        self.colors = {0: ""}
        self.can_draw = False

        # game stuff
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(500)
        self.window = turtle.Screen()
        self.window.bgcolor("lightgrey")
        self.pen.speed(0)
        self.myPen._tracer(8, 25)

        self.connect4_cell_list = []
        self.players = []

        self.my_turn = False
        self.my_move = None
        self.winner = 0


    def play(self):
        # self.game = Connect4Game.Connect4Game()
        self.enter_lobby()
                # self.init_game()

        self.test_game_loop()

    def enter_lobby(self):
        print("Waiting for players..")
        self.initialize_grid()
        while not self.can_start:
            pass

        print("Two players available. Starting game..")
        if self.client_id == 1:
            self.my_turn = True

    def connect(self):
        print("Connecting to the server...")

        try:
            self.clientSocket.connect((self.host, self.port))
            self.connected = True
        except:
            print("Could not connect to the server!")

        print("Succesfully connected.")
        while 1:
            received = self.clientSocket.recv(4096)

            if not received:
                break

            try:
                received_message = received.decode('UTF-8').strip()

                print("Received from server: {}\n".format(received_message))
                if received_message == "start":
                    print("Can now start the game!")
                    self.can_start = True
                elif received_message == "1":
                    self.client_id = 1
                    print("Assigned myself as client 1")
                elif received_message == "2":
                    self.client_id = 2
                    print("Assigned myself as client 2")
                elif received_message.startswith("winner"):
                    self.winner = int(received_message.split('=')[1])
                    print("SELF.WINNER SET")
                elif received_message == "turn":
                    print("getting turn")
                    self.get_turn()
            except:
                print("Client received payload!")

                # means we're getting bytedata
                grid = pickle.loads(received)
                print("Grid...", grid)
                print("Type grid ", type(grid))
                self.connect4_cell_list = grid
                self.can_draw = True
                print("Setting can_draw to true")
                self.my_turn = not self.my_turn
                print("I am client {0} and is it my turn? {1}".format(self.client_id, self.my_turn))

        self.clientSocket.close()

    def disconnect(self):
        self.clientSocket.close()

    def send_request(self, request):
        with request_lock:
            while not self.connected:
                pass
            self.clientSocket.send(request.encode())

    def get_turn(self):
        self.my_turn = True

    def check_players(self):
        return self.send_request("/online")

    def ping_server(self):
        self.send_request("/ping")

    def draw_grid(self, grid):
        self.pen.setheading(0)
        self.pen.goto(-350, 130)
        for rower in range(0, 6):
            for col in range(0, 7):
                if grid[rower][col] == 0:
                    self.pen.fillcolor("#FFFFFF")
                elif grid[rower][col] == 2:
                    self.pen.fillcolor("#FF0000")
                elif grid[rower][col] == 1:
                    self.pen.fillcolor("#FFFF00")

                self.pen.begin_fill()
                self.pen.circle(25)
                self.pen.end_fill()

                self.pen.penup()
                self.pen.forward(58)
                self.pen.pendown()
            self.pen.setheading(270)
            self.pen.penup()
            self.pen.forward(58)
            self.pen.setheading(180)
            self.pen.forward(58 * 7)
            self.pen.setheading(0)
            self.pen.getscreen().update()

    def draw_board(self):
        self.pen.up()
        self.pen.setheading(0)
        self.pen.goto(-386, -200)
        self.pen.begin_fill()
        for b in range(4):
            self.pen.color("blue")
            self.pen.pendown()
            self.pen.forward(420)
            self.pen.left(90)
        self.pen.up()
        self.pen.end_fill()

    def draw_gamepanel(self):
        self.pen.up()
        self.pen.setheading(0)
        self.pen.goto(80, 219)
        self.pen.begin_fill()
        for rectangle in range(2):
            self.pen.color("white")
            self.pen.down()
            self.pen.forward(250)
            self.pen.right(90)
            self.pen.forward(418)
            self.pen.right(90)
        self.pen.end_fill()
        self.pen.up()
        self.myPen.color("black")
        self.myPen.goto(-150, 250)
        self.myPen.write("CONNECT 4", True, align="center", font=("Arial", 40, "bold"))

    def check_if_winner(self, grid, color):
        # Vertical row checking
        for r in range(6):
            for c in range(4):
                if grid[r][c] == color and grid[r][c + 1] == color and grid[r][c + 2] == color and grid[r][c + 3] == color:
                    return color
        # Horizontal row checking
        for x in range(3):
            for y in range(7):
                if grid[x][y] == color and grid[x + 1][y] == color and grid[x + 2][y] == color and grid[x + 3][y] == color:
                    return color
        # Diagonal checking
        for i in range(3):
            for z in range(4):
                if grid[i][z] == color and grid[i + 1][z + 1] == color and grid[i + 2][z + 2] == color and grid[i + 3][z + 3] == color:
                    return color

        #diagonal checking
        for d in range(5,2,-1):
            for c in range(4):
                if grid[d][c] == color and grid[d-1][c+1] == color and grid[d-2][c+2] == color and grid[d-3][c+3] == color:
                    return color
        return 0

    def winner_screen(self, winner):
        # winner_dict = {"YELLOW": 1, "RED": 2}

        self.pen.penup()
        self.pen.color("black")
        self.pen.goto(200, 150)
        self.pen.write("{} WINS".format(winner), True, align="center", font=("Arial", 20, "bold"))
        self.pen.getscreen().update()

        print(self.connect4_cell_list)
        self.draw_global()
        user_input = input("Type 'quit' to quit the game\n")
        game_over = True
        while game_over:
            if user_input == 'quit':
                game_over = False
            else:
                user_input = input("Type 'quit' to quit the game\n")

    def initialize_grid(self):
        # Initialise empty 6 by 7 connect4 grid
        for rows in range(0, 6):
            self.connect4_cell_list.append([])
            for cols in range(0, 7):
                self.connect4_cell_list[rows].append(0)

        self.draw_gamepanel()
        self.draw_board()
        self.draw_grid(self.connect4_cell_list)


    def wait_for_turn(self):
        print("waiting for my turn!!")
        while not self.my_turn:
            pass

    def test_game_loop(self):
        print("entering game loop")

        for i in range(1, 43):

            self.wait_for_turn()

            self.draw_grid(self.connect4_cell_list)

            if self.winner > 0:
                if self.winner == 2:
                    self.winner_screen("RED")
                    break
                self.winner_screen("YELLOW")
                break

            user_input = self.window.numinput("Your turn", "Pick column number:", 0, minval=1, maxval=7)
            self.my_move = user_input
            print("PLAYER MADE MOVE: {}".format(self.my_move))


            chosen_cell = int(user_input)
            column_minus = chosen_cell - 1

            # Column full
            while self.connect4_cell_list[0][column_minus] != 0:
                user_input = self.window.numinput("Your turn", "Pick other column number row is full:", 1, minval=1,
                                             maxval=7)
                chosen_cell = int(user_input)
                column_minus = chosen_cell - 1

            # Make the chip slide to the bottom of the board, row starting from 5 then minus 1
            row = 5
            while self.connect4_cell_list[row][column_minus] != 0:
                row = row - 1

            # Find out the colour of the current player (1 or 2)
            playerColor = self.client_id

            # Place the token on the grid
            self.connect4_cell_list[row][column_minus] = playerColor

            # Draw the grid
            self.draw_grid(self.connect4_cell_list)

            winner = self.check_if_winner(self.connect4_cell_list, playerColor)
            if winner == 2:
                winnerdata = "winner=2"
                self.clientSocket.send(winnerdata.encode())
                self.winner_screen("RED")
                break
            elif winner == 1:
                winnerdata = "winner=1"
                self.clientSocket.send(winnerdata.encode())
                self.winner_screen("YELLOW")
                break
            # self.draw_grid(self.connect4_cell_list)
            self.draw_global()

        print("Game over!")
            # self.my_turn = False

    # def game_loop(self):
    #
    #     for turn in range(1, 43):
    #
    #         if self.winner > -1:
    #             self.winner_screen(self.winner)
    #
    #         self.wait_for_turn()
    #
    #         # wait for player request
    #         user_input = self.window.numinput("Your turn", "Pick column number:", 0, minval=1, maxval=7)
    #
    #         if not user_input:
    #             break
    #
    #         self.my_move = user_input
    #
    #         # self.client.send_request(str(user_input))
    #
    #         chosen_cell = int(user_input)
    #         column_minus = chosen_cell - 1
    #
    #         # Column full
    #         while self.connect4_cell_list[0][column_minus] != 0:
    #             user_input = self.window.numinput("Your turn", "Pick other column number row is full:", 1, minval=1,
    #                                          maxval=7)
    #             chosen_cell = int(user_input)
    #             column_minus = chosen_cell - 1
    #
    #         # Make the chip slide to the bottom of the board, row starting from 5 then minus 1
    #         row = 5
    #         while self.connect4_cell_list[row][column_minus] != 0:
    #             row = row - 1
    #
    #         # Find out the colour of the current player (1 or 2)
    #         playerColor = int((turn % 2) + 1)
    #
    #         # Place the token on the grid
    #         self.connect4_cell_list[row][column_minus] = playerColor
    #
    #         # Draw the grid
    #         self.draw_grid(self.connect4_cell_list)
    #
    #         winner = self.check_if_winner(self.connect4_cell_list, playerColor)
    #         if winner == 2:
    #             self.winner_screen("RED")
    #             break
    #         elif winner == 1:
    #             self.winner_screen("YELLOW")
    #             break
    #         # self.draw_grid(self.connect4_cell_list)
    #         self.draw_global()

    def draw_global(self):
        print("---------------------drawglobal function")

        # self.draw_grid(self.connect4_cell_list)
        data_string = pickle.dumps(self.connect4_cell_list)
        with request_lock:
            while not self.connected:
                pass
            print("---------------------sending from drawglobal")
            self.clientSocket.send(data_string)

        while not self.can_draw:
            pass

        print("out of can draw loop and drawing right now------")
        self.draw_grid(self.connect4_cell_list)
        self.can_draw = False

client = Client(config.host, config.port)

client_handler = threading.Thread(target=client.connect)
client_handler.start()
client.play()


# client = Client(config.host, config.port)
# client_handler = threading.Thread(target=client.connect)
# client_handler.daemon = True
# client_handler.start()

# thr1 = threading.Thread(target=client.check_players)
# thr2 = threading.Thread(target=client.ping_server)
# client.check_players()
# client.ping_server()

# thr1.start()
# thr1.join()
# thr2.start()

# client.connect()

# client.check_players()
