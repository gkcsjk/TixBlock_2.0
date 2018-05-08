import hashlib as hasher
from datetime import datetime


class Block:
    def __init__(self, index=0, timestamp='', data={}, previous_hash='', author='', answer=''):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Dictionary
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
        self.author = author
        self.answer = answer

    def getData(self):
        return self.data

    def getPrice(self):
        return self.data['Price']

    def getHash(self):
        return self.hash

    def getPrevHash(self):
        return self.previous_hash

    def getIndex(self):
        return self.index

    def updateAuthor(self, authorName):
        self.author = authorName

    def updateAnswer(self, answer):
        self.answer = answer

    def updateBlock(self, answer, authorName):
        self.updateAuthor(authorName)
        self.updateAnswer(answer)

    def updateData(self, data):
        self.data = data

    def getAnswer(self):
        return self.answer

    def getAuthor(self):
        return self.author

    def isEmpty(self):
        return self.data == {} and self.index != 0

    def __str__(self):
        return 'Block #{}. Prev Hash: {}'.format(self.index, self.previous_hash)

    def hash_block(self):
        sha = hasher.sha256()
        seq = (str(x) for x in (
            self.index, self.timestamp, self.data, self.previous_hash))
        sha.update(''.join(seq).encode('utf-8'))
        return sha.hexdigest()

    def makeGenesisBlock(self):
        return Block(index=0, timestamp=datetime.now(), data='Genesis Block..!!', previous_hash='0')

    def make_block2(self, blockchain, data=''):
        """
        This function will return a block with populated data.
        """
        if (blockchain.getLen()) == 0:
            idx = 0
            lastBlockHash = '0'
            data = "Genesis block it is"
        else:
            lastBlock = blockchain.getLastBlock()
            idx = lastBlock.index + 1
            lastBlockHash = lastBlock.hash

        return Block(index=idx,
                     timestamp=datetime.now(),
                     data=data,
                     previous_hash=lastBlockHash)
