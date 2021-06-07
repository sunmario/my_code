from random import randint as ra
import sqlite3

"""
А если все в одном классе то это очень локально и легко исправить
 
И второе
 
Это абстракция
 
Типо странно что банк знает про такие низкоуровневые детали как запросы sql
 
В том и смысл оопе
 
Ты разделяешь абстракции на разные уровни
 
И не экономь на именах переменнхы
 
con, cur и так далее это так себе имена

db_connection уже получше
 
Но main точно должен быть отдельно
 
Типо класс банк отвечает за работу с аккаунтами
 
Он не должен внутри себя крутить цикл с вводом/выводом команд
 
Кстати, хорошая идея попробовать написать немного тестов на эту прогу
"""




class Bank:

    def __init__(self, db_file="card.s3db"):
        try:
            self.con = sqlite3.connect(db_file)
        except FileNotFoundError:
            file = open("card.s3db", "w")
            self.con = sqlite3.connect(file)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER UNIQUE,number TEXT UNIQUE,pin TEXT,balance INTEGER DEFAULT 0);")
        self.con.commit()
        self.cur.execute('select max(id) from card')
        self.new_id = self.cur.fetchone()[0]
        self.cur_acc = None

    def luhn_check(self,number):
        card = list(number)
        card = [int(i) for i in card]
        last_digit = card[-1]
        rest = card[:len(card) - 1]
        for i in range(len(rest)):
            if i % 2 == 0:
                rest[i] = rest[i] * 2
        for i in range(len(rest)):
            if rest[i] > 9:
                rest[i] = rest[i] - 9
        s = sum(rest)
        dec = False
        if (s + last_digit) % 10 == 0:
            dec = True
        return dec

    def create_account(self):
        acc = Account()
        self.cur.execute('select max(id) from card')
        self.new_id = self.cur.fetchone()[0]
        if self.new_id is None:
            self.new_id = 0
        ins = "insert into card values({l[0]},{l[1]},{l[2]},{l[3]});".format(
            l=[str((self.new_id + 1)), str(acc.card_number), str(acc.pin), str(acc.balance)])
        self.cur.execute(ins)
        self.con.commit()
        print("Your card has been created")
        print("Your card number:\n{}".format(acc.card_number))
        print("Your card PIN:\n{}\n".format(acc.pin))

    def login(self):
        card_input = input("Enter your card number:")
        pin_input = input("Enter your PIN:")
        print("\n")
        check = "select * from card where number = {}".format(card_input)
        self.cur.execute(check)
        query = self.cur.fetchall()
        if query:
            for i in query:
                if i[1] == card_input:
                    if i[2] == pin_input:
                        self.cur_acc = card_input
                        print("You have successfully logged in!\n")
                    else:
                        print("Wrong card number or PIN!\n")
                else:
                    print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")

    def logout(self):
        self.cur_acc = None

    def check_balance(self):
        if self.cur_acc is not None:
            check = "select * from card where number = {}".format(self.cur_acc)
            self.cur.execute(check)
            query = self.cur.fetchall()[0]
            print("Balance:{}\n".format(query[3]))

    def get_balance(self, cardb):
        check = "select * from card where number = {}".format(cardb)
        self.cur.execute(check)
        query = self.cur.fetchall()
        res = None
        if query is not []:
            res = query[0][3]
        else:
            pass
            # no such card
        return res

    def add_income(self):
        if self.cur_acc is not None:
            cur_bal = self.get_balance(self.cur_acc)
            inc = input("Enter income:\n")
            upd = "update card set balance = {l[0]} where number = {l[1]}".format(l=[cur_bal + int(inc), self.cur_acc])
            self.cur.execute(upd)
            self.con.commit()
            print("Income was added!\n")

    def do_transfer(self):
        print("Transfer")
        trans_number = input("Enter card number:")
        if self.luhn_check(trans_number):
            check = "select * from card where number = {}".format(trans_number)
            self.cur.execute(check)
            d = self.cur.fetchall()
            #print(d)
            if not d:
                print("Such a card does not exist.\n")
            else:
                mo = input("Enter how much money you want to transfer:")
                cur_bal1 = self.get_balance(self.cur_acc)
                if int(mo) > cur_bal1:
                    print("Not enough money!\n")
                else:
                    cur_bal1 = cur_bal1 - int(mo)
                    upd = "update card set balance = {l[0]} where number = {l[1]};".format(l=[cur_bal1, self.cur_acc])
                    self.cur.execute(upd)
                    self.con.commit()
                    cur_bal2 = d[0][3] + int(mo)
                    upd_t = "update card set balance = {l[0]} where number = {l[1]};".format(l=[cur_bal2, trans_number])
                    self.cur.execute(upd_t)
                    self.con.commit()
                    print("Success!\n")

        else:
            print("Probably you made a mistake in the card number. Please try again!\n")

    def close_acc(self):
        dele = "delete from card where number = {}".format(self.cur_acc)
        self.cur.execute(dele)
        self.con.commit()
        self.cur_acc = None
        print("The account has been closed!\n")

    def main(self):
        exit_bool = True
        while exit_bool:
            if self.cur_acc is None:
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


class Account(Bank):
    def luhn(self):
        card = str("400000" + "".join([str(ra(0, 9)) for _ in range(10)]))
        card = [int(i) for i in card]
        last_digit = 0
        rest = card[:len(card) - 1]
        for i in range(len(rest)):
            if i % 2 == 0:
                rest[i] = rest[i] * 2
        for i in range(len(rest)):
            if rest[i] > 9:
                rest[i] = rest[i] - 9
        s = sum(rest)
        if s % 10 == 0:
            last_digit = 0
        else:
            last_digit = 10 - (s % 10)
        valid = card[:len(card) - 1]
        valid.append(last_digit)
        valid = [str(i) for i in valid]
        return "".join(valid)

    def __init__(self):
        super().__init__()
        self.card_number = self.luhn()
        self.pin = "".join([str(ra(0, 9)) for _ in range(4)])
        self.balance = 0


bank = Bank()
bank.main()
