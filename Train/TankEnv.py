import numpy as np

obstacleID = -1
shellID = -10

class TankEnv:
    def __init__(self):
        self.game_start = False
        self.playerID = 0
        self.playerPos = []
        self.pre_playerHealth = 0
        self.playerHealth = 0
        self.enemyPos = []
        self.pre_enemyHealth = 0
        self.enemyHealth = 0
        self.shells = []
        self.obstacles = []
        self.result = []
        self.round_number = 0
        self.map2D = None
        self.action = 0
        self.action_pos = []
        self.pre_step = 0
        self.step = 0
    
    #The funtion get data from game environment
    def get_data(self, data):
        self.playerID = data["playerID"]
        self.playerPos = data["pos"]
        if(len(self.playerPos) > 0):
            self.game_start = True
        self.pre_playerHealth = self.playerHealth
        self.playerHealth = data["health"]
        self.enemyPos = data["enemy_pos"] 
        self.pre_enemyHealth = self.enemyHealth
        self.enemyHealth = data["enemy_health"]
        self.shells = data["shells"]
        self.obstacles = data["obstacles"]
        self.result = data["result"]
        self.round_number = data["round_number"]

    #The fuction to know when game environment already
    def is_game_start(self):
        return self.game_start

    #Function convert pos from game map to numpy map
    def convert_pos(self, posX, posY):
        x = abs(posX)
        y = abs(posY)
        new_posX = 0
        new_posY = 0
        #first quadrant
        if (posX > 0) and (posY > 0):
            new_posX = 20 + x
            new_posY = 20 - y
        #second quadrant
        elif (posX < 0) and (posY > 0):
            new_posX = 20 - x
            new_posY = 20 - y
        #third quadrant
        elif (posX < 0) and (posY < 0):
            new_posX = 20 - x
            new_posY = 20 + y
        #fourth quadrant
        elif (posX > 0) and (posY < 0):
            new_posX = 20 + x
            new_posY = 20 + y
        #(0,0)
        else:
            new_posX = 20
            new_posY = 20

        return new_posX, new_posY 

    #The function return stage
    def get_stage(self):
        #Build 2D map. The game evronment build with Oxy from -20 to 20 with type float.
        #                    20
        #     _______________________________
        #     |              |               |
        #     |              |               |
        #     |              |               |
        #     |              |               |
        #     |              |               |
        # -20 |______________|_______________| 20
        #     |              |               |
        #     |              |               |
        #     |              |               |
        #     |              |               |
        #     |              |               |
        #     |______________|_______________|
        #                   -20
        #
        #                   To    
        #   0 _______________________________ 40
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |                              |
        #     |______________________________|
        #    40               
        #But i will convert all to int for model easyer learning
        #Empy box: 0, obstacles: 1, shell: 10
        map = np.zeros([40,40], dtype=int)

        #Add pos of obstacles into 2D map
        try:
            for ob in self.obstacles:
                pos_ob = self.obstacles.get(ob)
                xmin = int(float(pos_ob.get("xmin")))
                xmax = int(float(pos_ob.get("xmax")))
                ymin = int(float(pos_ob.get("ymin")))
                ymax = int(float(pos_ob.get("ymax")))
                xmin, ymax = self.convert_pos(xmin, ymax)
                xmax, ymin = self.convert_pos(xmax, ymin)
                for i in range (xmin, xmax + 1, 1):
                    for j in range (ymin, ymax + 1, 1):
                        map[i][j] = obstacleID
        except:
            print("Had error when add pos of obstacles to 2D map")
        #Add pos of shell if exits into 2D map
        if len(self.shells) > 0:
            try:
                for shell in self.shells:
                    pos_shell = self.shells.get(shell)
                    init_pos = pos_shell.get("init_pos")
                    cur_pos = pos_shell.get("cur_pos")
                    x_init = int(float(init_pos.get("x")))
                    y_init = int(float(init_pos.get("y")))
                    x_cur = int(float(cur_pos.get("x")))
                    y_cur = int(float(cur_pos.get("y")))
                    x_init, y_init = self.convert_pos(x_init, y_init)
                    x_cur, y_cur = self.convert_pos(x_cur, y_cur)
                    if(x_init > x_cur):
                        xmax = x_init
                        xmin = x_cur
                    else:
                        xmax = x_cur
                        xmin = x_init
                    if(y_init > y_cur):
                        ymax = y_init
                        ymin = y_cur
                    else:
                        ymax = y_cur
                        ymin = y_init
                    for i in range (xmin, xmax + 1, 1):
                        for j in range (ymin, ymax + 1, 1):
                            map[i][j] = shellID
            except:
                print("Had error when add pos of shell if exits into 2D map")
        else:
            pass
        #Save map
        self.map2D = map
        #Flattening the map matrix to a vector
        DQNState = map.flatten().tolist()
        # Add position and health of agent to the DQNState
        playerPosX, playerPosY = self.convert_pos(int(float(self.playerPos.get("x"))), int(float(self.playerPos.get("y"))))
        DQNState.append(playerPosX)
        DQNState.append(playerPosY)
        DQNState.append(int(float(self.playerHealth)))
        # Add position and health of enemy to the DQNState
        enemyPosX, enemyPosY = self.convert_pos(int(float(self.enemyPos.get("x"))), int(float(self.enemyPos.get("y"))))
        DQNState.append(enemyPosX)
        DQNState.append(enemyPosY)
        DQNState.append(int(float(self.enemyHealth)))
        #Convert the DQNState from list to array for training
        DQNState = np.array(DQNState)
        #Return Stage
        return DQNState

    #The function calulator reward for each stage
    def get_reward(self):
        reward = 0

        playerPosX, playerPosY = self.convert_pos(int(float(self.playerPos.get("x"))), int(float(self.playerPos.get("y"))))

        #agent tank dive into obstacles
        try:
            if(self.map2D[playerPosX][playerPosY] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX - 1][playerPosY - 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX][playerPosY - 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX + 1][playerPosY - 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX + 1][playerPosY] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX + 1][playerPosY + 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX][playerPosY + 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX - 1][playerPosY + 1] == obstacleID):
                reward -= 1
            elif(self.map2D[playerPosX - 1][playerPosY] == obstacleID):
                reward -= 1
            else:
                pass
        except:
            pass

        #agent tank drive into shell zone
        try:    
            if(self.map2D[playerPosX][playerPosY] == shellID):
                reward -= 5
        except:
            pass
        #agent tank hit
        if(self.playerHealth < self.pre_playerHealth):
            reward -= 20
        
        #agent tank die
        if(self.playerHealth <= 0):
            reward -= 50

        #enemy tank hit
        if(self.enemyHealth < self.pre_enemyHealth):
            reward += 20
        
        #enemy tank die
        if(self.enemyHealth <= 0):
            reward += 50
        return reward

    #Function check round end
    def check_round_end(self):
        if (self.playerHealth <= 0) or (self.enemyHealth <= 0):
            return True
        else:
            return False
        
    #Function check game end
    def check_game_end(self):
        player = int(self.result.get("player"))
        enemy = int(self.result.get("enemy"))
        if(player >= 5) or (enemy >= 5):
            return True
        else:
            return False
    
    #Function check win game
    def check_win(self):
        #0: PLAYING, 1: WIN, 2: LOSE
        player = int(self.result.get("player"))
        enemy = int(self.result.get("enemy"))
        if player >= 5:
            return 1
        elif enemy >= 5:
            return 2
        else:
            return 0

    #Function normalization action for agent
    def nor_action(self, act):
        act = int(act)
        playerPosX = int(float(self.playerPos.get("x"))) 
        playerPosY = int(float(self.playerPos.get("y")))
        enemyPosX = int(float(self.enemyPos.get("x")))
        enemyPosY = int(float(self.enemyPos.get("y")))
        if(act == 4):
            #Type 1: Action = 1 : SHOOT (I hardset, if Agent want shoot, it will shoot into current enemy pos)
            #4: Shoot into the enemy pos
            action = 1
            pos = [enemyPosX, enemyPosY] 
        else:
            #Type 2: Action = 0 : MOVE
            action = 0
            #0: Move up 2 box
            pos = [playerPosX, playerPosY - 2]
            #1: Move back 2 box
            pos = [playerPosX, playerPosY + 2]
            #2: Move left 2 box
            pos = [playerPosX - 2, playerPosY]
            #3: Move right 2 box
            pos = [playerPosX + 2, playerPosY]
        return action, pos

    #Fuction save action and pos for server get action
    def send_action(self, action, pos):
        self.step += 1
        self.action = action
        self.action_pos = pos
    
    #Fuction for server get action
    def get_action(self):
        return self.action, self.action_pos

    #Function check jump to next step or not
    def next_step(self):
        if(self.pre_step < self.step):
            self.pre_step = self.step
            return True
        else:
            return False

