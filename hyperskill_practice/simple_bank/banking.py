from random import randint as ra
import sqlite3


class DbAdapter:
    def __init__(self, db_file="card.s3db"):
        try:
            self.connection_db = sqlite3.connect(db_file)
        except FileNotFoundError:
            try:
                file = open("card.s3db", "w")
                self.connection_db = sqlite3.connect(file, timeout=15)
            except PermissionError:
                print("You don't have permission to create files in this directory")
        self.cursor = self.connection_db.cursor()
        query = "create table if not exists card " \
                "(id integer auto_increment," \
                "number text unique," \
                "pin text," \
                "balance integer default 0," \
                "primary key(id));"
        self.cursor.execute(query)
        self.connection_db.commit()

    def db_add_account(self, number, pin):
        balance = 0
        insert_query = "insert into card(number,pin,balance) values({l[0]},{l[1]},{l[2]});".format(
            l=[str(number), str(pin), str(balance)])
        self.cursor.execute(insert_query)
        self.connection_db.commit()

    def db_get_balance(self, card):
        check_query = "select balance from card where number = {}".format(card)
        self.cursor.execute(check_query)
        query = self.cursor.fetchall()
        res = query[0][0]
        return res

    def db_card_exists(self, number):
        check_query = "select number from card where number = {}".format(number)
        self.cursor.execute(check_query)
        try:
            exist = self.cursor.fetchall()[0][0]
            if exist is not None:
                return True
        except IndexError:
            pass
        return False

    def db_get_card_info(self, number):
        check_query = "select number,pin from card where number = {}".format(number)
        self.cursor.execute(check_query)
        info = self.cursor.fetchall()[0]
        return info

    def db_update_balance(self, money, account):
        cur_bal = int(money) + self.db_get_balance(account)
        update_query = "update card set balance = {l[0]} where number = {l[1]}".format(l=[cur_bal, account])
        self.cursor.execute(update_query)
        self.connection_db.commit()

    def db_do_transfer(self, current, trans_number, money):
        if not self.db_card_exists(trans_number):
            raise RuntimeError("Such card doesn't exist!")
        else:
            current_balance1 = self.db_get_balance(current)
            if int(money) > current_balance1:
                raise RuntimeError("Not enough money!")
            else:
                cur_bal1 = -int(money) + self.db_get_balance(current)
                update_query = "update card set balance = {l[0]} where number = {l[1]}".format(l=[cur_bal1, current])
                self.cursor.execute(update_query)
                cur_bal = int(money) + self.db_get_balance(trans_number)
                update_query = "update card set balance = {l[0]} where number = {l[1]}".format(
                    l=[cur_bal, trans_number])
                self.cursor.execute(update_query)
                self.connection_db.commit()

    def db_delete_acc(self, card):
        delete_query = "delete from card where number = {}".format(card)
        self.cursor.execute(delete_query)
        self.connection_db.commit()


class Bank:
    def __init__(self):
        self.db = DbAdapter()
        self.current_account = None

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
        self.db.db_add_account(card_number, pin)
        return card_number, pin

    def login(self, card_input, pin_input):
        if self.db.db_card_exists(card_input):
            info = self.db.db_get_card_info(card_input)
            if info[1] == pin_input:
                self.current_account = card_input
                return True
        return False

    def check_balance(self):
        return self.db.db_get_balance(self.current_account)

    def add_income(self, inc, account):
        self.db.db_update_balance(inc, account)

    def do_transfer(self, trans_number, money):
        # trans_number - card number where money is sent to
        # money - sum of money that is sent
        try:
            self.db.db_do_transfer(self.current_account, trans_number, money)
            return True
        except RuntimeError as e:
            raise e

    def close_acc(self):
        self.db.db_delete_acc(self.current_account)
        self.current_account = None

    def logout(self):
        self.current_account = None


class Main:
    def __init__(self):
        self.bank = Bank()
        self.need_exit = False

    def login(self):
        card_input = input("Enter your card number:")
        pin_input = input("Enter your PIN:")
        if self.bank.login(card_input, pin_input):
            print("You have successfully logged in!\n")
        else:
            print("Wrong card number or PIN!\n")

    def create_acc(self):
        out = self.bank.create_account()
        print("Your card has been created\n")
        print("Your card number:\n{}".format(out[0]))
        print("Your card PIN:\n{}\n".format(out[1]))

    def exit(self):
        self.need_exit = True

    def balance(self):
        print("Balance:{}\n".format(self.bank.check_balance()))

    def add_income(self):
        inc = input("Enter income:\n")
        self.bank.add_income(inc, self.bank.current_account)
        print("Income was added!\n")

    def transfer(self):
        print("Transfer")
        trans_number = input("Enter card number:\n")
        money = input("Enter how much money you want to transfer:\n")
        try:
            self.bank.do_transfer(trans_number, money)
            print("Success!\n")
        except RuntimeError as e:
            print(e)

    def close_acc(self):
        self.bank.close_acc()
        print("The account has been closed!\n")

    def logout(self):
        print("Logged out!\n")
        self.bank.logout()

    def main_menu(self):
        options_logged_in = {"1": ["1. Balance", self.balance],
                             "2": ["2. Add income", self.add_income],
                             "3": ["3. Do transfer", self.transfer],
                             "4": ["4. Close account", self.close_acc],
                             "5": ["5. Log out", self.logout],
                             "0": ["0. Exit", self.exit]
                             }

        options_not_logged_in = {"1": ["1. Create an account", self.create_acc],
                                 "2": ["2. Log into account", self.login],
                                 "0": ["0. Exit", self.exit]
                                 }

        while not self.need_exit:
            if self.bank.current_account is None:
                for i in options_not_logged_in.keys():
                    print(options_not_logged_in[i][0])
                answer = input()
                try:
                    options_not_logged_in[answer][1]()
                except KeyError:
                    print("Such option doesn't exist, choose one from the list")
            else:

                for i in options_logged_in.keys():
                    print(options_logged_in[i][0])
                answer1 = input()
                try:
                    options_logged_in[answer1][1]()
                except KeyError:
                    print("Such option doesn't exist, choose one from the list")
        print("Bye!")


if __name__ == '__main__':
    Main().main_menu()
