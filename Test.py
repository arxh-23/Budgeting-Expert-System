import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import random, os

LARGE_FONT= ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)
SMALL_FONT = ("Helvetica", 8)

headerlist = ['Date', 'Withdrawal', 'Deposit', 'Balance']
spendList = ['Dining Out', 'Groceries', 'Shopping', 'Transportation', 'Housing', 'Entertainment', 'Bills', 'Loan Repayment']
essentialList = ['Groceries', 'Housing', 'Bills', 'Loan Repayment', 'Transportation']
nonessentialList = ['Dining Out', 'Shopping', 'Entertainment']
incomeList = ['Salary', 'Bonus', 'Interest', 'Return on Investement', 'Personal Sale']

global avg_weekly_deposits, avg_weekly_withdrawals, avg_monthly_deposits, avg_monthly_withdrawals, savings_per_week, savings_per_month, total_deposited, total_spent, current_savings, monthly_income
global allInferences 

debt_list = [
    {'name': 'Credit card', 'amount': 5000, 'interest_rate': 15},
    {'name': 'Student loan', 'amount': 20000, 'interest_rate': 5},
    {'name': 'Car loan', 'amount': 10000, 'interest_rate': 7},
    {'name': 'Mortgage', 'amount': 100000, 'interest_rate': 3},
]

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def select_file():
    global filename, allInferences
    filetypes = (
                ('CSV files', '*.csv'),
                ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    
    df = preprocess(filename)
    expert_system = ExpertSystem(df, debt_list)
    expert_system.addRules()
    expert_system.checkBudget()
    expert_system.eval_Savings()
    expert_system.checkCashflow()
    expert_system.checkforSpikes()
    expert_system.evaluateDebt()
    expert_system.makeInferences()
    allInferences = expert_system.getInferences()
    allInferences.sort(key=lambda x: x.severity)
    print('\nAll Inferences: \n')
    for i in allInferences:
        # if i.type == 'Spike':
            print(i.type, 'Inference: Premise:', i.premise, '\nRecommendation:', i.conclusion, '\nSeverity:',i.severity , '\n')

class ESapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        # tk.Tk.iconbitmap(self,default='clienticon.ico')
        tk.Tk.wm_title(self, "Financial Budget Expert System")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.configure(background='dark grey')

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command = lambda: popupmsg("Not supported just yet!"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, PageOne, GraphPage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def startup(self, cont):
        select_file()
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text=("Welcome to the budgeting Expert System"), font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        label1 = tk.Label(self, text=("Please select a CSV file to begin."), font=NORM_FONT)
        label1.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Open a File",
                            command=lambda: controller.startup(PageOne))
        button1.pack()

        button2 = ttk.Button(self, text="Exit Program",
                            command=quit)
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(GraphPage))
        button3.pack()

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Blackboard", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button3 = ttk.Button(self, text="Show Inferences",
                            command= lambda: self.showInferences())
        button3.pack()

    def showInferences(self):
        global allInferences
        # show inferences in 3 lists (severe, moderate, minor)
        severInferences = []
        moderateInferences = []
        minorInferences = []
        
        textBox_severe = tk.Text(self, height=20, width=70, padx=10, pady=10, wrap=tk.WORD)
        textBox_severe.pack(expand=True, side=tk.LEFT) 
        textBox_severe.insert(tk.END, 'Severe Inferences: \n\n')

        textBox_moderate = tk.Text(self, height=20, width=70, padx=10, pady=10, wrap=tk.WORD)
        textBox_moderate.pack(expand=True, side=tk.LEFT) 
        textBox_moderate.insert(tk.END, 'Moderate Inferences: \n\n')

        textBox_minor = tk.Text(self, height=20, width=70, padx=10, pady=10, wrap=tk.WORD)
        textBox_minor.pack(expand=True, side=tk.LEFT)
        textBox_minor.insert(tk.END, 'Minor Inferences: \n\n')
            

        for i in allInferences:
            if i.severity == 1:
                # severInferences.append(i)
                # inf = i.type + 'Inference: Premise:' + i.premise + 'Recommendation:' + i.conclusion + 'Severity:' + str(i.severity)
                # severInferences.append(inf + '\n')
                textBox_severe.insert(tk.END, i.type + ' Inference: Premise: ' + i.premise + ' Recommendation: ' + i.conclusion + '\n\n')
            elif i.severity == 2:
                # moderateInferences.append(i)
                textBox_moderate.insert(tk.END, i.type + ' Inference: Premise: ' + i.premise + ' Recommendation: ' + i.conclusion + '\n\n')
            else:
                minorInferences.append(i)
                textBox_minor.insert(tk.END, i.type + ' Inference: Premise: ' + i.premise + ' Recommendation: ' + i.conclusion + '\n\n')

        # textBox_severe = tk.Text(self, height=10, width=50, padx=10, pady=10, wrap=tk.WORD)
        # textBox_severe.pack(expand=True) 
        # textBox_severe.insert(tk.END, 'Severe Inferences: \n ' + str(severInferences))
        # textBox_severe.tag_configure("left", justify='left')
        # textBox_severe.tag_add("left", 1.0, "end")
       



class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select a method of inference", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(GraphPage))
        button3.pack()

class GraphPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class ExpertSystem:
    def __init__(self, df, debt_list):
        self.df = df
        self.debt_list = debt_list
        self.rules = []
        self.facts = []
        self.inferences = []
        self.types = ['Spending', 'Savings', 'Debt', 'Cashflow', 'Spike']

    def add_rule(self, type, premise, conclusion, severity):
        self.rules.append(Rule(type, premise, conclusion, severity))

    def get_rules(self):
        return self.rules

    def add_inference(self, type, premise, conclusion, severity):
        self.inferences.append(Inference(type, premise, conclusion, severity))

    def evaluateDebt(self):
        high_interest_debt = []
        total_debt = 0
        
        for debt in self.debt_list:
            total_debt += debt['amount']
            if debt['interest_rate'] >= 8: # if interest rate is greater than or equal to 8%
                high_interest_debt.append(debt)
        
        if high_interest_debt:
            self.add_fact('Debt','high_interest_debt', True)
        else:
            self.add_fact('Debt','high_interest_debt', False)
        if total_debt > 0.5 * monthly_income:
            self.add_fact('Debt','high_debt_to_MonthlyIncome', True)
        else:
            self.add_fact('Debt','high_debt_to_MonthlyIncome', False)

    def makeInferences(self):
        for rule in self.rules:
            if rule.check(self.facts):
                for type in self.types:
                    if rule.type == type:
                        self.add_inference(type, rule.premise, rule.conclusion, rule.severity)

    def getInferences(self):
        # return self.spendingInferences, self.savingsInferences, self.debtInferences, self.cashflowInferences
        return self.inferences

    def add_fact(self, type, name, value):
        self.facts.append(Fact(type, name, value))

    def getFacts(self):
        return self.facts
    
    def getRules(self):
        return self.rules

    def addRules(self):
        self.add_rule('Cashflow','Weekly Cashflow is negative', 'You currently have a negative Weekly cashflow Adjust your budget.', 1)
        self.add_rule('Cashflow','Monthly Cashflow is negative', 'You currently have a negative Monthly cashflow Adjust your budget.', 1)
        self.add_rule('Cashflow','Total Net Cashflow is negative', 'You currently have a negative net cashflow. Adjust your budget.', 1)

        self.add_rule('Spending','Essential Costs Spending is too high', 'Lower your Essential spending.', 2)
        self.add_rule('Spending','Non-Essential Costs Spending is too high', 'Lower your Nonessential spending.', 1)

        categories = self.df['Category'].unique()
        for category in categories:
            if category in ['Groceries', 'Shopping']:
                self.add_rule('Spending', category + ' Spending is too high', 'Lower your ' + category + ' spending.', 2)
            elif category in ['Transportation', 'Essential Costs']:
                self.add_rule('Spending', category + ' Spending is too high', 'Lower your ' + category + ' spending.', 3)
            else:
                self.add_rule('Spending', category + ' Spending is too high', 'Lower your ' + category + ' spending.', 1)


        self.add_rule('Debt','high_interest_debt', 'High-interest debt detected, consider paying off the debt first.', 1)
        self.add_rule('Debt','high_debt_to_MonthlyIncome', 'Your debt-to-income ratio is high, consider paying off some debt or increasing your income.', 2)

        self.add_rule('Savings','low_savings', 'Your savings are low, consider increasing your savings.', 2)
        self.add_rule('Savings','Insufficient Emergency Fund', 'Your emergency fund is insufficient, consider increasing your emergency fund.', 1)
        self.add_rule('Savings','Insufficient Retirement Fund', 'Your retirement fund is insufficient, consider increasing your retirement fund.', 3)

    def checkBudget(self):
        global current_savings, total_deposited, total_spent
        df = self.df
        df = df[df['Withdrawal'] != 0] # filter out all the rows that have 0 in the Withdrawal column
        df = df.groupby(['Category']).sum() # group the dataframe by Category and sum the Withdrawal column
        df = df.sort_values(by=['Withdrawal'], ascending=False) # sort the dataframe by Withdrawal column in descending order
        df = df.reset_index() # reset the index
        df = df[['Category', 'Withdrawal']] # select only the Category and Withdrawal columns
        df = df.rename(columns={'Withdrawal': 'Amount'}) # rename the Withdrawal column to Amount
        spending_dict = df.to_dict('records') # convert the dataframe to a list of dictionaries
        # add the percentage of spending for essential and non-essential costs
        spending_dict.append({'Category': 'Essential Costs', 'Amount': df[df['Category'].isin(['Housing', 'Bills', 'Groceries', 'Transportation'])]['Amount'].sum()})
        spending_dict.append({'Category': 'Non-Essential Costs', 'Amount': df[df['Category'].isin(['Entertainment', 'Dining Out', 'Shopping', 'Loan Repayment'])]['Amount'].sum()})


        # print list of categories and amount spent
        # for i in range(len(spending_dict)):
        #     print(spending_dict[i]['Category'], ': ', spending_dict[i]['Amount'])
        
        spending_percentages = {row['Category']: row['Amount'] / total_deposited for row in spending_dict} # calculate the percentage of spending for each category

        # print list of categories and percentage of spending
        # for key, value in spending_percentages.items():
        #     print(key, ': ', value)

        # #evaluate each category against its threshold and add fact if it does not meet the threshold
        spending_thresholds = {'Housing': 0.4, 'Groceries': 0.1, 'Dining Out': 0.1, 'Shopping': 0.2, 'Transportation': 0.1, 'Bills': 0.1, 'Loan Repayment': 0.1, 'Essential Costs': 0.6, 'Non-Essential Costs': 0.4, 'Entertainment': 0.1}
        for category in spending_percentages:
            if spending_percentages[category] > spending_thresholds[category]:
                # print(category + ' Spending is too high')
                self.add_fact('Spending', category + ' Spending is too high', True)
            else:
                # print(category + ' Spending is not too high')
                self.add_fact('Spending', category + ' Spending is too high', False)
    
    def eval_Savings(self):
        global total_invested, avg_weekly_deposits, avg_weekly_withdrawals, avg_monthly_deposits, avg_monthly_withdrawals, savings_per_week, savings_per_month, total_deposited, total_spent, current_savings, monthly_income
        emergency_fund_goal, retirement_goal = 1000, 100000
        savings_percentage = total_deposited / total_spent * 100
        investment_percentage = total_invested / total_deposited * 100
        emergency_fund_achieved = current_savings >= emergency_fund_goal
        retirement_goal_achieved = total_invested >= retirement_goal

        # recommendations = []
        if savings_percentage < 10:
            # recommendations.append("Consider increasing your savings to ensure a secure future.")
            self.add_fact('Savings','low_savings', True)
        else:
            self.add_fact('Savings','low_savings', False)
        if not emergency_fund_achieved:
            # recommendations.append("Consider starting an emergency fund to cover unexpected expenses.")
            self.add_fact('Savings','Insufficient Emergency Fund', True)
        else:
            self.add_fact('Savings','Insufficient Emergency Fund', False)
        if not retirement_goal_achieved:
            # recommendations.append("Consider increasing contributions to your retirement account.")
            self.add_fact('Savings','Insufficient Retirement Fund', True)
        else:
            self.add_fact('Savings','Insufficient Retirement Fund', False)

    def checkCashflow(self):
        global total_invested, avg_weekly_deposits, avg_weekly_withdrawals, avg_monthly_deposits, avg_monthly_withdrawals, savings_per_week, savings_per_month, total_deposited, total_spent, current_savings, monthly_income
        if avg_weekly_deposits < avg_weekly_withdrawals:
            self.add_fact('Cashflow','Weekly Cashflow is negative', True)
        else:
            self.add_fact('Cashflow','Weekly Cashflow is negative', False)
        if avg_monthly_deposits < avg_monthly_withdrawals:
            self.add_fact('Cashflow','Monthly Cashflow is negative', True)
        else:
            self.add_fact('Cashflow','Monthly Cashflow is negative', False)
        if total_deposited < total_spent:
            self.add_fact('Cashflow','Total Net Cashflow is negative', True)
        else:
            self.add_fact('Cashflow','Total Net Cashflow is negative', False)

    def checkforSpikes(self): #function to check for spikes in spending by category
        #if there are more than 3 spikes in a category, then create a corresponding rule and fact in the expert system
        global avg_weekly_deposits, avg_weekly_withdrawals, avg_monthly_deposits, avg_monthly_withdrawals, savings_per_week, savings_per_month, total_deposited, total_spent, current_savings, monthly_income
        categories = self.df['Category'].unique()
        for category in categories:
            category_df = self.df[self.df['Category'] == category]
            category_df = category_df.groupby(['Month'])['Withdrawal'].sum().reset_index()
            avg_spending = category_df['Withdrawal'].mean()
            category_df['Above_Avg'] = category_df['Withdrawal'] > avg_spending
            spikes = category_df[category_df['Above_Avg'] == True]
            spikes = spikes.reset_index(drop=True)
            if len(spikes) >= 3 and category != 'Loan Repayment':
                self.add_rule('Spike', 'More than 3 monthly spikes in ' + category, 'Consider creating a strict Monthly budget for ' + category, 1)
                self.add_fact('Spike', 'More than 3 monthly spikes in ' + category, True)
            else:
                # es.add_fact('Spike', 'More than 3 monthly spikes in ' + category, False)
                pass #if there are no spikes, then don't add a fact

class Fact:
    def __init__(self, type, name, value):
        self.type = type
        self.name = name
        self.value = value

class Rule:
    def __init__(self, type, premise, conclusion, severity):
        self.type = type
        self.premise = premise
        self.conclusion = conclusion
        self.severity = severity

    def check(self, facts):
        for f in facts:
            if self.premise == f.name and f.value == True and self.type == f.type:
                # print('premise in facts')
                return True
        # print('premise not in facts')
        return False

    def getConclusion(self):
        return self.conclusion
    
    def getPremises(self):
        return self.premise

class Inference:
    def __init__(self, type, premise, conclusion, severity):
        self.type = type
        self.premise = premise
        self.conclusion = conclusion
        self.severity = severity
    
    def getConclusion(self):
        return self.conclusion
    
    def getPremises(self):
        return self.premise

def preprocess(filename):
    global total_invested, avg_weekly_deposits, avg_weekly_withdrawals, avg_monthly_deposits, avg_monthly_withdrawals, savings_per_week, savings_per_month, total_deposited, total_spent, current_savings, monthly_income
    
    df = pd.read_csv(filename)
    current_savings = df[df['Withdrawal'] != 0]['Withdrawal'].sum() - df[df['Deposit'] != 0]['Deposit'].sum()
    total_spent = df[df['Withdrawal'] != 0]['Withdrawal'].sum()
    total_deposited = df[df['Deposit'] != 0]['Deposit'].sum()
    
    avg_weekly_deposits = df['Deposit'].sum() / df['Week'].nunique()
    avg_weekly_withdrawals = df['Withdrawal'].sum() / df['Week'].nunique()
    savings_per_week = avg_weekly_deposits - avg_weekly_withdrawals
    
    avg_monthly_deposits = df['Deposit'].sum() / df['Month'].nunique()
    avg_monthly_withdrawals = df['Withdrawal'].sum() / df['Month'].nunique()
    savings_per_month = avg_monthly_deposits - avg_monthly_withdrawals
    
    monthly_income = df[df['Category'] == 'Salary']['Deposit'].sum()
    avg_monthly_income = monthly_income / df['Month'].nunique()
    monthly_income = avg_monthly_income

    total_invested = df[df['Category'] == 'Investment']['Deposit'].sum()

    return df 

def main():
    global debt_list
    app = ESapp()
    app.mainloop()

if __name__ == '__main__':
    main()