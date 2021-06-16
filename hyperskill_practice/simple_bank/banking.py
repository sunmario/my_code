from random import randint as ra
import sqlite3


class Bank:

    def __init__(self, db_file="card.s3db"):
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
        self.current_account = None

    @staticmethod
    def luhn_check(number):
        """
        Алгоритм Луна использует простое правило вычисления контрольной суммы для проверки идентификационных номеров,
        таких как номера пластиковых карт.
        Алгоритм определяет ошибки ввода одной неправильной цифры,
        а также почти все перестановки соседних цифр, за исключением перестановки 09-90 или обратной 90-09.
        """
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
        self.cursor.execute('select max(id) from card')
        self.new_id = self.cursor.fetchone()[0]
        if self.new_id is None:
            self.new_id = 0
        insert_query = "insert into card values({l[0]},{l[1]},{l[2]},{l[3]});".format(
            l=[str((self.new_id + 1)), str(acc.card_number), str(acc.pin), str(acc.balance)])
        self.cursor.execute(insert_query)
        self.connection_db.commit()
        print("Your card has been created")
        print("Your card number:\n{}".format(acc.card_number))
        print("Your card PIN:\n{}\n".format(acc.pin))

    def login(self):
        card_input = input("Enter your card number:")
        pin_input = input("Enter your PIN:")
        print("\n")
        check_query = "select * from card where number = {}".format(card_input)
        self.cursor.execute(check_query)
        query = self.cursor.fetchall()
        if query:
            for i in query:
                if i[1] == card_input:
                    if i[2] == pin_input:
                        self.current_account = card_input
                        print("You have successfully logged in!\n")
                    else:
                        print("Wrong card number or PIN!\n")
                else:
                    print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")

    def logout(self):
        self.current_account = None

    def check_balance(self):
        if self.current_account is not None:
            check_query = "select * from card where number = {}".format(self.current_account)
            self.cursor.execute(check_query)
            query = self.cursor.fetchall()[0]
            print("Balance:{}\n".format(query[3]))

    def get_balance(self, cardb):
        check_query = "select * from card where number = {}".format(cardb)
        self.cursor.execute(check_query)
        query = self.cursor.fetchall()
        res = None
        if query is not []:
            res = query[0][3]
        else:
            pass
            # no such card
        return res

    def add_income(self):
        if self.current_account is not None:
            cur_bal = self.get_balance(self.current_account)
            inc = input("Enter income:\n")
            update_query = "update card set balance = {l[0]} where number = {l[1]}".format(l=[cur_bal + int(inc), self.current_account])
            self.cursor.execute(update_query)
            self.connection_db.commit()
            print("Income was added!\n")

    def do_transfer(self):
        print("Transfer")
        trans_number = input("Enter card number:")
        check_query = "select * from card where number = {}".format(trans_number)
        self.cursor.execute(check_query)
        checking_card = self.cursor.fetchall()
        if not checking_card:
                print("Such a card does not exist.\n")
        else:
            money = input("Enter how much money you want to transfer:")
            current_balance1 = self.get_balance(self.current_account)
            if int(money) > current_balance1:
                print("Not enough money!\n")
            else:
                current_balance1 = current_balance1 - int(money)
                update_query1 = "update card set balance = {l[0]} where number = {l[1]};".format(l=[current_balance1, self.current_account])
                self.cursor.execute(update_query1)
                self.connection_db.commit()
                current_balance2 = checking_card[0][3] + int(money)
                update_query2 = "update card set balance = {l[0]} where number = {l[1]};".format(l=[current_balance2, trans_number])
                self.cursor.execute(update_query2)
                self.connection_db.commit()
                print("Success!\n")


    def close_acc(self):
        delete_query = "delete from card where number = {}".format(self.current_account)
        self.cursor.execute(delete_query)
        self.connection_db.commit()
        self.current_account = None
        print("The account has been closed!\n")

    def main(self):
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


class Account(Bank):
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

    def __init__(self):
        super().__init__()
        self.card_number = self.luhn()
        self.pin = "".join([str(ra(0, 9)) for _ in range(4)])
        self.balance = 0


bank = Bank()
bank.main()
