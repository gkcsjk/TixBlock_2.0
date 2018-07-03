# TixBlock_2.0
This project is to simulate the process of booking tickets
Most of the work was done by Erick Lie. What I did is to organise html structure, add admin tool and login function.
## Project Structure
```
  .
    ├── static                     # Static files
    │   ├── js                     # bootstrap file
    |   └── css                    # Css files
    ├── templates                  # Html templates
    │   ├── admin                  # Admin pages templates
    │   │   ├── base.html          # The admin pages' base, defined html head, page header, ...
    │   │   ├── events.html        # The page to view/add/remove events
    │   │   ├── home.html          # Admin Home page
    │   │   └── users.html         # The page to view existing users
    │   ├── base.html              # Pages' base, defined html head, page header, ...
    |   ├── home.html              # Home page, list all available events
    |   ├── login.html             # Login page
    |   ├── ConfirmPayment.html    # Comfirm payment page, show all the selected tickets and price
    |   ├── Confirmed.html         # Payment successful page, download booked tickets
    |   ├── StripeCharges.html     # Not used
    |   ├── StripeIndex.html       # Stripe payment page
    |   ├── StripeLayout.html      # Not used
    |   ├── cart.html              # Not used
    |   ├── chooseSeat.html        # choose event seat page
    |   ├── chooseTime.html        # choose event time page
    |   ├── listBlockchain.html    # show existing blocks
    |   └── myDebug.html           # Not used
    ├── ticket                     # Store all the booked tickets
    |   ├── [filename].pdf         # ticket info
    |   └── [filename].png         # QRcode
    ├── app.py                     # Flask application logic file
    ├── Stripe.py                  # Stripe payment logic file
    ├── block.py                   # Define block data structure 
    ├── blockchain.py              # Define blockchain data structure
    ├── user.py                    # Define user's data structure
    ├── mySql.py                   # Database operations
    ├── thisMain.py                # main logic including adding blocks, generating tickets, creating user
    ├── main.py                    # Not used
    ├── myPayment.py               # Not used
    ├── database.db                # sqlite database file
    ├── requirements.txt           # requirements generated by pip
    └── README.md
```
## Configure Environment
* Python 3.6.5 with pip installed
* You may use virtualenv to build your python environment
* You may use Pycharm IDE to create your virtual environment as well:
```
https://www.jetbrains.com/help/pycharm/quick-start-guide.html
```
* Please refer to ```requirements.txt```. To install all requirements:
```
pip install -r requirements.txt
```
## run a test
* Please refer to [flask quickstart](http://flask.pocoo.org/docs/1.0/quickstart/)
* If you are using Pycharm, you can configure at ```Run->Edit Configurations``` and set the target to ```app.py```.
You can also change other setting such as environment, Python interpreter, etc.

## run at PythonAnywhere.com
* Register/Login to [PythonAnywhere](https://www.pythonanywhere.com/), you will be directed into ```Dashboard tag``` after login.
You can see there are six tabs ```Dashboard```, ```Consoles```, ```Files```, ```Web```, ```Task```, and ```Database```.
* Create a new web app in ```Web tab``` with the option ```Flask``` in ```Python 3.6```
* Start a new console in ```Consoles tab``` and clone the project to a proper path
```
git clone https://github.com/gkcsjk/TixBlock_2.0.git
```
* Install all the dependencies
``` 
pip3 install -r requirments.txt
```
* In the ```Web tab```, change the ```Source Code```, ```Working directory``` to your file path, and modify the ```WSGI configuration file``` to make sure that they match your project path
* You site should now be well configured, if not, please refer to ```Log files``` in ```Web tab``` for more information.
* You can view your files in ```File tab``` as well.


