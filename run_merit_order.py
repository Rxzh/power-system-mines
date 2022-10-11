from merit_order import MeritOrder

dict_pmax = {
    "nuclear" : 1363,
    "gas" : 286,
    "coal" : 34
    
}

dict_price = {
    "nuclear": 5,
    "gas" : 18.5,
    "coal" : 30
}

demand = 1500

mo = MeritOrder(dict_pmax, dict_price, demand)

print(mo.compute_electricity_price())

mo.plot()


