from merit_order import MeritOrder

dict_pmax = {
    "nuclear" : 100,
    "gas" : 160,
    "coal" : 50
    
}

dict_price = {
    "nuclear": 5,
    "gas" : 18.5,
    "coal" : 30
}

demand = 300

mo = MeritOrder(dict_pmax, dict_price, demand)

print(mo.compute_electricity_price())

mo.plot()


