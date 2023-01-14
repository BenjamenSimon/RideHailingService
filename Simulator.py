# Simulator

## This script is imported to run the simulator in different notebooks


## Import Packages

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import random

## Load Data

pay_prob_df = pd.read_csv('Data/probs.csv', names = ['PAY', 'PROB'], header = 0)


## Create the results arrays

def create_users_df(num_riders):
    
    users = {'USER_ID': np.arange(1, num_riders+1),
          'ACTIVE': np.repeat(0, num_riders),
          'REQ_M1': np.repeat(0, num_riders),
          'REQ_M2': np.repeat(0, num_riders),
          'REQ_M3': np.repeat(0, num_riders),
          'REQ_M4': np.repeat(0, num_riders),
          'REQ_M5': np.repeat(0, num_riders),
          'REQ_M6': np.repeat(0, num_riders),
          'REQ_M7': np.repeat(0, num_riders),
          'REQ_M8': np.repeat(0, num_riders),
          'REQ_M9': np.repeat(0, num_riders),
          'REQ_M10': np.repeat(0, num_riders),
          'REQ_M11': np.repeat(0, num_riders),
          'REQ_M12': np.repeat(0, num_riders),
          'RATE_M1': np.repeat(0, num_riders),
          'RATE_M2': np.repeat(0, num_riders),
          'RATE_M3': np.repeat(0, num_riders),
          'RATE_M4': np.repeat(0, num_riders),
          'RATE_M5': np.repeat(0, num_riders),
          'RATE_M6': np.repeat(0, num_riders),
          'RATE_M7': np.repeat(0, num_riders),
          'RATE_M8': np.repeat(0, num_riders),
          'RATE_M9': np.repeat(0, num_riders),
          'RATE_M10': np.repeat(0, num_riders),
          'RATE_M11': np.repeat(0, num_riders),
          'RATE_M12': np.repeat(0, num_riders),
          'RATE_M13': np.repeat(0, num_riders)
          }

    users_df = pd.DataFrame(users) 
    
    return(users_df)


def create_rides_df():
    
    rides = {'USER_ID': [],
          'MONTH': [],
          'RIDE_ID': [],
          'ACCEPTED': [],
          'PAY': [],
          'PROFIT': []
          }

    rides_df = pd.DataFrame(rides)
    
    return(rides_df)


## The process

### Generate new active users

def generate_new_active_users(month, users_df):
    
    lower = (month - 1) * 1000
    upper = (month) * 1000
    
    # Flag new users as active
    users_df.ACTIVE[lower:upper] = 1

    # This is the rate at which the new users request rides
    users_df["RATE_M"+f"{month}"][lower:upper] = 1
    
    return(users_df)



### Find active users

def find_active_users(users_df):
    
    # These users are active and will generate requests
    active_users = users_df.index[users_df.ACTIVE == 1]

    # This is the number of active users
    num_active_users = len(active_users)
    
    return(active_users, num_active_users, users_df)



### Generate requests

def generate_requests(active_users, num_active_users, month, users_df):
    
    # This is the rate at which active users request new rides
    rate = users_df["RATE_M"+f"{month}"][active_users]

    # These are the number of requests per user this month
    users_df["REQ_M"+f"{month}"][active_users] = random.poisson(lam=rate, size = num_active_users)

    # These are the active users with 0 requests
    non_returning_users = active_users[users_df["REQ_M"+f"{month}"][active_users] == 0]

    # Set these users to never active again
    users_df.ACTIVE[non_returning_users] = -1

    # These are the users with requests greater than 0
    users_requesting = users_df.index[users_df["REQ_M"+f"{month}"] > 0]

    # These are the requests that we need to generate acceptances for
    requests_oi = users_df["REQ_M"+f"{month}"][users_requesting]
    
    return(users_requesting, requests_oi, users_df)



### Generate acceptances: Fixed rate

def generate_acceptances_individually(users_requesting, pay, pay_probs, month, users_df, rides_df):
    
    # Extract the number of rides of each user
    ids_and_requests = users_df.loc[users_requesting, ['USER_ID', "REQ_M"+f"{month}"]]

    # Calculate the total number of rides requested
    num_rides = sum(ids_and_requests["REQ_M"+f"{month}"])

    # Set up an array to store the results
    rides_this_month = np.zeros((num_rides, len(rides_df.columns)))

    # A count of the number of rides processed
    ride_row = 0
    
    # Look up the acceptance probability of the Pay
    prob_acc = pay_probs.PROB[pay_probs.PAY == pay].values[0]

    # Loop through each ride and generate if it accepted or not
    # and how the Pay, and store the results in the temp array
    for row in range(0, len(ids_and_requests)):
        user_id_j = ids_and_requests.USER_ID.iloc[row]
        requests_j = ids_and_requests["REQ_M"+f"{month}"].iloc[row]
        
        total_acc_j = 0
        
        for ride in range(1, requests_j+1):
            acc_j_r = random.random() < prob_acc
            rides_this_month[ride_row, :] = [user_id_j, month, ride, acc_j_r, pay, 30-pay]
            ride_row = ride_row + 1
            total_acc_j = total_acc_j + acc_j_r
            
        users_df["RATE_M"+f"{month+1}"][users_requesting[row]] = total_acc_j
            
    # These are the users that had none of their ride requests accepted this month
    non_returning_users_2 = users_requesting[users_df["RATE_M"+f"{month+1}"][users_requesting] == 0]

    # Set these users to never active again
    users_df.ACTIVE[non_returning_users_2] = -1        
        
    # Convert the temp ride array to a data frame        
    rides_this_month_df = pd.DataFrame(rides_this_month, columns=rides_df.columns)        

    # Append the temp array to the rides results df
    rides_df = pd.concat([rides_df, rides_this_month_df], ignore_index=True)
    
    return(users_df, rides_df)



### Generate acceptances: Adaptive rate

def generate_acceptances_adaptive(users_requesting, pays, probs, pay_probs, month, users_df, rides_df):
    
    # Extract the number of rides of each user
    ids_and_requests = users_df.loc[users_requesting, ['USER_ID', "REQ_M"+f"{month}"]]

    # Calculate the total number of rides requested
    num_rides = sum(ids_and_requests["REQ_M"+f"{month}"])

    # Set up an array to store the results
    rides_this_month = np.zeros((num_rides, len(rides_df.columns)))

    # A count of the number of rides processed
    ride_row = 0
    

    # Loop through each ride and generate if it accepted or not
    # and how the Pay, and store the results in the temp array
    for row in range(0, len(ids_and_requests)):
        user_id_j = ids_and_requests.USER_ID.iloc[row]
        requests_j = ids_and_requests["REQ_M"+f"{month}"].iloc[row]
        
        total_acc_j = 0

        for ride in range(1, requests_j+1):
            if total_acc_j > 0:
                pay = pays[1]
                prob_acc = probs[1]
            else:
                pay = pays[0]
                prob_acc = probs[0]
                
            acc_j_r = random.random() < prob_acc
            rides_this_month[ride_row, :] = [user_id_j, month, ride, acc_j_r, pay, 30-pay]
            ride_row = ride_row + 1
            total_acc_j = total_acc_j + acc_j_r
            
        users_df["RATE_M"+f"{month+1}"][users_requesting[row]] = total_acc_j
            
    # These are the users that had none of their ride requests accepted this month
    non_returning_users_2 = users_requesting[users_df["RATE_M"+f"{month+1}"][users_requesting] == 0]

    # Set these users to never active again
    users_df.ACTIVE[non_returning_users_2] = -1        
        
    # Convert the temp ride array to a data frame        
    rides_this_month_df = pd.DataFrame(rides_this_month, columns=rides_df.columns)        

    # Append the temp array to the rides results df
    rides_df = pd.concat([rides_df, rides_this_month_df], ignore_index=True)
    
    return(users_df, rides_df)



### Generate acceptances: Time dependent rate

def generate_acceptances_half(users_requesting, pays, probs, pay_probs, month_change, month, users_df, rides_df):
    
    # Extract the number of rides of each user
    ids_and_requests = users_df.loc[users_requesting, ['USER_ID', "REQ_M"+f"{month}"]]

    # Calculate the total number of rides requested
    num_rides = sum(ids_and_requests["REQ_M"+f"{month}"])

    # Set up an array to store the results
    rides_this_month = np.zeros((num_rides, len(rides_df.columns)))

    # A count of the number of rides processed
    ride_row = 0
    

    # Loop through each ride and generate if it accepted or not
    # and how the Pay, and store the results in the temp array
    for row in range(0, len(ids_and_requests)):
        user_id_j = ids_and_requests.USER_ID.iloc[row]
        requests_j = ids_and_requests["REQ_M"+f"{month}"].iloc[row]
        
        total_acc_j = 0

        for ride in range(1, requests_j+1):
            if month > month_change:
                pay = pays[1]
                prob_acc = probs[1]
            else:
                pay = pays[0]
                prob_acc = probs[0]
                
            acc_j_r = random.random() < prob_acc
            rides_this_month[ride_row, :] = [user_id_j, month, ride, acc_j_r, pay, 30-pay]
            ride_row = ride_row + 1
            total_acc_j = total_acc_j + acc_j_r
            
        users_df["RATE_M"+f"{month+1}"][users_requesting[row]] = total_acc_j
            
    # These are the users that had none of their ride requests accepted this month
    non_returning_users_2 = users_requesting[users_df["RATE_M"+f"{month+1}"][users_requesting] == 0]

    # Set these users to never active again
    users_df.ACTIVE[non_returning_users_2] = -1        
        
    # Convert the temp ride array to a data frame        
    rides_this_month_df = pd.DataFrame(rides_this_month, columns=rides_df.columns)        

    # Append the temp array to the rides results df
    rides_df = pd.concat([rides_df, rides_this_month_df], ignore_index=True)
    
    return(users_df, rides_df)