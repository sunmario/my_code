from random import randint as ra
import sqlite3

class DbAdapter:
    def __init__(self,db_file="card.s3db"):
        try:
            self.connection_db = sqlite3.connect(db_file)
        except FileNotFoundError:
            try:
                file = open("card.s3db", "w")
                self.connection_db = sqlite3.connect(file)
            except PermissionError:
                print("You don't have permission to create files in this directory")
        self.cursor = self.connection_db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER UNIQUE,number TEXT UNIQUE,pin TEXT,balance INTEGER DEFAULT 0);")
        self.connection_db.commit()
        self.cursor.execute('select max(id) from card')
        self.new_id = self.cursor.fetchone()[0]
        if self.new_id is None:
            self.new_id = 1

    def db_add_account(self,number,pin):
        balance = 0
        self.cursor.execute('select max(id) from card')
        self.new_id = self.cursor.fetchone()[0]
        if self.new_id is None:
            self.new_id = 1
        insert_query = "insert into card values({l[0]},{l[1]},{l[2]},{l[3]});".format(
            l=[str((self.new_id + 1)), str(number), str(pin), str(balance)])
        self.cursor.execute(insert_query)
        self.connection_db.commit()

    def db_get_balance(self, card):
        check_query = "select balance from card where number = {}".format(card)
        self.cursor.execute(check_query)
        query = self.cursor.fetchall()
        res = query[0][0]
        return res

    def db_update_balance(self,money,account):
        cur_bal = int(money) + self.db_get_balance(account) # maybe check if anyacc is logged in
        update_query = "update card set balance = {l[0]} where number = {l[1]}".format(l=[cur_bal, account])
        self.cursor.execute(update_query)
        self.connection_db.commit()

    def db_do_transfer(self,current,trans_number,money):
        #not_done
        check_query = "select balance from card where number = {}".format(trans_number)
        self.cursor.execute(check_query)
        checking_card = self.cursor.fetchall()
        if not checking_card:
                print("Such a card does not exist.\n") #может тут эксепшн
        else:
            current_balance1 = self.db_get_balance(current)
            if int(money) > current_balance1:
                print("Not enough money!\n")# надо как-то передавать
            else:
                self.db_update_balance(-money,current)
                self.db_update_balance(money,trans_number)
                #maybe i should update with add_income


    def db_card_exist(self,card):
        check_query = "select number,pin from card where number = {}".format(card)
        self.cursor.execute(check_query)
        exist = self.cursor.fetchall()
        if exist is not None:
            return exist
        else:
            return False


    def db_delete_acc(self,card):
        delete_query = "delete from card where number = {}".format(card)
        self.cursor.execute(delete_query)
        self.connection_db.commit()




class Bank:
    def __init__(self):
        self.db = DbAdapter()
        self.current_account = None
        self.exit = False

    @staticmethod
    def luhn():
        """
        Алгоритм Луна использует простое правило вычисления контрольной суммы для проверки идентификационных номеров,
        таких как номера пластиковых карт.
        Алгоритм определяет ошибки ввода одной неправильной цифры,
        а также почти все перестановки соседних цифр, за исключением перестановки 09-90 или обратной 90-09.

        В данном случае в задании было указано генерировать номера карт
        с 400000 + случайные цифры(длина номера карты 16), которые должны проходить проверку
        алгоритмом Луна.
        """
        card = str("400000" + "".join([str(ra(0, 9)) for _ in range(10)]))
        card = [int(i) for i in card]
        rest = card[:len(card) - 1]
        for i in range(len(rest)):
            if i % 2 == 0:
                rest[i] = rest[i] * 2
        for i in range(len(rest)):
            if rest[i] > 9:
                rest[i] = rest[i] - 9
        s = sum(rest)
        last_digit = 0
        if s % 10 == 0:
            last_digit = 0
        else:
            last_digit = 10 - (s % 10)
        valid = card[:len(card) - 1]
        valid.append(last_digit)
        valid = [str(i) for i in valid]
        return "".join(valid)


    def create_account(self):
        card_number = self.luhn()
        pin = "".join([str(ra(0, 9)) for _ in range(4)])
        self.db.db_add_account(card_number,pin)
        print("Your card has been created")
        print("Your card number:\n{}".format(card_number))
        print("Your card PIN:\n{}\n".format(pin))

    def login(self):
        card_input = input("Enter your card number:")
        pin_input = input("Enter your PIN:\n")
        query = self.db.db_card_exist(card_input)
        if query != []:
            if query[0][0] == card_input:
                if query[0][1] == pin_input:
                    self.current_account = card_input
                    print("You have successfully logged in!\n")
                else:
                    print("Wrong card number or PIN!\n")
            else:
                    print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")

    def check_balance(self):
        res = self.db.db_get_balance(self.current_account)
        print("Balance:{}\n".format(res))

    def add_income(self):
        cur_bal = self.db.db_get_balance(self.current_account)
        inc = input("Enter income:\n")
        self.db.db_update_balance(inc,self.current_account)
        print("Income was added!\n")

    def do_transfer(self):
        #not done
        print("Transfer")
        trans_number = input("Enter card number:")
        check = self.db.db_card_exist(trans_number)
        if check == False:
                print("Such a card does not exist.\n")
        else:
            money = input("Enter how much money you want to transfer:")
            current_balance1 = self.db.db_get_balance(self.current_account)
            if int(money) > current_balance1:
                print("Not enough money!\n")
            else:

                print("Success!\n")

    def close_acc(self):
        self.db.db_delete_acc(self.current_account)
        print("The account has been closed!\n")
        self.current_account = None

    def logout(self):
        self.current_account = None

    def main_menu(self):
        exit_bool = True
        while exit_bool:
            if self.current_account is None:
                print("1. Create an account\n2. Log into account\n0. Exit")
                answer = input()
                if answer == "1":
                    self.create_account()
                elif answer == "2":
                    self.login()
                else:
                    exit_bool = False
            else:
                print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
                answer1 = input()
                if answer1 == "1":
                    self.check_balance()
                elif answer1 == "2":
                    self.add_income()
                elif answer1 == "3":
                    self.do_transfer()
                elif answer1 == "4":
                    self.close_acc()
                elif answer1 == "5":
                    self.logout()
                else:
                    exit_bool = False
        print("Bye!")


if __name__ == '__main__':
    Bank().main_menu()

