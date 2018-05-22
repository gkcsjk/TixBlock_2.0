from flask import Flask
from flask import render_template, redirect, url_for
from flask import request, Response
from flask import send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from user import User

import stripe
import os

#####
# Below is our secret key for Stripe Payment
#####
os.environ['SECRET_KEY'] = 'sk_test_pS9qQQhUxOv807oJsijQdgPH'
os.environ['PUBLISHABLE_KEY'] = 'pk_test_qSr906RDQZrsoTfjfRCvXvgE'

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

####
# Below is the initialization
####

# Initialization of our blockchain, this will import from thisMain.py
from thisMain import thisMain

myMain = thisMain()
# Initialization of our SQL, this will import from mySql.py
from mySql import mySql

mySql = mySql()
# Checking all events on the system
if mySql.checkCountEventTable() < 1:
    mySql.runExample()  # To load all the example events.

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_tixblock'
)

# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
current_user_account = ''
current_user_name = ''
ticket_selected_count = len(mySql.select_ticket(True))


# Homepage, listing all the events available for user to choose
@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    eventList = mySql.retrieveFromEvents(' DISTINCT place')
    return render_template('home.html', title='Home', eventList=eventList, cart=ticket_selected_count, user=current_user_name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        account = request.form['email']
        if firstName != '' and account != '' and lastName != '':
            # Input is valid
            if mySql.getUser(account) is None:
                # create user in database if not exist
                mySql.insertUser(firstName, lastName, account)
            firstName_db = mySql.getUser(account)[1]
            lastName_db = mySql.getUser(account)[2]
            currentUser = myMain.createUser(firstName_db, lastName_db, account)
            login_user(currentUser)
            global current_user_account, current_user_name
            current_user_account = currentUser.account
            current_user_name = currentUser.firstName + ' ' + currentUser.lastName
            if mySql.getUser(account)[3] == 1 and firstName == 'admin' and lastName == 'admin':
                return redirect(url_for('admin_home'))
            return redirect(url_for('main'))
        else:
            return render_template('login.html', info='Invalid input, please check your email and names.')
    else:
        return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


# Equal to: http://tixblock.pythonanywhere.com/chooseTime/
# When client chooses an event, options of date and time will be shown
@app.route('/chooseTime/', methods=['GET', 'POST'])
@login_required
def chooseTime():
    if request.method == 'POST':
        global dateList  # Will be accessed in chooseSeatPrice
        global eventVal  # Used in confirmation
        # When user click one of the button, it will give different values.
        # Hence variable eventVal is there to catch the value.
        eventVal = request.form["e"]
        # This clause below is to be inserted into database for conditioning purposes.
        # IT will be based on the button clicked by user!
        whereClause = ' place = \'' + eventVal + '\''
        dateList = mySql.retrieveFromEvents(' DISTINCT time ', whereClause)

        return render_template('chooseTime.html', cart=ticket_selected_count, eventName=eventVal, dateL=dateList, user=current_user_name)


# http://tixblock.pythonanywhere.com/chooseSeat/
# Customr will choose their seat
@app.route('/chooseSeat/', methods=['GET', 'POST'])
@login_required
def chooseSeatPrice():
    if request.method == 'POST':
        global eventDateTime  # For confirmation

        # Getting this from global variable
        eventDateTime = request.form["submit"]

        whereClause = ' place = \'' + eventVal + '\'' + ' AND ' + 'time = \'' + eventDateTime + '\''
        sqlSelect = 'seat, price'

        sqlSelect = 'seat, price'

        priceSeatList = mySql.retrieveFromEvents(sqlSelect, whereClause)
        priceSeatDict = {}
        for i in priceSeatList:
            priceSeatDict[i] = i

        # Keep in mind every events have their own seat and prices
        return render_template('chooseSeat.html', cart=ticket_selected_count, eventName=eventVal, eventTime=eventDateTime,
                               seatPriceList=priceSeatDict, user=current_user_name)


# After customer chooses their seat, confirm everything for them to go to payment page.
@app.route('/ConfirmPayment/', methods=['GET', 'POST'])
@login_required
def confirmation():
    if request.method == 'POST':
        global seat
        global price
        global totPrice
        global ticket_selected_count
        seatPrice = request.form["submit"]
        seatPrice = seatPrice.split('-')
        seat = seatPrice[0]
        price = seatPrice[1]

        # Enough data to put it to temporary table
        mySql.insertData(True, eventVal, eventDateTime, seat, price)
        # Get all the unpaid tickets on the temporary list.
        allTempTix = mySql.select_ticket(True)
        ticket_selected_count = len(allTempTix)

        totPrices = mySql.totalPrice()
        totPrice = totPrices[0][0]

        return render_template('ConfirmPayment.html', cart=ticket_selected_count, rows=allTempTix, totPrice=totPrice, user=current_user_name)
    else:
        totPrices = mySql.totalPrice()
        totPrice = totPrices[0][0]

        if (not totPrice):
            eventList = mySql.retrieveFromEvents(' DISTINCT place')
            return render_template('home.html', cart=ticket_selected_count, title='Home', eventList=eventList, user=current_user_name)
        allTempTix = mySql.select_ticket(True)
        return render_template('ConfirmPayment.html', cart=ticket_selected_count, rows=allTempTix, totPrice=totPrice, user=current_user_name)


@app.route('/stripePayment/')
@login_required
def stripePayment():
    key = stripe_keys['publishable_key']
    # Since the amount of Stripe payment is represented in cents, to make it readable, times it by 100.
    amount = int(totPrice) * 100
    return render_template('StripeIndex.html', cart=ticket_selected_count, key=key, amount=amount, user=current_user_name)


@app.route('/cancelPayment')
@login_required
def cancelPayment():
    mySql.rollbackBoughtTicket()
    mySql.dropTemp()
    eventList = mySql.retrieveFromEvents(' DISTINCT place')
    global ticket_selected_count
    ticket_selected_count = len(mySql.select_ticket(True))
    return render_template('home.html', cart=ticket_selected_count, title='Home', eventList=eventList, user=current_user_name)


@app.route('/charge', methods=['POST'])
@login_required
def charge():
    # This amount is in cents.
    amount = int(totPrice) * 100


    # customer = stripe.Customer.create(
    #     email='customer@example.com',
    #     source=request.form['stripeToken']
    # )
    #
    # charge = stripe.Charge.create(
    #     customer=customer.id,
    #     amount=amount,
    #     currency='aud',
    #     description='Flask Charge'
    # )

    # Customer has paid! Everything good.. Now the blockchain...

    ### Do something about blockchain after payment ###
    datas = mySql.insertDataFromTemp()  # it will get all the tickets bought.

    filenameL = []

    # Looping all the events.
    for i in datas:
        eventVal = i[0]
        eventDateTime = i[1]
        seat = i[2]
        price = i[3]
        myMain.addData(eventVal, eventDateTime, seat, price)  # it only process one payment..
        a, _hash, _prehash = myMain.run()
        filenameL.append(a)  # Passing filename to the render_template parameter

        mySql.testBlockchain(eventVal, eventDateTime, seat, price, _hash, _prehash)

    mySql.deleteBoughtTicket()
    mySql.dropTempTable()
    global ticket_selected_count
    ticket_selected_count = len(mySql.select_ticket(True))
    #########################################

    return render_template('Confirmed.html', cart=ticket_selected_count, amount=amount / 100, tickets=filenameL, user=current_user_name)


@app.route('/ticket/<filename>', methods=['GET', 'POST'])
@login_required
def returnFile(filename):
    try:
        print(filename)
        return send_file('ticket/' + filename, attachment_filename=filename)
    except Exception as e:
        return str(e)


@app.route('/printBlockchain/')
@login_required
def printBlockchain():
    rows = mySql.getBlockchain()
    return render_template("listBlockchain.html", cart=ticket_selected_count, rows=rows, user=current_user_name)


@app.route('/delBc/')
@login_required
def deleteBc():
    mySql.delBlockchain()
    # rows = mySql.select_ticket(True)
    # return render_template("listBlockchain.html",rows = rows)
    eventList = mySql.retrieveFromEvents(' DISTINCT place')
    return render_template('home.html', cart=ticket_selected_count, title='Home', eventList=eventList, user=current_user_name)


@app.route('/delUsr/')
@login_required
def deleteUsr():
    mySql.deleteUsers()
    eventList = mySql.retrieveFromEvents(' DISTINCT place')
    return redirect(url_for('admin_home'))


# This is just for debuggin purposes..
@app.route('/debug/')
@login_required
def debug():
    mySql.dropTemp()
    return render_template('listBlockchain.html')

    place = "Event ABCDE"
    date = "27 - 11 - 2017 11:00 pm"
    seat = "1A"
    price = 109

    mySql.insertData(True, place, date, seat, price)

    place = "Event 2"
    date = "27 - 11 - 2017 11:00 pm"
    seat = "3Z"
    price = 109000

    mySql.insertData(True, place, date, seat, price)
    datas = mySql.insertDataFromTemp()

    rows = mySql.select_ticket(True)
    return render_template('ConfirmPayment.html')
    return render_template('Confirmed.html', mess=datas)


"""
Admin Pages
"""


@app.route('/admin/')
@login_required
def admin_home():
    if mySql.getUser(current_user_account) is not None and mySql.getUser(current_user_account)[3] == 1:
        return render_template('admin/home.html')
    else:
        return redirect(url_for('main'))


@app.route('/admin/users/')
@login_required
def admin_users():
    if mySql.getUser(current_user_account) is not None and mySql.getUser(current_user_account)[3] == 1:
        user_list = mySql.admin_get_users()
        return render_template('admin/users.html', users=user_list)
    else:
        return redirect(url_for('main'))


@app.route('/admin/events/', methods=['GET', 'POST'])
@login_required
def admin_events():
    if mySql.getUser(current_user_account) is not None and mySql.getUser(current_user_account)[3] == 1:
        if request.method == 'POST':
            if request.form['submit']:
                delete_event_id = request.form['submit']
                mySql.admin_delete_event(delete_event_id)
                if request.form['submit'] == 'Add':
                    new_place = request.form['place']
                    new_time = request.form['time']
                    new_seat = request.form['seat']
                    new_price = request.form['price']
                    mySql.admin_add_event(new_place, new_time, new_seat, new_price)
        events_list = mySql.admin_get_events()
        return render_template('admin/events.html', events=events_list)
    else:
        return redirect(url_for('main'))




@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == "__main__":
    app.run(debug=True)
