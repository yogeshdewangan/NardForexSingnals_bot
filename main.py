import time, ini_reader, trader, logging, get_signals

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s')

sl_tp_track_dic = {}


def get_time_date():
    from datetime import datetime
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def average(symbol):
    positions, last_order_id = trader.get_all_positions_by_symbol(symbol)
    sl = sl_tp_track_dic[symbol][0]
    tp = sl_tp_track_dic[symbol][1]
    buy_or_sell = sl_tp_track_dic[symbol][2]

    current_price = trader.get_current_price(symbol, buy_or_sell)
    # current_price = 140.450
    if buy_or_sell == "SELL":
        if current_price > sl:
            last_order_id = last_order_id + 1
            comment = "Order" + str(last_order_id)
            order, sl, tp = trader.place_order(symbol, buy_or_sell, comment)
            if order is not None and order.comment == "Request executed":
                sl_tp_track_dic[symbol] = [sl, tp, buy_or_sell, comment]
                print(get_time_date() + " Order placed: " + symbol + " " + buy_or_sell + " " + comment)

                # Change target price for all open positions  first_order - 200, second order - 300, third_order - 400
                half_tp = int(ini_reader.props["tp_pip"])/2
                if 'JPY' in symbol:
                    half_tp = int(ini_reader.props["tp_pip"])*3 / 2
                tp = last_order_id * half_tp + 10
                trader.change_target_price_for_all_position_by_symbol(symbol, tp, buy_or_sell)
                print(get_time_date() + " Changed tp : " + symbol + " " + buy_or_sell )

    if buy_or_sell == "BUY":
        if current_price < sl:
            last_order_id = last_order_id + 1
            comment = "Order" + str(last_order_id)
            order, sl, tp = trader.place_order(symbol, buy_or_sell, comment)
            if order is not None and order.comment == "Request executed":
                sl_tp_track_dic[symbol] = [sl, tp, buy_or_sell, comment]
                print(get_time_date() + " Order placed: " + symbol + " " + buy_or_sell + " " + comment)

                # Change target price for all open positions  first_order - 200, second order - 300, third_order - 400
                half_tp = int(ini_reader.props["tp_pip"])/2
                if 'JPY' in symbol:
                    half_tp = int(ini_reader.props["tp_pip"])*3 / 2
                tp = last_order_id * half_tp + 10
                trader.change_target_price_for_all_position_by_symbol(symbol, tp, buy_or_sell)
                print(get_time_date() + " Changed tp : " + symbol + " " + buy_or_sell)


if __name__ == '__main__':
    # while True:
    #     if trader.close_all_positions():
    #         break
    #     else:
    #         time.sleep(500)
    sl_tp_track_dic = trader.load_open_positions()

    while True:
        try:
            profit = trader.get_current_profit()
            # print("Profit: " + str(profit))
            if profit > int(ini_reader.props["close_all_at_profit"]):
                trader.close_all_positions()
        except Exception as e:
            print('Exception : Unable to get profit or close positions' + str(e))
            time.sleep(60)

        for item in sl_tp_track_dic:
            if ini_reader.props["average_trades"] == 'true':
                average(item)

        pair_dic = get_signals.signals()
        # pair_dic["USDJPY"] = {"price": 130.497, "BuyOrSell": "SELL"}
        # # print("Signals: " + str(pair_dic))
        if pair_dic != {}:
            for symbol in pair_dic:

                symbol = symbol.replace('/', '')
                if not trader.is_position_exist(symbol, pair_dic[symbol]["BuyOrSell"]):
                    try:
                        comment = "Order1"
                        order, sl, tp = trader.place_order(symbol, pair_dic[symbol]["BuyOrSell"], comment)
                        if order is not None and order.comment == "Request executed":
                            sl_tp_track_dic[symbol] = [sl, tp, pair_dic[symbol]["BuyOrSell"], comment]
                            print(get_time_date() + " Order placed: " + symbol + " " + pair_dic[symbol]["BuyOrSell"] + " " + comment)
                    except Exception as e:
                        print('Exception : Unable to get profit or close positions' + str(e))

        time.sleep(5)

