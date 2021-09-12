import portfolio as pf
import pprint as pp

symbol = 'TQQQ'
portf = pf.portfolio(10000)

print(portf.amount)
portf.buy_position(symbol, 10, 20)
portf.sell_position(symbol, 10, 25)
print(portf.amount, portf.profit_loss)
portf.buy_position(symbol, 10, 20)
portf.sell_position(symbol, 10, 25)
print(portf.amount, portf.profit_loss)
portf.buy_position(symbol, 10, 20)
portf.sell_position(symbol, 10, 25)
print(portf.amount, portf.profit_loss)
portf.buy_position(symbol, 10, 20)
portf.sell_position(symbol, 10, 11)
print(portf.amount, portf.profit_loss)
pp.pprint(portf.history)
portf.print_profit_loss()