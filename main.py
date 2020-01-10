from screener import *

if __name__ == "__main__":
    # username = input("Enter your Pared admin email address: ")
    # password = input("Enter your Pared admin password: ")
    user = User("hashim@pared.com", "Hkhalidj86!")
    screener = JefeScreener(["24228"], user, 'firefox')
    screener.run()
