from block import Block
from datetime import datetime
from Stripe import Stripe as stripe
import random

import sys
import PIL.Image
import os.path
sys.modules['Image'] = PIL.Image


def main():
    from blockchain import Blockchain
    blockchain  = Blockchain()
    blockchain.addToChain(Block().make_block2(blockchain)) # Genesis block created here

    """
    # Making our own blocks.
    n = 3
    for _ in range(0, n):
        data = {'Place': 'Place_{}'.format(_+1),
        'Time': 'Time of the event:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'Seat': 'E{}'.format(random.randint(1,999)),
        'Price': 'AUD {}'.format(random.randint(1,99999))
        }
        block = Block().make_block2(blockchain, data)

        blockchain.addToChain(block) # Add the new block to the chain
        #prev_block = blockchain.getLastBlock() # Update the previous block pointer.

        generate_qrcode(block) # Generate the QR Code of new block.
        generate_pdf(block) # Generate the PDF of new block.

    print_to_file(blockchain)
    """

    # Before making the block, I need to get POW from users to make a block.
    # Assume we have user 1 attempting to verify himself..
    from user import User
    u1 = User("FirstNameBob","LastNameDoe","Account0123-ABC-321") # Creating a user
    u2 = User("SecondNameJane","Doe","Acc1987-ZXC")
    u3 = User("ThirdNameJosh","Burrows","901-999-231")
    userList = []
    userList.append(u1)
    userList.append(u2)
    userList.append(u3)

    # Need to make data list.
    placeList = []
    priceSeatDict = {}
    dateList = []

    placeList.append("Belmont Park")
    placeList.append("New Era Field")
    placeList.append("Yankee Stadium")

    priceSeatDict["C"] = "109"
    priceSeatDict["D"] = "129"
    priceSeatDict["E"] = "139"

    # Input is %d - %m - %Y %I:%M %p
    # Date - Month - Year Hour:Minute AM/PM
    dateList.append("27 - 11 - 2017 11:00 pm")
    dateList.append("09 - 12 - 2017 11:00 pm")
    dateList.append("19 - 01 - 2018 11:00 pm")


    numOfTicket = 3
    i = numOfTicket
    totalPrice = 0

    approvalList = []  # Only for paypal. Cannot use this atm.
    pdfList = []  # List of PDF file made this time.

    from myPayment import MyPayment
    paymentClass = MyPayment()

    thisPDF = []  # PDF generated based on tickets.

    # looping down the ticket.
    while i>0:
        # a, b, c = main2(blockchain, userList, placeList, dateList, priceSeatDict, paymentClass) # Paypal payment
        a, pdfName = main2(blockchain, userList, placeList, dateList, priceSeatDict, paymentClass) # Stripe payment
        totalPrice += a
        thisPDF.append(pdfName)
        # paymentIDList.append(b) # paypal payment
        # approvalList.append(c) # paypal payment
        i -= 1
    check_user(userList)

    paymentID = sPayment.createCharge(totalPrice*100)	# Converting to $ because Stripe will start from c ..
    checkDuplicate(paymentIDList,paymentID) # To prevent duplicate payment_id

    print("Total Price:{}. PaymentID:{}.\nTickets:\n{}\n".format(totalPrice,paymentID, '\n'.join(thisPDF)))

    """
    for i in thisPDF:
        import subprocess
        subprocess.Popen([i], shell=True)
    """

    """
    # Find the payerID from the approval_url.
    # Looping through all strings
    d = list(approvalList[0])
    stringLength = len(d) - 1
    while(stringLength > 0):
        if(d[stringLength] is "="):
            break
        stringLength -= 1
    startIndex = stringLength + 1
    payerID = d[startIndex:len(d)-1] # This result still in list
    payerID =''.join(payerID) # Make this string.

    inputUser = input("Pay now? (Y/N)")
    if(inputUser.upper() == "Y"):
        #payerID = input("Enter your payer ID:")
        #i = paymentID[0]
        #payerID = paymentClass.testAuthorize(paymentID)
        paymentClass.executePayment(paymentID, payerID)
        """


def main2(blockchain, uL, placeL, dateL, priceSeatD, paymentClass):
    """
    This function is basically, generating all the documents required.
    It will return price of each ticket and file of PDF created.
    """

    ########################################################
    # Choosing values from the list randomly
    cPlace = placeL[random.randint(0,len(placeL)-1)]
    cSeat, cPrice = random.choice(list(priceSeatD.items()))
    cSeat += str(random.randint(0,9))
    unprocessedTime = dateL[random.randint(0,len(dateL)-1)]
    cTime = datetime.strptime(unprocessedTime, '%d - %m - %Y %I:%M %p')
    ########################################################

    # Generating a payment using paypal, this will generate payment ID. paymentID, approval_url = generate_payment(
    # blockchain.getLen(), cPrice, paymentClass) # Maybe put this at the top, after looping all tickets, so there is
    # only one paymentID. paymentID = "test123" + str(random.randint(1,99999)) # Just a random generic number

    # paymentFlag = blockchain.checkDuplicatePaymentID(paymentID) # Return True or False, to check if payment ID has
    # been duplicated.

    """
    # Data of the block with payment
    data = {'Place': '{}'.format(cPlace),
    'Time': 'Time of the event:{}'.format(cTime),
    'Seat': '{}'.format(cSeat),
    'Price': 'AUD {}'.format(cPrice),
    'PaymentID':'{}'.format(paymentID)
    }
    """

    # Data of the block without payment
    data = {'Place': '{}'.format(cPlace),
    'Time': 'Time of the event:{}'.format(cTime),
    'Seat': '{}'.format(cSeat),
    'Price': 'AUD {}'.format(cPrice)
    }

    # Server will request a new block to be mined if there isn't any block ready to go.
    newBlock = nextBlocksUsed(blockchain, uL) # if the last block is empty, it will get the last block. Otherwise,
    # a new block will be added.

    # If duplicate payment ID is found, paymentFlag will be False and the rest of the if loop won't be executed
    # if(newBlock and paymentFlag):	# This is for paypal payment
    if newBlock:		# This is for stripe payment
        # Update the data of the empy block.
        newBlock.updateData(data)

        generate_qrcode(newBlock)  # Generate the QR Code of new block.
        generate_barcode(newBlock)  # Generate barcode.

        pdfName = generate_pdf(newBlock)  # Generate the PDF of new block.
        print('test', file=sys.stderr)
        print_to_file(blockchain)  # Generate txt file.

        # return int(cPrice), paymentID, approval_url # This line is used with paypal payment
        return int(cPrice), pdfName # This line used for Stripe payment.
    else:
        #print("New block is not created! newBlock:{}. paymentFlag:{}.".format(newBlock, paymentFlag)) # This line is used with paypal payment
        print("New block is not created! newBlock:{}.".format(newBlock)) # This line is used with Stripe payment


def nextBlocksUsed(blockchain, uL):
    """
    Make a new block if the length of the empty block is less than N.
    Example: if we want to make 3 empty blocks every single times, set N to 4.
    """
    N = 4  # Number of empty blocks + 1.
    while blockchain.lenEmptyBlock() < N:
        a = createBlockEmptyData(blockchain, uL)
    return blockchain.nextBlockToUse()


def createBlockEmptyData(blockchain, uL):
    # Make a new block with empty data
    data = {}
    newBlock = Block().make_block2(blockchain, data) # Server releases a block to be mined by user.	This will return None if payment ID is duplicated

    # In real life, user will not be chosen, but will race against each others
    user1 = uL[random.randint(0,len(uL)-1)]
    solution, answer = user1.minePuzzle(newBlock.getHash(), condition) # PoW to verify himself, user needs to send the answer for verification in the real life.

    # Verifying the answer.
    isAnswerTrue = verifyAnswer(solution, condition)

    # Verifying the whole blockchain
    isNoBrokenChain = blockchain.verifyBlockchain() # Check every single blockchain, making sure there isn't any broken chain

    if(isNoBrokenChain == False and isAnswerTrue):
        print("Not adding to blockchain..")
        return None
    else: # If there isn't any broken chain.

        # The person is successfully verify himself and the blockchain.
        user1.addToken(1) # Add one token
        newBlock.updateAnswer(answer) # Update the answer of the new made block to verify the specific requirement.
        newBlock.updateAuthor(user1.getName()) # Update the author of the block.

        # This is to modify the blockchain will be made public.
        blockchain.addToChain(newBlock) # Add the new block to the chain
        return newBlock


def verifyAnswer(solution, condition):
    import string
    if(solution.startswith(condition)):
        return True
    return False


def check_user(uL):
    for i in uL:
        print(i)


def print_to_file(blockchain):
    file = open(pathTicket + '\out.txt','w')
    str = ""
    str+= '----- Below is the whole blockchain.. -----\n'
    for b in blockchain:
        # print('Data of Ticket:\n{}. Ticket number:{}.\nTimestamp:{}.\nHash:{}.\nPrevious hash:{}.\n'.format(b.data,b.index,b.timestamp,b.hash,b.previous_hash))
        # print('Block Author:{}.\nBlock Answer to Reach Requirement:{}.\n'.format(b.getAuthor(),b.getAnswer()))
        str += 'Data of Ticket:\n{}. Ticket number:{}.\nTimestamp:{}.\nHash:{}.\nPrevious Hash:{}.\nAnswer:{}.\nAuthor:{}.\n\n'.format(b.data,b.index,b.timestamp,b.hash, b.previous_hash, b.getAnswer(), b.getAuthor())
    file.write(str)
    file.close()


def generate_payment(i, price, pClass):
    """
    This is with the use of PayPal payment
    """
    print("Please wait while we are processing your payment..")
    # payment = MyPayment("Ticket{}".format(i),price,"AUD",1)
    pClass.setName("Ticket{}".format(i))
    pClass.setPrice(price)
    pClass.setCurrency("AUD")
    pClass.setQuantity(1)
    return pClass.getPayment()


def generate_qrcode(b):
    import pyqrcode
    i = b.index
    qrcode = pyqrcode.create(b.getHash()) # Creat a qr code
    st = os.path.join(pathTicket, str(i) + '.png')
    qrcode.png(st, scale =8) # Output in png on the same dir. 0.png for example
    # print("--- Finish generating QRCode, saved as:{} ---".format(st))


def generate_pdf(block):
    # importing report master
    import time
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

    i = block.index

    # pdf_name = pathTicket + "\\" + str(i) + 'Ticket.pdf'
    pdf_name = os.path.join(pathTicket, str(i) + 'Ticket.pdf')
    doc = SimpleDocTemplate(pdf_name,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]

    # logo = pathTicket + '\\barcode'+ str(i) + ".png"
    logo = os.path.join(pathTicket, 'barcode' + str(i) + '.png')
    im = Image(logo,8*inch,3*inch)
    Story.append(im)

    formatted_time = time.ctime()
    list_full_name = ["Mike Driscoll","Julie Hayden","Augustine Marie"]
    full_name = list_full_name[random.randint(0,len(list_full_name)-1)]
    address_parts = ["411 State St.", "Marshalltown, IA 50158"]

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
    ptext = '<font size=12> Below is the detail of your ticket<br/>Place: {}.<br/>Seat: {}.<br/>{}.<br/></font>'.format(block.data['Place'], block.data['Seat'], block.data['Time'])
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))

    # logo = pathTicket + "\\" + str(i) + ".png" # An example of pdf generation using the qrcode we just generated
    os.path.join(pathTicket, str(i) + '.png')
    im = Image(logo, 3*inch, 3*inch)
    Story.append(im)

    doc.build(Story)
    # print('---PDF Generated, saved as %s---' %pdf_name)
    return pdf_name


def test_read_qrcode(i):
    """
    In the real life, this will not be needed. Considering there is scanner that will get us the hash straight away.
    """
    import qrtools

    qr = qrtools.QR()
    qr.decode(str(i)+".png")
    # print("--- Result of Decoded QR code:{}.\n".format(qr.data))
    return qr.data


def generate_barcode(block):
    import barcode
    from barcode.writer import ImageWriter

    code39 = barcode.get_barcode_class('code39')
    barcode39 = code39(str(block.getHash()), writer=ImageWriter())
    # fileName = pathTicket + '\\barcode'+str(block.getIndex())
    fileName = os.path.join(pathTicket, 'barcode'+str(block.getIndex()))
    barcode39.save(fileName)

    # print("Saved as {}.".format(fileName))


def checkDuplicate(aList, item):
    if item not in aList:
        aList.append(item)


if __name__ == "__main__":

    # Initiate paymentIDList
    global paymentIDList
    paymentIDList = []  # This is list of paymentID. There shouldn't be any double ID here.

    # Creating the directory ticket for all the outputs.
    pathTicket = os.path.abspath("ticket")
    if not os.path.exists(pathTicket):
        os.makedirs(pathTicket)
        print("Making a directory:"+pathTicket)

    # Condition is requirement required by the server for user to successfuly mined a block. Maybe we should place it in blokchain...
    global condition
    condition = '00'  # Requirement for user to do mining. They need to find a hash start with this condition.

    # Initiate class of Strip
    global sPayment
    sPayment = stripe()

    main()