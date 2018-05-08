import stripe


class Stripe:
    def __init__(self):
        self.apiKey = "sk_test_pS9qQQhUxOv807oJsijQdgPH"
        self.clientID = "pk_test_qSr906RDQZrsoTfjfRCvXvgE"
        self.currency = "AUD"
        self.chargeIDList = []

        self.customerList = []

        self.configure()
        self.autoPagCust()  # Populate the customer list from the dashboard

    def configure(self):
        stripe.api_key = self.apiKey
        stripe.client_id = self.clientID

    def createCharge(self, amount, desc=''):
        # print("Attempting charge..!!")
        """
        If the amount is 10, then it will be 10c. If it's 10000 it will be $100.
        By the end of the creation of class charge, it will be straight away created and authorized in the system.

        This function gets 2 parameters:
        - Amount : which is the amount going to be paid
        - Desc : Description of the items, default is empty.
        """

        r = stripe.Charge.create(
            amount=amount,
            currency=self.currency,
            description=desc,
            source="tok_visa",  # obtained with Stripe.js
        )
        self.chargeIDList.append(r['id'])  # Adding chargeID to the list.

        return r['id']  # Get the ID of the charge or payment.

    # print('%r' % (r))
    # print('Amount:{}.'.format(r['amount']))

    def retrieveCharge(self):
        a = self.chargeIDList[-1]
        return stripe.Charge.retrieve(a, self.apiKey)

    def myPayout(self, amt):
        return stripe.Payout.create(
            amount=amt,
            currency=self.currency,
            source_type="bank_account")

    def addCust(self, custEmail, acctBal):
        if (not self.isDuplicateCust(custEmail, acctBal)):
            # Creating a customer
            theCust = stripe.Customer.create(
                email=custEmail,
                account_balance=acctBal
            )

            # Add customer to the list
            self.customerList.append(theCust)

            customerId = theCust["id"]

            """
            # Subscribe the customer..
            plan = "basic"
            subscribe = stripe.Subscription.create(
            customer=customerId,
            items=[{"plan":plan}]
            )
            """
        else:
            print("DUPLICATE FOUND:\nemail: {}\nPlease check your email!\n".format(custEmail))

    def isDuplicateCust(self, custEmail, acctBal):
        # Return true if there is duplicate, false otherwise.

        custEmailList = [x["email"] for x in self.customerList]

        if (custEmail not in custEmailList):
            return False
        return True

    def autoPagCust(self):
        customers = stripe.Customer.all(limit=1)
        for customer in customers.auto_paging_iter():
            self.customerList.append(customer)

    """
    # How do we know if the charge / payment is duplicate e.g what if client is doing it in purpose?
    def autoPagCharge(self):
        charges = stripe.Charge.list(limit=3)
        for i in charges:
            print(i)
    """


if __name__ == "__main__":
    import random

    myStripe = Stripe()
    descrip = "Description 1."
    amt = random.randint(1, 1000000)
    # myStripe.createCharge(amt, descrip)
    # print(myStripe.retrieveCharge())
    myStripe.createCharge(20000)

    # Accepted customer 1.
    email1, acct1 = "1@gmail.com", "0"
    myStripe.addCust(email1, acct1)

    # Accepted customer 2
    email2, acct2 = "2@gmail.com", "3"
    myStripe.addCust(email2, acct2)

    # This should print duplicate found
    myStripe.addCust(email1, acct2)

    # This should print duplicate found as well.
    myStripe.addCust(email1, "12392198123")
