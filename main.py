import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random, os, calendar, datetime
from datetime import datetime

headerlist = ['Date', 'Description', 'Withdrawal', 'Deposit', 'Balance']
spendList = ['Food', 'Groceries', 'Shopping', 'Transportation', 'Travel', 'Entertainment', 'Bills', 'Other']
incomeList = ['Salary', 'Bonus', 'Interest', 'Other']
global savings_per_week, savings_per_month, savings_per_year

def cleanData():
    if not os.path.exists('data.csv'): # check if the file exists
        df = pd.read_csv('accountactivity.csv', names=headerlist) #assign column names 
        df.replace(np.nan, 0, inplace=True) # replace NaN with 0, inplace=True means it will change the original dataframe

        # convert the date column to a datetime format
        df['Date'] = pd.to_datetime(df['Date'])
        df['Week'] = df['Date'].dt.week
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year

        for i in range(len(df)): # iterate through the dataframe
            if df.at[i, 'Deposit'] == 0: # if the Deposit column is 0
                df.at[i, 'Category'] = random.choice(spendList) # assign a random spend category to each row
            # elif df.at[i, 'Withdrawal'] == 0: # if the Withdrawal column is 0
            else:
                df.at[i, 'Category'] = random.choice(incomeList) # assign a random income category to each row

        df.to_csv('data.csv', index=False) # save the dataframe to a csv file, index=False means it will not save the index column (0, 1, 2, 3, ...)

        # print(df.columns)
        print(df)
    else:
        df = pd.read_csv('data.csv')
        # print(df)
    return df 

def plotSpending(df):
    df = df[df['Withdrawal'] != 0] # filter out all the rows that have 0 in the Withdrawal column
    df = df.groupby(['Category']).sum() # group the dataframe by Category and sum the Withdrawal column
    df = df.sort_values(by=['Withdrawal'], ascending=False) # sort the dataframe by Withdrawal column in descending order
    df = df.reset_index() # reset the index
    # print(df)

    # plot the data
    plt.figure(figsize=(15, 5))
    plt.bar(df['Category'], df['Withdrawal'])
    plt.xlabel('Category')
    plt.ylabel('Withdrawal')
    plt.title('Spending by Category')
    plt.show()

def plotIncome(df):
    df = df[df['Deposit'] != 0] # filter out all the rows that have 0 in the Deposit column
    df = df.groupby(['Category']).sum() # group the dataframe by Category and sum the Deposit column
    df = df.sort_values(by=['Deposit'], ascending=False) # sort the dataframe by Deposit column in descending order
    df = df.reset_index() # reset the index
    # print(df)

    # plot the data
    plt.figure(figsize=(10, 5))
    plt.bar(df['Category'], df['Deposit'])
    plt.xlabel('Category')
    plt.ylabel('Deposit')
    plt.title('Income by Category')
    plt.show()

def plot_cashflow(df):
    #show cashflow of income vs spending week by week beginning at the first date in the data set and ending at the last date in the data set
    df = df.groupby(['Week']).sum() # group the dataframe by Date and sum the Deposit and Withdrawal columns
    df = df.sort_values(by=['Week'], ascending=True) # sort the dataframe by Date column in ascending order
    df = df.reset_index() # reset the index
    # print(df)

    # plot the data
    plt.figure(figsize=(15, 5))
    plt.plot(df['Week'], df['Deposit'], label='Income')
    plt.plot(df['Week'], df['Withdrawal'], label='Spending')
    plt.xlabel('Week')
    plt.ylabel('Amount')
    plt.title('Cashflow')
    plt.legend()
    plt.show()

def calc_week_avgs(df):
    
    #first find averages for total deposits and withdrawals for each week
    avg_weekly_deposits = df['Deposit'].sum() / df['Week'].nunique()
    avg_weekly_withdrawals = df['Withdrawal'].sum() / df['Week'].nunique()

    print('Average weekly deposits: ', avg_weekly_deposits)
    print('Average weekly withdrawals: ', avg_weekly_withdrawals)
    print('Average weekly cashflow: ', avg_weekly_deposits - avg_weekly_withdrawals)
    global savings_per_week 
    savings_per_week = avg_weekly_deposits - avg_weekly_withdrawals
    print()

    # calculate the sum of deposits and withdrawals for each week
    week_sums = df.groupby(['Week', 'Category']).agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
    
    # calculate the number of weeks
    num_weeks = week_sums['Week'].nunique()
    
    # calculate the average deposits and withdrawals per week
    week_avgs = week_sums.groupby('Category').agg({'Deposit': 'mean', 'Withdrawal': 'mean'})
    week_avgs['Deposit'] = week_avgs['Deposit'] / num_weeks
    week_avgs['Withdrawal'] = week_avgs['Withdrawal'] / num_weeks

    return week_avgs

def calc_monthly_avgs(df):
        
    #first find averages for total deposits and withdrawals for each week
    avg_monthly_deposits = df['Deposit'].sum() / df['Month'].nunique()
    avg_monthly_withdrawals = df['Withdrawal'].sum() / df['Month'].nunique()

    print('Average monthly deposits: ', avg_monthly_deposits)
    print('Average monthly withdrawals: ', avg_monthly_withdrawals)
    print('Average monthly cashflow: ', avg_monthly_deposits - avg_monthly_withdrawals)
    global savings_per_month
    savings_per_month = avg_monthly_deposits - avg_monthly_withdrawals
    print()

    # calculate the sum of deposits and withdrawals for each month
    month_sums = df.groupby(['Month', 'Category']).agg({'Deposit': 'sum', 'Withdrawal': 'sum'}).reset_index()
    
    # calculate the number of months
    num_months = month_sums['Month'].nunique()
    
    # calculate the average deposits and withdrawals per month
    month_avgs = month_sums.groupby('Category').agg({'Deposit': 'mean', 'Withdrawal': 'mean'})
    month_avgs['Deposit'] = month_avgs['Deposit'] / num_months
    month_avgs['Withdrawal'] = month_avgs['Withdrawal'] / num_months

    return month_avgs

def plot_montly_avgs(month_avgs):
    #plot monthly averages of income and spending by category
    plt.figure(figsize=(15, 5))
    plt.bar(month_avgs.index, month_avgs['Deposit'], label='Income')
    plt.bar(month_avgs.index, month_avgs['Withdrawal'], label='Spending')
    plt.xlabel('Category')
    plt.ylabel('Amount')
    plt.title('Monthly Averages')
    plt.legend()
    plt.show()

def plot_weekly_avgs(week_avgs):
    #plot weekly averages of income and spending by category
    plt.figure(figsize=(15, 5))
    plt.bar(week_avgs.index, week_avgs['Deposit'], label='Income')
    plt.bar(week_avgs.index, week_avgs['Withdrawal'], label='Spending')
    plt.xlabel('Category')
    plt.ylabel('Amount')
    plt.title('Weekly Averages')
    plt.legend()
    plt.show()

def detect_spikes(df, category):
    category_df = df[df['Category'] == category] # filter out all the rows that have the category we are looking for
    category_df = category_df.groupby(['Week'])['Withdrawal'].sum().reset_index() # group the dataframe by Category and sum the Deposit column
    avg_spending = category_df['Withdrawal'].mean() # calculate the average spending for the category
    category_df['Above_Avg'] = category_df['Withdrawal'] > avg_spending # create a new column that is True if the spending is above the average spending
    spikes = category_df[category_df['Above_Avg'] == True] # filter out all the rows that have False in the Above_Avg column
    spikes = spikes.reset_index(drop=True) # reset the index
    if spikes.empty:
        print(f"No Weekly spikes found in the category '{category}'.") 
    else:
        print(f"Weekly Spikes found in the category '{category}' in weeks:", spikes['Week'].tolist()) 
        # print(spikes[['Week']])
        # spike_Weeks = spikes['Week'].tolist() # convert the dataframe to a list
        # for spike_Week in spike_Weeks: # loop through the list of spike weeks
        #     spike_week = category_df[category_df['Week'] == spike_Week].index[0] # get the index of the first row in the category_df that has the spike week
        #     first_day_of_week = df[df['Week'] == spike_Week]['Date'].iloc[spike_week] # get the first day of the week that has the spike
        #     print(f"Weekly Spike occurred in week: {spike_Week} with first day of the week being {first_day_of_week}") # print the spike week and the first day of the week

def detect_spikes_by_month(df, category):
    category_df = df[df['Category'] == category] # filter out all the rows that have the category we are looking for
    category_df = category_df.groupby(['Month'])['Withdrawal'].sum().reset_index() # group the dataframe by Category and sum the Deposit column
    avg_spending = category_df['Withdrawal'].mean() # calculate the average spending for the category
    category_df['Above_Avg'] = category_df['Withdrawal'] > avg_spending # create a new column that is True if the spending is above the average spending
    spikes = category_df[category_df['Above_Avg'] == True] # filter out all the rows that have False in the Above_Avg column
    spikes = spikes.reset_index(drop=True) # reset the index
    if spikes.empty:
        print(f"No Monthly spikes found in the category '{category}'.") 
    else:
        print(f"Monthly Spikes found in the category '{category}' in months:") 
        # print(spikes[['Month']])
        spike_months = spikes['Month'].tolist()
        for spike_month in spike_months:
            spike_week = category_df[category_df['Month'] == spike_month].index[0]
            first_day_of_week = df[df['Month'] == spike_month]['Date'].iloc[spike_week]
            # print(f"Monthly Spike occurred in Month: {spike_month} with first day of the week being {first_day_of_week}")
            first_day_of_week = datetime.strptime(first_day_of_week, '%Y-%m-%d')
            print('Monthly spike occured in : ' + calendar.month_name[spike_month] + ' of ' + str(first_day_of_week.year))

def wishlist(price, savings = 10):
    # calculate the number of months it will take to save up for an item
    if(savings_per_week <= 0 and savings_per_month <= 0):
        print("Your account currently has a negative netflow. You will need to increase your income or decrease your spending to save up for this item.")
        return
    months = price / savings
    print(f"It will take {months} months to save up for this item.")

def main():
    df = cleanData()
    # calc_week_avgs(df)
    # calc_monthly_avgs(df)
    # wishlist(1000, 10)
    # plotIncome(df)
    # plotSpending(df)
    # plot_cashflow(df)
    # print(calc_week_avgs(df))
    # print()
    # print(calc_monthly_avgs(df))
    # plot_weekly_avgs(calc_week_avgs(df))
    # plot_montly_avgs(calc_monthly_avgs(df))
    for x in spendList:
        detect_spikes(df, x)
        detect_spikes_by_month(df, x)
    detect_spikes(df, 'Groceries')
    detect_spikes_by_month(df, 'Groceries')

if __name__ == "__main__":
    main()
