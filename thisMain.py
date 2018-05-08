from block import Block
from datetime import datetime
from blockchain import Blockchain
from user import User

import random

import sys
import PIL.Image

sys.modules['Image'] = PIL.Image

import os.path


class thisMain:
    def __init__(self):
        # Creating blockchain
        self.currentUser = User(
            id=random.randint(0, 10000),
            account="guest@guest.com"
        )
        self.blockchain = Blockchain()
        newBlock = Block().make_block2(self.blockchain)
        self.blockchain.addToChain(newBlock)  # Genesis block created here


        # Creating user list
        # u1 = User("FirstNameBob", "LastNameDoe", "Account0123-ABC-321")  # Creating a user
        # u2 = User("SecondNameJane", "Doe", "Acc1987-ZXC")
        # u3 = User("ThirdNameJosh", "Burrows", "901-999-231")
        # self.userList = []
        # self.userList.append(u1)
        # self.userList.append(u2)
        # self.userList.append(u3)

        # Creating the directory ticket for all the outputs.
        self.pathTicket = os.path.abspath("ticket")
        if not os.path.exists(self.pathTicket):
            os.makedirs(self.pathTicket)
        # print("Making a directory:"+self.pathTicket)

        self.condition = "0"

    def createUser(self, firstName, lastName, account):
        self.currentUser.updateFirstName(firstName)
        self.currentUser.updateLastName(lastName)
        self.currentUser.updateAccount(account)
        self.currentUser.id = account
        return self.currentUser


    def addData(self, place, time, seat, price):
        self.data = {'Place': '{}'.format(place),
                     'Time': 'Time of the event:{}'.format(time),
                     'Seat': '{}'.format(seat),
                     'Price': 'AUD {}'.format(price)
                     }

    def run(self):
        # Server will request a new block to be mined if there isn't any block ready to go.
        newBlock = self.nextBlocksUsed()  # if the last block is empty, it will get the last block. Otherwise, a new block will be added.

        # If duplicate payment ID is found, paymentFlag will be False and the rest of the if loop won't be executed
        # if(newBlock and paymentFlag):	# This is for paypal payment
        if (newBlock):
            # Update the data of the empy block.
            newBlock.updateData(self.data)
            # Generate the QR Code of new block.
            self.generate_qrcode(newBlock)
            # Generate barcode
            self.generate_barcode(newBlock)
            # Generate the PDF of new block.
            pdfName = self.generate_pdf(newBlock)
            # Generate txt file.
            self.print_to_file()

            # return int(cPrice), paymentID, approval_url # This line is used with paypal payment
            return pdfName, newBlock.getHash(), newBlock.getPrevHash()  # This line used for Stripe payment.
        else:
            # print("New block is not created! newBlock:{}. paymentFlag:{}.".format(newBlock, paymentFlag)) # This line is used with paypal payment
            # print("New block is not created! newBlock:{}.".format(newBlock)) # This line is used with Stripe payment
            pass

    def nextBlocksUsed(self):
        """
        Make a new block if the length of the empty block is less than N.
        Example: if we want to make 3 empty blocks every single times, set N to 4.
        """
        N = 4  # Number of empty blocks + 1.
        while (self.blockchain.lenEmptyBlock() < N):
            self.createBlockEmptyData()
        return self.blockchain.nextBlockToUse()

    def createBlockEmptyData(self):
        # Make a new block with empty data
        data = {}
        newBlock = Block().make_block2(self.blockchain,
                                       data)  # Server releases a block to be mined by user.	This will return None if payment ID is duplicated

        # In real life, user will not be chosen, but will race against each others
        # user1 = self.userList[random.randint(0, len(self.userList) - 1)]
        user1 = self.currentUser
        solution, answer = user1.minePuzzle(newBlock.getHash(),
                                            self.condition)  # PoW to verify himself, user needs to send the answer for verification in the real life.

        # Verifying the answer.
        isAnswerTrue = self.verifyAnswer(solution, self.condition)

        # Verifying the whole blockchain
        isNoBrokenChain = self.blockchain.verifyBlockchain()  # Check every single blockchain, making sure there isn't any broken chain

        if (isNoBrokenChain == False and isAnswerTrue):
            print("Not adding to blockchain..")
            return None
        else:  # If there isn't any broken chain.

            # The person is successfully verify himself and the blockchain.
            user1.addToken(1)  # Add one token
            newBlock.updateAnswer(answer)  # Update the answer of the new made block to verify the specific requirement.
            newBlock.updateAuthor(user1.getName())  # Update the author of the block.

            # This is to modify the blockchain will be made public.
            self.blockchain.addToChain(newBlock)  # Add the new block to the chain
            return newBlock

    def verifyAnswer(self, solution, condition):
        import string
        if solution.startswith(condition):
            return True
        return False

    def generate_pdf(self, block):
        # importing report master
        import time
        from reportlab.lib.enums import TA_JUSTIFY
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        i = block.hash
        # pdf_name = self.pathTicket + "/" + str(i) + 'Ticket.pdf'
        pdf_name = os.path.join(self.pathTicket, str(i)+'Ticket.pdf')
        doc = SimpleDocTemplate(pdf_name, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        Story = []

        # Adding barcode
        # logo = self.pathTicket + '/barcode' + str(i) + ".png"
        logo = os.path.join(self.pathTicket, 'barcode'+str(i)+'.png')
        im = Image(logo, 8 * inch, 3 * inch)
        Story.append(im)

        formatted_time = time.ctime()
        full_name = self.currentUser.firstName + ' ' + self.currentUser.lastName
        # list_full_name = ["Mike Driscoll", "Julie Hayden", "Augustine Marie"]
        # full_name = list_full_name[random.randint(0, len(list_full_name) - 1)]

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        ptext = '<font size=12>%s</font>' % formatted_time

        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 15))

        ptext = '<font size=12>Dear %s:</font>' % full_name.split()[0].strip()
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))

        ptext = '<font size=12>Thank you for purchasing the ticket! </font>'
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12))

        """
        # This line below, is for paypal payment
        ptext = '<font size=12> Below is the detail of your ticket<br/>Place: {}.<br/>Seat: {}.<br/>{}.<br/>Payment ID:{}.<br/>\
        </font>'.format(block.data['Place'], block.data['Seat'], block.data['Time'], block.data['PaymentID'])
        """
        ptext = '<font size=12> Below is the detail of your ticket<br/>Place: {}.<br/>Seat: {}.<br/>{}.<br/></font>'.format(
            block.data['Place'], block.data['Seat'], block.data['Time'])
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12))

        # Adding QR Code
        # logo = self.pathTicket + "/" + str(
        #    i) + ".png"  # An example of pdf generation using the qrcode we just generated
        logo = os.path.join(self.pathTicket, str(i)+'.png')
        im = Image(logo, 3 * inch, 3 * inch)
        Story.append(im)

        doc.build(Story)
        # print('---PDF Generated, saved as %s---' %pdf_name)
        return str(i) + 'Ticket.pdf'

    # FILE NAME GENERATED AS: 1Ticket.pdf, 2Ticket.pdf

    def generate_qrcode(self, b):
        import pyqrcode
        i = b.hash
        qrcode = pyqrcode.create(b.getHash())  # Creat a qr code
        # st = self.pathTicket + "/" + str(i) + '.png'
        st = os.path.join(self.pathTicket, str(i)+'.png')
        qrcode.png(st, scale=8)  # Output in png on the same dir. 0.png for example

    # print("--- Finish generating QRCode, saved as:{} ---".format(st))

    def generate_barcode(self, block):
        import barcode
        from barcode.writer import ImageWriter

        code39 = barcode.get_barcode_class('code39')
        barcode39 = code39(str(block.getHash()), writer=ImageWriter())
        # fileName = self.pathTicket + '/barcode' + str(block.getHash())
        fileName = os.path.join(self.pathTicket, 'barcode'+str(block.getHash()))
        barcode39.save(fileName)

    def print_to_file(self):
        file = open(self.pathTicket + '/out.txt', 'w')
        str = ""
        str += '----- Below is the whole blockchain.. -----\n'
        for b in self.blockchain:
            # print('Data of Ticket:\n{}. Ticket number:{}.\nTimestamp:{}.\nHash:{}.\nPrevious hash:{}.\n'.format(b.data,b.index,b.timestamp,b.hash,b.previous_hash))
            # print('Block Author:{}.\nBlock Answer to Reach Requirement:{}.\n'.format(b.getAuthor(),b.getAnswer()))
            str += 'Data of Ticket:\n{}. Ticket number:{}.\nTimestamp:{}.\nHash:{}.\nPrevious Hash:{}.\nAnswer:{}.\nAuthor:{}.\n\n'.format(
                b.data, b.index, b.timestamp, b.hash, b.previous_hash, b.getAnswer(), b.getAuthor())
        file.write(str)
        file.close()
