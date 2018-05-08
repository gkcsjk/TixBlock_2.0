import paypalrestsdk
import logging

# from paypalrestsdk import Payment

# logging.basicConfig(level=logging.INFO)

"""
TODO:
1. Items can be more than 1. Need to edit the way we calculate total.
2. Items need to be placed in one function. Hence we can call both for authorize and payment functions.
3. URL redirect to authorize still not there...
"""


class MyPayment:
    def __init__(self, item="", price=0, currency="", quantity=0):
        self.name = item
        self.price = price
        self.currency = currency
        self.quantity = quantity
        self.total = self.price * self.quantity

        self.configure()

    def configure(self):
        paypalrestsdk.configure({
            'mode': 'sandbox',
            'client_id': 'AaaBPJ7KbtQQnCGGawUnrVLBPe9LjeOaOGU14HdU_b9uI8Uj87EkRbwAuZcUT1VM1M2Ma2liZ3rEw9GN',
            'client_secret': 'EHeXa3aB0hMsPPF1--Hqkos-L67qOZ2QyI23FzxE6hZ4rk5M9CR04HVkTUc70hKlYuPvTW-QaNqKAlHV'})
        print("Successfully configuring paypal...")

    def setItem(self, item):
        self.item = item

    def setName(self, name):
        self.name = name

    def setCurrency(self, currency):
        self.currency = currency

    def setQuantity(self, quantity):
        self.quantity = quantity

    def setPrice(self, price):
        self.price = price

    def setPaymentIntent(self):
        self.payment['intent'] = 'authorize'

    def getPayment(self):
        """
        self.payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
        "payment_method": "paypal"},
        "redirect_urls": {
        "return_url": "http://localhost:3000/payment/execute=",
        "cancel_url": "http://localhost:3000/"},
        "transactions": [{
        "item_list": {
        "items": [{
        "name": self.name,
        "price":self.price,
        "currency": "AUD",
        "quantity": self.quantity}]},
        "amount": {
        "total": str(self.price * self.quantity),
        "currency": "AUD"},
        "description": "This is the payment transaction description."}]})
        """

        intent = "sale"  # Can also be "authorize"
        payer = {"payment_method": "paypal"}

        redirect_urls = {"return_url": "www.google.com", "cancel_url": "www.bing.com"}

        item_description = {"name": self.name, "price": self.price, "currency": self.currency,
                            "quantity": self.quantity}  # this could be more than one item..

        items = [item_description]  # Reckon this could be multiple. Get total from here!

        # This is only for one item. Imagine we have 2 or more items, we need one more variable to keep the values
        amount = {"total": self.price * self.quantity, "currency": self.currency}
        description = "Payment Description~"

        transactions = [{"item_list": {"items": items}, "amount": amount, "description": description}]

        self.payment = paypalrestsdk.Payment({
            "intent": intent,
            "payer": payer,
            "redirect_urls": redirect_urls,
            "transactions": transactions},
        )

        if self.payment.create():
            print("Payment[%s] created successfully" % (self.payment.id))
            for link in self.payment.links:
                if link.rel == "approval_url":
                    # Convert to str to avoid Google App Engine Unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    approval_url = str(link.href)
                    print("Redirect for approval: \n%s" % (approval_url))

                    import webbrowser
                    webbrowser.open(approval_url)

            return self.payment.id, approval_url
        else:
            print("Error while creating payment:")
            print(self.payment.error)

    def executePayment(self, pID, payerID):
        for i in pID:
            # Fetch Payment
            payment = paypalrestsdk.Payment.find(i)
            if (payment.execute({'payer_id': payerID})):
                print("Payment[%s] execute successfully" % (payment.id))
            else:
                print(payment.error)

        # Get List of Payments
        payment_history = paypalrestsdk.Payment.all({"count": len(pID)})
        for i in payment_history.payments:
            print("  -> Payment[%s]" % (payment.id))

    def getReturnURL(self):
        return self.payment['redirect_urls']['return_url']

    def testAuthorize(self):
        # To authorize payment, get the payment ID first to get the details of the payment and change the intent to authorize. That should be it...!!
        self.payment["intent"] = "authorize"

        # What I am doing here? It's basically the same as payment but different intent value. smh.
        total = 99
        intent = "authorize"
        transactions = []
        details = {"subtotal": "99"}
        amount = {"total": str(total),
                  "currency": self.currency, "details": details}

        description = "This is payment transaction description ~"

        payer = {"payment_method": "paypal"}

        redirect_urls = {"return_url": "www.google.com", "cancel_url": "www.bing.com"}

        item_description = {"name": self.name, "price": self.price, "currency": self.currency,
                            "quantity": self.quantity}  # this could be more than one item..
        items = [item_description]
        # This is only for one item. Imagine we have 2 or more items, we need one more variable to keep the values
        amount = {"total": self.price * self.quantity, "currency": self.currency}
        description = "Payment Description~"
        transactions = [{"item_list": {"items": items}, "amount": amount, "description": description}]

        self.authorize = paypalrestsdk.Payment({
            "intent": intent,
            "payer": payer,
            "redirect_urls": redirect_urls,
            "transactions": transactions},
        )

        print("Successful authorization!")
        return self.authorize


if __name__ == "__main__":
    test = MyPayment("MyItem", 20, "AUD", 1)
    paymentID, approvalURL = test.getPayment()

    print(test.payment)

    import webbrowser

    a = webbrowser.open(approvalURL)

    print(a)
