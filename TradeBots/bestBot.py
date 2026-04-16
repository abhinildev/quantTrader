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

                # ================= ASH (UNCHANGED - STABLE) =================
                if product == "ASH_COATED_OSMIUM":
                    spread = best_ask - best_bid

                    if spread < 2:
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

                    anchor_price = 10000

                    if best_ask < anchor_price:
                        orders.append(Order(product, best_ask, 10))

                    if best_bid > anchor_price:
                        orders.append(Order(product, best_bid, -10))

                    if buy_qty > 0:
                        orders.append(Order(product, buy_price, buy_qty))
                        orders.append(Order(product, buy_price - 1, buy_qty // 3))
                        orders.append(Order(product, buy_price - 2, buy_qty // 4))

                    if sell_qty > 0:
                        orders.append(Order(product, sell_price, -sell_qty))
                        orders.append(Order(product, sell_price + 1, -(sell_qty // 4)))
                        orders.append(Order(product, sell_price + 2, -(sell_qty // 3)))

                # ================= INT (FIXED STRATEGY) =================
                elif product == "INTARIAN_PEPPER_ROOT":
                    spread = best_ask - best_bid

                    if spread <= 0:
                        result[product] = orders
                        continue

                    prev_price = data.get(product, mid_price)
                    prev_vol = data.get(product + "_vol", 1)

                    # ===== PRICE SIGNAL =====
                    trend = mid_price - prev_price
                    fair_price = 0.65 * prev_price + 0.35 * mid_price + 0.35 * trend

                    vol = 0.7 * prev_vol + 0.3 * abs(trend)

                    z = (mid_price - fair_price) / max(vol * 0.7, 1)

                    # ===== ORDER BOOK IMBALANCE (NEW EDGE) =====
                    bid_vol = sum(order_depth.buy_orders.values())
                    ask_vol = -sum(order_depth.sell_orders.values())
                    imbalance = (bid_vol - ask_vol) / max(bid_vol + ask_vol, 1)

                    if abs(imbalance) > 0.5:
                        z += imbalance * (0.8 + 0.4 * abs(imbalance))

                    z += 0.6 * imbalance

                    inventory_bias = position/20
                    z -= 0.35 * inventory_bias

                    # ===== INVENTORY CONTROL =====
                    if position > 10:
                        z -= 0.3
                    elif position < -10:
                        z += 0.3

                    # edge = max(1, spread // 2)
                    # buy_price = int(round(best_bid + edge))
                    # sell_price = int(round(best_ask - edge))
                    size = min(20, 8 + int(abs(z) * 3))

                    if abs(z) > 1.5:
                        size += 5
                    if abs(z) > 2.0:
                        size += 5


                    if abs(z) < 0.7:
                        buy_price = best_bid + 1
                        sell_price = best_ask - 1
                    elif abs(z) < 1.5:
                        buy_price = best_bid + 2
                        sell_price = best_ask - 2

                        if imbalance > 0:
                            buy_price += 1   # slight push
                        else:
                            sell_price -= 1  # slight push
                        orders.append(Order(product, best_bid + 1, size // 3))
                    else:
                        buy_price = best_ask
                        sell_price = best_bid

                    # ===== MAIN STRATEGY =====
                    threshold = 0.65
                    if abs(imbalance) > 0.6:
                        threshold -= 0.1
                    if z < -threshold:
                        orders.append(Order(product, buy_price, size))
                        orders.append(Order(product, min(buy_price + 1, best_ask), size // 2))
                    elif z > threshold:
                        orders.append(Order(product, sell_price, -size))
                        orders.append(Order(product, max(sell_price - 1, best_bid), -size // 2))
                    else:
                        pass

                    # ===== CONTROLLED AGGRESSION =====
                    # if abs(z) > 1.2:
                    #     if z < 0:
                    #         orders.append(Order(product, best_ask, size // 3))
                    #     else:
                    #         orders.append(Order(product, best_bid, -size // 3))

                    new_trader_data[product + "_vol"] = vol

                result[product] = orders
                new_trader_data[product] = mid_price

            return result, 0, json.dumps(new_trader_data)

        except Exception as e:
            return {}, 0, json.dumps(data)