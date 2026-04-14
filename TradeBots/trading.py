from datamodel import Order, TradingState
"""
The strategies here that are used are Market making for emeralds 
Mean reversion is being used for tomatoes
Inventory control is being used for risk management
"""
class Trader:
    def run(self, state: TradingState):
        res={}
        for product in state.order_depths:
            order_depth=state.order_depths[product]
            orders=[]
            # skip if no data
            if not order_depth.buy_orders or not order_depth.sell_orders:
                res[product]=orders
                continue
            best_bid=max(order_depth.buy_orders)
            best_ask=min(order_depth.sell_orders)
            mid_price=(best_bid+best_ask) /2
            position=state.position.get(product,0)            

            ###Emeralds
            if product=="EMERALDS":
                fair_price=10000
                ###Market matching
                buy_price= min(best_bid+1,best_ask-1)
                sell_price=max(best_ask-1,best_bid+1)
                
                buy_qty=5
                sell_qty=5
                ##Inventory control
                if position>15:
                    buy_qty=0
                if position<-15:
                    sell_qty=0
                if buy_qty>0:
                    orders.append(Order(product,buy_price,buy_qty))
                if sell_qty>0:
                    orders.append(Order(product,sell_price,-sell_qty))
            #tomatoes
            elif product == "TOMATOES":
                fair_price=5000
                buy_qty=max(1,5-abs(position)//5)
                sell_qty=max(1,5-abs(position)//5)
                ### Mean Reversion
                threshold=2
                if abs(mid_price-fair_price)<1:
                    res[product]=orders
                    continue
                if mid_price<fair_price-threshold:
                    # BUY cheap
                    orders.append(Order(product,best_bid+1,buy_qty))
                elif mid_price>fair_price+threshold:
                    # Sell expensive
                    orders.append(Order(product,best_ask-1,-sell_qty))            
                ### Light market making
                else:
                    spread=best_ask-best_bid
                    if spread>=3:
                        orders.append(Order(product,best_bid+1,buy_qty))
                        orders.append(Order(product,best_ask-1,-sell_qty))
                ##INVENTORY CONTROL
                if position>15:
                    orders=[o for o in orders if o.quantity < 0]
                if position<-15:
                    orders=[o for o in orders if o.quantity > 0]
            res[product]=orders
        return res,0,""