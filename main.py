import re
import json
from IPython.display import clear_output as clear

class User():

    def __init__(self, state, year, insurance = 0, yard = 0, vacancy = 0, repair = 0, capex = 0, morgage = 0, down = 0, closing = 0, rehab = 0, laundry = 0, storage = 0, misc = 0):

        self.state = state
        self.year = year
        self.insurance = insurance
        self.yard = yard
        self.vacancy = vacancy
        self.repair = repair
        self.capex = capex
        self.morgage = morgage
        self.down = down
        self.closing = closing
        self.rehab = rehab
        self.laundry = laundry
        self.storage = storage
        self.misc = misc
        self.rent = self.access_rent()

        if self.state:
            self.tax_rate, self.hoa_rent, self.propman_rate, self.utilities = self.get_rates()

        else:
            self.tax_rate = None
            self.hoa_rent = None
            self.propman_rate = None 
            self.utilities = None


    def access_rent(self):

        with open('grossrents.txt') as f:
            rent = f.readlines()
        pattern = re.compile(r'^([A-Za-z\s\.]+)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)\s+\$?(\d+|\bNA\b)$')

        for l in rent:
            match = pattern.search(l)
            if match:
                state = match.group()
                rent2000 = match.group()
                rent1980 = match.group()
                rent1990 = match.group() 
                rent1970 = match.group()
                rent1960 = match.group()
                rent1950 = match.group()
                rent1940 = match.group()
                state = ' '.join(state.split()).lower()

                if state == self.state:
                    rent_value = [rent1940, rent1950, rent1960, rent1970, rent1980, rent1990, rent2000]
                    rent_by_decade = [int(rnt) if rnt != 'NA' else None for rnt in rent_value]
                    start_yr = 2000
                    end_yr = 1940

                    valid_rents = [(index * 10, rnt) for index, rnt in enumerate(rent_by_decade) if rnt is not None]
                    increment = (valid_rents[0][1] - valid_rents[-1][1]) / (valid_rents[0][0] - valid_rents[-1][0])
                    for year in range(start_yr, end_yr -1, -1):
                        if self.year == year:
                            rent = rent_by_decade[(start_yr - year) // 10] - increment * (start_yr - year) % 10
                            return rent
                        elif year > self.year > year - 10:
                            rent = rent_by_decade[(start_yr - year) // 10] - increment * (start_yr - self.year) % 10
                            return rent
                        

    def get_rates(self):

        with open('rates.json', 'r') as f:
            rates = json.load(f)
        
        format_rate = {key.lower(): value for key, value in rates.items()}
        return format_rate[self.state]
    
    
    def get_states(self):
        with open('rates.json', 'r') as f:
            rates = json.load(f)
        
        return [state.lower()for state in rates.keys()]
    

class Income():

    def __init__(self, user):
        self.rental = user.rent
        self.laundry = user.laundry
        self.storage = user.storage
        self.misc = user.misc
        self.total = self.calculateIncome()

    def calculateIncome(self):
        self.total = self.rental + self.laundry + self.storage + self.misc
        print(self.__repr__())
        return self.total
    
    def __repr__(self):
        return f"\n Your total monthly income is ${self.total:,.2f}\n"
    

class Expenses():

    def __init__(self, user):
        self.tax = user.rent * user.tax_rate
        self.hoa = user.rent * user.hoa_rate
        self.propman = user.rent * user.propman_rate
        self.insurance = user.insurance
        self.yard = user.yard
        self.vacancy = user.vacancy
        self.repairs = user.repairs
        self.capex = user.capex
        self.morgage = user.morgage
        self.utilities = user.utilities
        self.total = self.calculateExpense()

    def calculateExpense(self):
        self.total = self.tax + self.insurance + sum(self.utilities.values()) + self.hoa + self.yard + self.vacancy + self.repairs + self.capex + self.propman + self.morgage
        print(self.__rapr())
        return self.total
    
    def __rapr__(self):
        return f"\n Your total monthly expenses are ${self.total:,.2f}\n"
    


class CashFlow():

    def __init__(self, income, expenses):

        self.income = income.total
        self.expenses = expenses.total
        self.total = self.calculateCashFlow()

    def calculateCashFlow(self):

        self.total = (self.income - self.expenses) * 12
        print(self.__repr__())
        return self.total
    
    def __repr__(self):
        return f"\n Your total annual cash flow is ${self.total:,.2f}\n"
    

class CashReturn():

    def __init__(self, cash_flow, user):
        self.down = user.down
        self.closing = user.closing
        self.rehab = user.rehab
        self.misc = user.misc
        self.total_investment = self.calculateInvestment()
        self.cash_flow = cash_flow.total
        self.return_rate = self.calculateReturn()

    def calculateInvestment(self):
        return self.down + self.closing + self.rehab + self.misc
    
    def calculateReturn(self):
        return (self.cash_flow / self.total_investment) * 100
    
    def __repr__(self):
        return f"\n Your annual cash-on-cash return is {self.return_rate:,.2f}% \n"
    



class PropertyCalculate():

    def __init__(self):
        self.user = None
        self.users = {}
        self.states = User("", 0).get_states()

    def validateInput(self, prompt, var_type = float, defalut = None):
        while True:
            try:
                value = input(prompt)
                if not value and defalut is not None:
                    return defalut
                return var_type(value)
            except ValueError:
                print(f"Invalid input: {prompt} must be a {var_type.__name__}.")


    def register(self):
        while True:
            print("\n ******* NEW USER REGISTRATION *******")
            usernm = input("Enter a New Username: ")

            if usernm in self.users:
                print("Username already taken.. Please choose another username..")

            else:
                break

        pswd = input("Enter New Password: ")
        self.users[usernm] = pswd
        print("\n ---You are successfully registered---")


    def login(self):
        usernm = input("Username: ")
        pswd = input("Password: ")

        if usernm in self.users and self.users[usernm] == pswd:
            print(f"\n Logged in as {usernm}")
            self.getUserInput()
            self.calculate()
            self.logout()

        else:
            print("Username or password is incorrect or not matched")
            return False
        
    def logout(self):
        self.user = None
        print("\n --- Logged out successfully ---")


    def getUserInput(self):

        while True:
            state = input("1. State: ").lower()
            if state not in self.states:
                print("\n Invalid input: State not found. Please enter a valid state..")
                continue
            else:
                break
        
        while True:

            year = self.validateInput("2. Year (1940-2000): ", int)

            if year < 1940 and year > 2000:
                print("Invalid input: Year must be between 1940-2000 and must be integer...")
                continue
            else:
                break

        self.user = User(state, year)
        self.user.access_rent()
        self.user.get_rates()

        self.user.insurance = self.validateInput("3. Insurance amount: ")
        self.user.yard = self.validateInput("4. Yard amount: ")
        self.user.vacancy = self.validateInput("5. Vacancy amount: ")
        self.user.repair = self.validateInput("6. Repairs amount: ")
        self.user.capex = self.validateInput("7. Capital Expenditure amount: ")
        self.user.morgage = self.validateInput("8. Mortgage amount: ")
        self.user.down = self.validateInput("9. Down payment amount: ")
        self.user.closing = self.validateInput("10. Closing cost amount: ")
        self.user.rehab = self.validateInput("11. Rehab cost amount: ")
        self.user.laundry = self.validateInput("12. Laundry income (default: 0): ")
        self.user.storage = self.validateInput("13. Storage income (default: 0): ")
        self.user.misc = self.validateInput("14. Miscellaneous income (default: 0): ")

    
    def calculate(self):
        clear()

        user = User(self.user.state, self.user.year, self.user.insurance, self.user.yard, self.user.vacancy, self.user.repair, self.user.capex, self.user.morgage, self.user.down, self.user.closing, self.user.rehab, self.user.laundry, self.user.storage, self.user.misc)
        income = Income(user)
        expenses = Expenses(user)
        cash_flow = CashFlow(income, expenses)
        cash_return = CashReturn(cash_flow, user)

        print(cash_return)

    def run(self):

        while True:
            clear()
            choice = input("Enter 'login', 'register' or 'exit': ").lower()

            if choice == 'register':
                usernm = self.register()
                if usernm:
                    print("\n Please log in with your newly registered account...")

            elif choice == 'login':
                is_login = self.login()

                if is_login:
                    self.getUserInput()
                    self.calculate()
                    self.logout()
                elif not self.users:
                    print("User not found: Please register.. \n")

            elif choice == 'exit':
                print("Thank you for using our app..")
                break
            
            else:
                print("Please enter proper input... ('register', 'login', 'exit')")



count = PropertyCalculate()
count.run()
