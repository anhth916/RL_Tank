import os
import sys
import time
import base64
import shutil
import datetime
import socketio
import eventlet
import argparse
import threading
import eventlet.wsgi
import numpy as np
import pandas as pd
import configparser


from PIL import Image
from io import BytesIO
from flask import Flask
from threading import Thread
from numpy.lib.function_base import select

from DQNModel import DQN # A class of creating a deep q-learning model
from Memory import Memory # A class of creating a batch in order to store experiences for the training process
from TankEnv import TankEnv # A class of get and save stage send from game environment

tankEnv = TankEnv()

#initialize our client
sio = socketio.Client()

#registering event handler for the client
@sio.event
def connect():
    print("The tank is ready!!! Waiting game starting ...")


@sio.event
def connect_error(data):
    print("The connection to game server failed!")


@sio.event
def disconnect():
    print("Disconnect to game server.")

# called every frame and transfer data from game
@sio.on('radio_tank_1')
def on_message(data):
    tankEnv.get_data(data)
    next_step = tankEnv.next_step()
    if next_step == True:
        action, pos = tankEnv.get_action()
        send_control(action, pos)
    else:
        pass

#send control to game(action:  1 is fire, 0 is move to)
def send_control(action, pos):
    print("Da goi den lenh nay", action, pos)
    sio.emit(
        "radio_tank_1_reply",
        data={
            'action': action.__str__(),
            'pos_x': pos[0].__str__(),
            'pos_y': pos[1].__str__(),
        })

def socket_run():
    config = configparser.ConfigParser()
    config.read(r'C:\Users\Msi\Documents\FSoft_QAI\RL_Tank\game_server.cfg')
    address = config.get('SOCKET', 'SOCKET_CLIENT_ANDDRESS')
    port = config.get('SOCKET', 'SOCKET_PORT')
    sio.connect(address + port)

def train():
    # Create header for saving DQN learning file
    now = datetime.datetime.now() #Getting the latest datetime
    header = ["Ep", "Step", "Reward", "Total_reward", "Action", "Epsilon", "Done", "Termination_Code"] #Defining header for the save file
    filename = "Data/data_" + now.strftime("%Y%m%d-%H%M") + ".csv" 
    with open(filename, 'w') as f:
        pd.DataFrame(columns=header).to_csv(f, encoding='utf-8', index=False, header=True)

    # Parameters for training a DQN model
    N_EPISODE = 1000 #The number of episodes for training
    MAX_STEP = 2000   #The number of steps for each episode
    BATCH_SIZE = 32   #The number of experiences for each replay 
    MEMORY_SIZE = 100000 #The size of the batch for storing experiences
    SAVE_NETWORK = 10  # After this number of episodes, the DQN model is saved for testing later. 
    INITIAL_REPLAY_SIZE = 2000 #The number of experiences are stored in the memory batch before starting replaying
    INPUTNUM = 1606 #The number of input values for the DQN model
    ACTIONNUM = 5  #The number of actions output from the DQN model

    # Initialize a DQN model and a memory batch for storing experiences
    DQNAgent = DQN(INPUTNUM, ACTIONNUM)
    memory = Memory(MEMORY_SIZE)

    train = False #The variable is used to indicate that the replay starts, and the epsilon starts decrease.
    
    while True:
        start = tankEnv.is_game_start()
        if(start == True):
            # print("Start traning!")
            #Training Process
            for episode_i in range(0, N_EPISODE):
                try:
                    # Getting the initial state
                    s = tankEnv.get_stage() #Get the state after reseting. 
                                            #This function (get_state()) is an example of creating a state for the DQN model 
                    total_reward = 0 #The amount of rewards for the entire episode
                    check_end = False #The variable indicates that the episode ends
                    #Start an episde for training
                    for step in range(0, MAX_STEP):
                        
                        act = DQNAgent.act(s)  # Getting an action from the DQN model from the state (s)
                        action, pos = tankEnv.nor_action(act)  # Performing the action in order to obtain the new state
                        tankEnv.send_action(action, pos) #Send action to game
                        time.sleep(0.2) #Sleep a litter bit
                        s_next = tankEnv.get_stage()  # Getting a new state
                        reward = tankEnv.get_reward()  # Getting a reward
                        print("Step game: ", step, "voi action: ", action, "va vi tri: ", pos)
                        check_round = tankEnv.check_round_end() #Checking the end status of round game
                        check_end = tankEnv.check_game_end()  # Checking the end status of the episode game
                        # Add this transition to the memory batch
                        memory.push(s, action, reward, check_end, s_next)

                        # Sample batch memory to train network
                        if (memory.length > INITIAL_REPLAY_SIZE):
                            #If there are INITIAL_REPLAY_SIZE experiences in the memory batch
                            #then start replaying
                            batch = memory.sample(BATCH_SIZE) #Get a BATCH_SIZE experiences for replaying
                            DQNAgent.replay(batch, BATCH_SIZE)#Do relaying
                            train = True #Indicate the training starts
                        total_reward = total_reward + reward #Plus the reward to the total rewad of the episode
                        s = s_next #Assign the next state for the next step.

                        # Saving data to file
                        save_data = np.hstack(
                            [episode_i + 1, step + 1, reward, total_reward, action, DQNAgent.epsilon, check_end]).reshape(1, 7)
                        with open(filename, 'a') as f:
                            pd.DataFrame(save_data).to_csv(f, encoding='utf-8', index=False, header=False)

                        if(check_round == True):
                            time.sleep(2) #Wait next round
                            print("Next Round...")
                        
                        if check_end == True:
                            print("Ket thuc episode ", episode_i, "!")
                            time.sleep(3) #Sleep 3 second wait the next game
                            #If the episode ends, then go to the next episode
                            break

                    # Iteration to save the network architecture and weights
                    if (np.mod(episode_i + 1, SAVE_NETWORK) == 0 and train == True):
                        DQNAgent.target_train()  # Replace the learning weights for target model with soft replacement
                        #Save the DQN model
                        now = datetime.datetime.now() #Get the latest datetime
                        DQNAgent.save_model("C:\\Users\\Msi\\Documents\\FSoft_QAI\\RL_Tank\\Train\\SaveModel\\",
                                            "DQNmodel_" + now.strftime("%Y%m%d-%H%M") + "_ep" + str(episode_i + 1))
                    
                    #Print the training information after the episode
                    print('Episode %d ends. Number of steps is: %d. Accumulated Reward = %.2f. Epsilon = %.2f .Termination code: %d' % (
                        episode_i + 1, step + 1, total_reward, DQNAgent.epsilon, check_end))
                    
                    #Decreasing the epsilon if the replay starts
                    if train == True:
                        DQNAgent.update_epsilon()

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    break
            print("Finished.")
            break
        else:
            print("Waiting game start...")

if __name__ == '__main__':
    try:
        t = time.time()
        # creating thread
        t1 = threading.Thread(target=socket_run)
        t2 = threading.Thread(target=train)
        # starting thread
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        # both threads completely executed
        print("End!")
    except:
        print ("Thearding Error!")
