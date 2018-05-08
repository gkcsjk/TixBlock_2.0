"""
This blockchain can be and will be published.
"""


class Blockchain:
    def __init__(self):
        self.chain = []

    def addToChain(self, i):
        self.chain.append(i)

    def getChain(self):
        return self.chain

    def getLen(self):
        return len(self.chain)

    def getLastBlock(self):
        return self.chain[-1]

    def getGenesisBlock(self):
        return self.chain[0]

    def getBlock(self, i):
        return self.chain[i]

    def __getitem__(self, i):
        return self.chain[i]

    def __str__(self):
        for i in self.chain:
            print(i)

    def nextBlockToUse(self):
        """
        This will return none if there isn't any block ready to be used!
        """
        for i in self.chain:
            if (i.isEmpty()):
                return i  # Block.

    def lenEmptyBlock(self):
        j = 0
        for i in self.chain:
            if (i.isEmpty()):
                j += 1
        return j

    def verifyBlockchain(self):
        """
        This function is to verify the blockchain.
        Unmatched hash will return false
        """
        blocksIndex = self.getLen() - 1
        while blocksIndex > 0:
            currentBlock = self.getBlock(blocksIndex)
            previousBlock = self.getBlock(blocksIndex - 1)
            if (currentBlock.getPrevHash() != previousBlock.getHash()):
                # print("From blockchain.py: FOUND BROKEN CHAIN")
                return False
            blocksIndex -= 1
        # print("From blockchain.py: NO BROKEN CHAIN")
        return True

    def checkDuplicatePaymentID(self, paymentID):
        # Checking duplicate of payment ID.
        # If duplicate found, return false
        for i in self.chain:
            if (i.index == 0):
                continue
            else:
                if i.data and paymentID is i.data["PaymentID"]:
                    # print("Found duplicate!")
                    # print(i.data["PaymentID"])
                    return False
        return True


if __name__ == "__main__":
    print("Start testing")

    blockchain = Blockchain()

    from block import Block

    testBlock = Block()
    blockchain.addToChain(testBlock)

    testBlock2 = Block()
    blockchain.addToChain(testBlock2)
