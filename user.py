class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def setUsername(self, username: str):
        self.username = username

    def setPassword(self, password: str):
        self.password = password

