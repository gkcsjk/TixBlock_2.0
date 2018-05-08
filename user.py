import hashlib
import random
import string
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, firstName='', lastName='', account='', token=0):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.token = token
        self.account = account
        self.puzzleSolved = 0

    def updateFirstName(self, a):
        self.firstName = a

    def updateLastName(self, a):
        self.lastName = a

    def updateToken(self, token):
        self.token = token

    def addToken(self, token):
        self.token += token

    def updateAccount(self, account):
        self.account = account

    def __str__(self):
        return self.account
        return ('{} {} has {} tokens.'.format(self.firstName, self.lastName, self.token))

    def getName(self):
        return self.firstName + " " + self.lastName

    def getToken(self):
        return self.token

    def addPuzzleSolved(self):
        self.puzzleSolved += 1

    def minePuzzle(self, challenge_alphanumeric, condition):
        """
        This is the proof of work.
        """
        # Input challenge_alphanumeric is the hash of the block.
        # List of constants
        Found = False
        N = random.randint(50, 200)  # This is number of alphanumerics to make the hash.

        shaHash = hashlib.sha256()
        self.condition = condition
        while not Found:
            answer = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
                range(N))

            attempt = challenge_alphanumeric + answer

            shaHash.update(attempt.encode('utf-8'))

            solution = shaHash.hexdigest()

            if solution.startswith(self.condition):
                return solution, answer
                Found = True


if __name__ == "__main__":
    print("Start testing")

    userList = []

    u1 = User("A", "Doe", "123-456-789")
    userList.append(u1)

    print(u1)
    print("Expected: A Doe has 0 tokens")
    print("Successful!\n")

    u1.updateFirstName("New")
    u1.updateLastName("Year")
    print(u1.getName())
    print("Expected: New Year")
    print("Successful!\n")

    u1.addToken(1)
    print(u1.getToken())
    print("Expected: 1")
    print("Successful!\n")
