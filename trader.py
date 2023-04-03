import MetaTrader5 as mt
import pandas as pd
import plotly.express as px
from datetime import datetime

import ini_reader

mt.initialize()

tp_pip = int(ini_reader.props["sl_pip"])
sl_pip = int(ini_reader.props["tp_pip"])
lot = float(ini_reader.props["lot"])

mt.login(ini_reader.props["login"], ini_reader.props["password"], ini_reader.props["server"])

account_info = mt.account_info()
print(account_info)

print()
print("Login: ", account_info.login)
print("Balance: ", account_info.balance)
print("Equity: ", account_info.equity)

num_symbols = mt.symbols_total()
print("No. of symbols allowed: ", str(num_symbols))
print("Total positions: " + str(mt.positions_total()))


def get_current_profit():
    profit = 0
    positions = mt.positions_get()
    for position in positions:
        profit += position.profit
    return profit


def is_position_exist(symbol, buy_or_sell):
    try:
        positions = mt.positions_get()
        if buy_or_sell == 'BUY':
            type = 0
        else:
            type = 1
        for position in positions:
            if position.symbol == symbol and position.type == type:
                return True;
    except:
        return False


def get_current_price(symbol, type):
    return mt.symbol_info_tick(symbol).ask if type == 0 else mt.symbol_info_tick(symbol).bid


def get_all_positions_by_symbol(symbol):
    symbol_positions = []
    comments = []
    last_order_id =0
    positions = mt.positions_get()
    for position in positions:
        if position.symbol == symbol:
            comment = position.comment.replace("Order","")
            comments.append(int(comment))
            symbol_positions.append(position);
    last_order_id = max(comments) if len(comments)>0 else 0

    return symbol_positions, last_order_id


def change_target_price_for_all_position_by_symbol(symbol, new_tp, type):
    point = mt.symbol_info(symbol).point
    ask_price = mt.symbol_info_tick(symbol).ask
    bid_price = mt.symbol_info_tick(symbol).bid

    if type == "BUY":
        tp = ask_price + new_tp * point
    if type == "SELL":
        tp = bid_price - new_tp * point

    decimal_count = len(str(ask_price).split('.')[1])
    new_tp = round(tp, decimal_count)

    positions = mt.positions_get()
    for position in positions:
        if position.symbol == symbol:
            request = {
                "action": mt.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "symbol": position.symbol,
                "tp": new_tp,
            }
            ordeshr = mt.order_send(request)

def load_open_positions():

    positions_dict = {}
    all_symbols =[]
    positions = mt.positions_get()
    for position in positions:
        if position.symbol not in all_symbols:
            all_symbols.append(position.symbol)

    for symbol in all_symbols:
        comments = []
        for position in positions:
            if position.symbol == symbol:
                try:
                    comments.append(int(position.comment.replace("Order", "")))
                except:
                    pass

        for position in positions:
            if position.symbol == symbol and position.comment == "Order"+str(max(comments)):
                sl = 0.0
                if position.type == 0:
                    point = mt.symbol_info(symbol).point
                    sl = position.price_open - sl_pip * point
                    if 'JPY' in symbol:
                        sl = position.price_open - sl_pip*3 * point
                    decimal_count = len(str(position.price_open).split('.')[1])
                    sl = round(sl, decimal_count)
                if position.type == 1:
                    point = mt.symbol_info(symbol).point
                    sl = position.price_open + sl_pip * point
                    if 'JPY' in symbol:
                        sl = position.price_open + sl_pip*3 * point
                    decimal_count = len(str(position.price_open).split('.')[1])
                    sl = round(sl, decimal_count)
                positions_dict[symbol]= [sl, position.tp, "BUY" if position.type== 0 else "SELL", "Order"+str(max(comments))]
    return positions_dict


def close_all_positions_by_symbol(symbol):
    positions = mt.positions_get()
    for position in positions:
        if position.symbol == symbol:
            request = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "position": position.ticket,
                "type": 1 if position.type == 0 else 0,
                "price": mt.symbol_info_tick(position.symbol).ask if type == 0 else mt.symbol_info_tick(position.symbol).bid,
                "deviation": 20,
                "type_time": mt.ORDER_TIME_GTC,
            }
            order = mt.order_send(request)

    positions = mt.positions_get()
    count = 0
    for position in positions:
        if position.symbol == symbol:
            count += 1
    if count == 0:
        print("All position closed and booked profit")
        print("New positions will be triggered after 10 min or so")
        return True
    return False


def close_all_positions():
    positions = mt.positions_get()
    for position in positions:
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "position": position.ticket,
            "type": 1 if position.type == 0 else 0,
            "price": mt.symbol_info_tick(position.symbol).ask if type == 0 else mt.symbol_info_tick(position.symbol).bid,
            "deviation": 20,
            "type_time": mt.ORDER_TIME_GTC,
            # "type_filling": mt.ORDER_FILLING_RETURN,
        }
        order = mt.order_send(request)

    positions = mt.positions_get()
    if len(positions) == 0:
        print("All position closed and booked profit")
        print("New positions will be triggered after 10 min or so")
        return True
    return False


def place_order(symbol, type, comment):
    point = mt.symbol_info(symbol).point
    ask_price = mt.symbol_info_tick(symbol).ask
    bid_price = mt.symbol_info_tick(symbol).bid

    if type == "BUY":
        order_type = mt.ORDER_TYPE_BUY
        sl = ask_price - sl_pip * point
        tp = ask_price + tp_pip * point
        if 'JPY' in symbol:
            sl = ask_price - sl_pip*3 * point
            tp = ask_price + tp_pip*3 * point

    if type == "SELL":
        order_type = mt.ORDER_TYPE_SELL
        sl = bid_price + sl_pip * point
        tp = bid_price - tp_pip * point
        if 'JPY' in symbol:
            sl = bid_price + sl_pip*3 * point
            tp = bid_price - tp_pip*3 * point

    decimal_count = len(str(ask_price).split('.')[1])
    sl = round(sl, decimal_count)
    tp = round(tp, decimal_count)



    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": mt.symbol_info_tick(symbol).ask if order_type == 0 else mt.symbol_info_tick(symbol).bid,
        "sl": 0.0,
        "tp": tp,
        "deviation": 8,
        "magic": 199621147,
        "comment": comment,
        "type_time": mt.ORDER_TIME_GTC,
        # "type_filling": mt.ORDER_FILLING_RETURN,

    }

    order = mt.order_send(request)

    return order, sl, tp
