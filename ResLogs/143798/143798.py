import json
from datamodel import Order, TradingState

class Trader:
    def run(self, state: TradingState):
        result = {}
        try:
            data = json.loads(state.traderData) if state.traderData else {}
        except:
                data = {}

                # ✅ preserve past memory
                new_trader_data = data.copy()

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

                        # Slight aggression boost
                        if abs(position) < 3:
                            buy_qty = 10
                            sell_qty = 10
                        elif abs(position) < 5:
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
                            orders.append(Order(product, buy_price - 1, 4))
                            orders.append(Order(product, buy_price - 2, 3))

                        if sell_qty > 0:
                            orders.append(Order(product, sell_price, -sell_qty))
                            orders.append(Order(product, sell_price + 1, -4))
                            orders.append(Order(product, sell_price + 2, -3))

                    # ================= INT =================
                    elif product == "INTARIAN_PEPPER_ROOT":
                        spread = best_ask - best_bid

                        if spread <= 0:
                            result[product] = orders
                            continue

                        prev_price = data.get(product, mid_price)
                        prev_vol = data.get(product + "_vol", 1)

                        # Fair price (mean + trend)
                        fair_price = 0.7 * prev_price + 0.3 * mid_price
                        trend = mid_price - prev_price
                        fair_price += 0.25 * trend

                        # Volatility
                        vol = 0.7 * prev_vol + 0.3 * abs(mid_price - prev_price)

                        # Z-score
                        z = (mid_price - fair_price) / max(vol, 1)

                        buy_price = int(round(min(best_bid + 1, best_ask - 1)))
                        sell_price = int(round(max(best_ask - 1, best_bid + 1)))

                        # Dynamic sizing
                        size = min(10, 5 + int(abs(z) * 2))

                        # ✅ loosened threshold → more trades
                        if z < -0.8:
                            orders.append(Order(product, buy_price, size))
                        elif z > 0.8:
                            orders.append(Order(product, sell_price, -size))
                        else:
                            if position < 10:
                                orders.append(Order(product, buy_price, 3))
                            if position > -10:
                                orders.append(Order(product, sell_price, -3))
                        new_trader_data[product + "_vol"] = vol

                    result[product] = orders

                    
                    new_trader_data[product] = mid_price

                return result, 0, json.dumps(new_trader_data)