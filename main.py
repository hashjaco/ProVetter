from screener import *
from decouple import config

if __name__ == "__main__":
    user = User(config("USERNAME"), config("SECRET"))
    screener = JefeScreener(test_user=["24228"], user, browser='firefox')
    screener.run()
