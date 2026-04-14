import json
from datamodel import Order,TradingState
"""The strategies here that will be used are 
Market making for ASH and momentum for int
Inventory control for risk management
"""

class Trader:
    def run(self, state:TradingState):
        result={}
        for product in state.order_depths:
            order_depth=state.order_depths[product]
            orders=[]
            # skip if no data
            if not order_depth.buy_orders or not order_depth.sell_orders:
                result[product]=orders
                continue
            best_bid=max(order_depth.buy_orders)
            best_ask=min(order_depth.sell_orders)
            mid_price=(best_bid+best_ask)/2
            position=state.position.get(product,0)
            ###ASH
            if product=="ASH_COATED_OSMIUM":
                ### Market Matching
                spread=best_ask-best_bid
                if spread<2:
                    result[product]=orders
                    continue
                
                buy_price=best_bid+1
                sell_price=best_ask-1
                
                buy_qty=5
                sell_qty=5
                ###Inventory control
                if position>15:
                    buy_qty=0
                if position<-15:
                    sell_qty=0
                if buy_qty>0:
                    orders.append(Order(product,buy_price,buy_qty))
                if sell_qty>0:
                    orders.append(Order(product,sell_price,-sell_qty))
            ###INT
            elif product=="INTARIAN_PEPPER_ROOT":
                spread = best_ask - best_bid
                try:
                    if state.traderData:
                        data=json.loads(state.traderData)
                    else:
                        data={}
                except:
                    data={}
                prev_price=data.get(product,mid_price)
                if spread<1:
                    result[product]=orders
                    continue
                
                fair_price=prev_price * 0.8 +0.2*mid_price
                buy_qty=7
                sell_qty=7
                if abs(mid_price-fair_price)>3:
                    buy_qty=10
                    sell_qty=10
                threshold=1
                ## Momentum Logic
                if mid_price<fair_price-threshold:
                    orders.append(Order(product,best_bid+1,buy_qty))
                elif mid_price>fair_price+threshold:
                    orders.append(Order(product,best_ask-1,-sell_qty))
                else:
                    if position<10:
                        orders.append(Order(product,best_bid+1,3))
                    if position>-10:
                        orders.append(Order(product,best_ask-1,-3))
                if position>15:
                    orders=[o for o in orders if o.quantity <0]
                if position<-15:
                    orders=[o for o in orders if o.quantity >0]
            result[product]=orders
        new_trader_data={p:(max(state.order_depths[p].buy_orders)+min(state.order_depths[p].sell_orders))/2 for p in state.order_depths}
        return result ,0,json.dumps(new_trader_data)