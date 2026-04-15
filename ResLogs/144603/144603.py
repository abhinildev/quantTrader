import json
from datamodel import Order, TradingState

class Trader:
    def run(self, state: TradingState):
        result = {}
        try:
            data = json.loads(state.traderData) if state.traderData else {}
        except:
            data = {}

        new_trader_data = data.copy()

        try:
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

                # ================= ASH =================
                if product == "ASH_COATED_OSMIUM":
                    spread = best_ask - best_bid

                    if spread < 1:
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
                        buy_qty = 14
                        sell_qty = 14
                    elif abs(position) < 10:
                        buy_qty = 12
                        sell_qty = 12
                    else:
                        buy_qty = 10
                        sell_qty = 10

                    if position > 18:
                        buy_qty = 0
                    if position < -18:
                        sell_qty = 0

                    if buy_qty > 0:
                        orders.append(Order(product, buy_price, buy_qty))
                        orders.append(Order(product, buy_price - 1, buy_qty//3))
                        orders.append(Order(product, buy_price - 2, buy_qty//4))

                    if sell_qty > 0:
                        orders.append(Order(product, sell_price, -sell_qty))
                        orders.append(Order(product, sell_price + 1, -(sell_qty//4)))
                        orders.append(Order(product, sell_price + 2, -(sell_qty//3)))

                # ================= INT =================
                elif product == "INTARIAN_PEPPER_ROOT":
                    spread = best_ask - best_bid

                    if spread <= 0:
                        result[product] = orders
                        continue

                    prev_price = data.get(product, mid_price)
                    prev_vol = data.get(product + "_vol", 1)

                    fair_price = 0.7 * prev_price + 0.3 * mid_price
                    trend = mid_price - prev_price
                    fair_price += 0.25 * trend

                    vol = 0.7 * prev_vol + 0.3 * abs(mid_price - prev_price)

                    z = (mid_price - fair_price) / max(vol, 1)
                    if position>10:
                        z-=0.3
                    elif position<-10:
                        z+=0.3
                    buy_price = int(round(min(best_bid + 1, best_ask - 1)))
                    sell_price = int(round(max(best_ask - 1, best_bid + 1)))

                    size = min(15, 5 + int(abs(z) * 2))
                    if abs(z)>1.5:
                        size+=2
                    if z < -0.5:
                   
                        orders.append(Order(product, buy_price, size))
                        orders.append(Order(product, buy_price + 1, size // 2))
                    elif z > 0.5:
                        orders.append(Order(product, sell_price, -size))
                        orders.append(Order(product, sell_price - 1, -size // 2))
                    else:
                        if position < 10:
                         orders.append(Order(product, buy_price, 5))
                        if position > -10:
                         orders.append(Order(product, sell_price, -5))


                    new_trader_data[product + "_vol"] = vol

                result[product] = orders
                new_trader_data[product] = mid_price

            return result, 0, json.dumps(new_trader_data)

        except Exception as e:
            
            return {}, 0, json.dumps(data)