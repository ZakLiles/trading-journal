import csv
import datetime
from model import User, Trade, Order, db

def find_orders(file_path):
    orders_list=[]
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        account_trade_history = False

        for row in csv_reader:

            if len(row) > 0 and account_trade_history == False: 
                #Finds where Account Trade History section begins
                if "Account Trade History" in row[0]:
                    account_trade_history = True
                    trade_counter = 0
                    print("Found Account Trade History")
                    continue
            #reverts boolean after end of trade history is reached
            elif len(row) == 0 and account_trade_history == True:
                account_trade_history = False

            #Ignore rows that aren't in Account Trade History section
            if account_trade_history:
                #Skips first row of trade history, which is column headers
                if trade_counter > 0:
                    orders_list.append(row)
                trade_counter += 1
    
    return orders_list

def create_order(order_row, user_id):
    exec_time = datetime.datetime.strptime(order_row[1], "%m/%d/%y %H:%M:%S")
    spread = order_row[2]
    side = order_row[3]
    qty = int(order_row[4])
    pos_effect = order_row[5]
    symbol = order_row[6]

    #expiration date is only for options and future contracts
    #future contracts only have the month and year because it always expires on the third friday of the month
    if order_row[7] == '':
        expiration = None
    elif len(order_row[7].split()) == 2:
        expiration = datetime.datetime.strptime(order_row[7], "%b %y")
    elif len(order_row[7].split()) == 3:
        expiration = datetime.datetime.strptime(order_row[7], "%d %b %y")

    #strike price is for only options
    if order_row[8] == '':
        strike_price = None
    else:
        strike_price = float(order_row[8])

    type = order_row[9]
    price = float(order_row[10])
    order_type = order_row[12]

    #query database to find open trade for the user that matches the order symbol, spread, & side
    open_trade = Trade.query.filter_by(user_id=user_id, symbol=symbol, spread=spread, open=True).first()

    if open_trade is None:

        #make a new trade if no open trade is found
        open_trade = Trade(user_id=user_id, open_date=exec_time, symbol=symbol, entry_price=price, side=side, spread=spread, position=qty)
        db.session.add(open_trade)
        db.session.commit()
        order = Order(trade_id=open_trade.trade_id, exec_time=exec_time, spread=spread, side=side, qty=qty, pos_effect=pos_effect, symbol=symbol, expiration=expiration, strike_price=strike_price, type=type, price=price, order_type=order_type)
        db.session.add(order)
        db.session.commit()

    else:

        #check if new order qty is large enough to close the current open position and one is positive while the other is negative
        #split order into two separate orders, one that closes the open trade, one that opens a new trade
        if abs(qty) > abs(open_trade.position) and ((open_trade.position ^ qty) < 0): 
            
            #split qty's apart
            qty_one = open_trade.position * -1
            qty_two = qty - qty_one

            #closing order
            order_one = Order(trade_id=open_trade.trade_id, exec_time=exec_time, spread=spread, side=side, qty=qty_one, pos_effect=pos_effect, symbol=symbol, expiration=expiration,strike_price=strike_price, type=type, price=price, order_type=order_type)
            open_trade.exit_price = price
            open_trade.position = 0
            open_trade.open = False
            db.session.commit()
            if ((open_trade.entry_price < open_trade.exit_price) and (open_trade.side=="BUY")) or ((open_trade.entry_price > open_trade.exit_price) and open_trade.side=="SELL"):
                open_trade.result = "WIN"
            else:
                open_trade.result = "LOSS"

            db.session.add(order_one)

            #new opening trade
            new_open_trade = Trade(user_id=user_id, open_date=exec_time, symbol=symbol, entry_price=price, side=side, spread=spread, position=qty_two)
            db.session.add(new_open_trade)
            db.session.commit()

            #new opening order
            order_two = Order(trade_id=new_open_trade.trade_id, exec_time=exec_time, spread=spread, side=side, qty=qty_two, pos_effect=pos_effect, symbol=symbol, expiration=expiration,strike_price=strike_price, type=type, price=price, order_type=order_type)
            db.session.add(order_two)
            db.session.commit()
        else:
            #add order to open trade
            order = Order(trade_id=open_trade.trade_id, exec_time=exec_time, spread=spread, side=side, qty=qty, pos_effect=pos_effect, symbol=symbol, expiration=expiration, strike_price=strike_price, type=type, price=price, order_type=order_type)
            db.session.add(order)
            open_trade.position += qty
            db.session.commit()

            #if trade position equals zero, consider the trade close
            if open_trade.position == 0:
                open_trade.exit_price = price
                open_trade.open = False
                db.session.commit()
                if ((open_trade.entry_price < open_trade.exit_price) and (open_trade.side=="BUY")) or ((open_trade.entry_price > open_trade.exit_price) and open_trade.side=="SELL"):
                    open_trade.result = "WIN"
                else:
                    open_trade.result = "LOSS"
                db.session.commit()




