import json
from datamodel import Order,TradingState
"""The strategies here that will be used are 
Inventory control for risk management
Market making for ASH and mean reversion for int
"""

class Trader:
    def run(self, state:TradingState):
        result={}
        try:
            data=json.loads(state.traderData) if state.traderData else {}
        except:
            data={}
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
                skew=position*0.1
                buy_price = min(best_bid + 1-skew, best_ask - 1)
                sell_price = max(best_ask - 1-skew, best_bid + 1)
                
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
                
                prev_price=data.get(product,mid_price)
                if spread<1:
                    result[product]=orders
                    continue
                
                fair_price=prev_price * 0.8 +0.2*mid_price
                prev_vol=data.get(product+"_vol",1)
                vol=0.8* prev_vol +0.2 *abs(mid_price-prev_price)
                z=(mid_price-fair_price)/max(vol,1)
                base_size=5
                size=base_size+int(abs(z))
                size=min(size,10)
                buy_price = min(best_bid + 1, best_ask - 1)
                sell_price = max(best_ask - 1, best_bid + 1)
                if z<-1:
                    orders.append(Order(product,buy_price,size))
                elif z>1:
                    orders.append(Order(product,sell_price,-size))
                else:
                    if position < 10:
                        orders.append(Order(product, buy_price, 3))
                    if position > -10:
                        orders.append(Order(product, sell_price, -3))
                data[product+"_vol"]=vol
                if position>15:
                    orders=[o for o in orders if o.quantity <0]
                if position<-15:
                    orders=[o for o in orders if o.quantity >0]
            result[product]=orders
        new_trader_data={}
        for p in state.order_depths:
            od=state.order_depths[p]
            if od.buy_orders and od.sell_orders:
                new_trader_data[p]=(max(od.buy_orders)+min(od.sell_orders))/2
    
        return result ,0,json.dumps(data)