import json
from datamodel import Order, TradingState

class Trader:
    def run(self, state: TradingState):
        result = {}

        try:
            data = json.loads(state.traderData) if state.traderData else {}
        except:
            data = {}

        new_trader_data = {}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            if not order_depth.buy_orders or not order_depth.sell_orders:
                result[product] = orders
                continue

            best_bid = max(order_depth.buy_orders)
            best_ask = min(order_depth.sell_orders)
            mid_price = (best_bid + best_ask) / 2
            position = state.position.get(product, 0)

            if product == "ASH_COATED_OSMIUM":
                spread = best_ask - best_bid

                if spread < 1.5:
                    result[product] = orders
                    continue

                buy_price = min(best_bid + 1, best_ask - 1)
                sell_price = max(best_ask - 1, best_bid + 1)

                skew = position * 0.05
                buy_price -= skew
                sell_price -= skew

                buy_price = int(round(buy_price))
                sell_price = int(round(sell_price))

                if abs(position) < 5:
                    buy_qty = 9
                    sell_qty = 9
                else:
                    buy_qty = 8
                    sell_qty = 8

                if position > 18:
                    buy_qty = 0
                if position < -18:
                    sell_qty = 0

                if buy_qty > 0:
                    orders.append(Order(product, buy_price, buy_qty))
                    orders.append(Order(product, buy_price - 1, 3))
                    orders.append(Order(product, buy_price - 2, 2))

                if sell_qty > 0:
                    orders.append(Order(product, sell_price, -sell_qty))
                    orders.append(Order(product, sell_price + 1, -3))
                    orders.append(Order(product, sell_price + 2, -2))

            elif product == "INTARIAN_PEPPER_ROOT":
                spread = best_ask - best_bid

                if spread < 1:
                    result[product] = orders
                    continue

                prev_price = data.get(product, mid_price)

                fair_price = 0.8 * prev_price + 0.2 * mid_price

                trend = mid_price - prev_price
                fair_price += 0.1 * trend

                threshold = 0.45

                buy_price = min(best_bid + 1, best_ask - 1)
                sell_price = max(best_ask - 1, best_bid + 1)

                buy_qty = 7
                sell_qty = 7

                if abs(mid_price - fair_price) > 1.8:
                    buy_qty = 9
                    sell_qty = 9

                if mid_price < fair_price - threshold:
                    orders.append(Order(product, buy_price, buy_qty))
                elif mid_price > fair_price + threshold:
                    orders.append(Order(product, sell_price, -sell_qty))
                else:
                    if position < 10:
                        orders.append(Order(product, buy_price, 3))
                    if position > -10:
                        orders.append(Order(product, sell_price, -3))

                if position > 18:
                    orders = [o for o in orders if o.quantity < 0]
                    orders.append(Order(product, best_bid, -6))

                if position < -18:
                    orders = [o for o in orders if o.quantity > 0]
                    orders.append(Order(product, best_ask, 6))

            result[product] = orders
            new_trader_data[product] = mid_price

        return result, 0, json.dumps(new_trader_data)