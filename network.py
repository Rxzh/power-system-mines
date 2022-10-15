import pandas as pd
import matplotlib.pyplot as plt
import pandapower
from pandapower.plotting import simple_plotly
import pandapower.networks as pn
import pandapower.topology
import pandapower.plotting
from pandapower.plotting.plotly import pf_res_plotly
import pandapower.converter
import pandapower.estimation
import pandapower.test
import numpy as np
import sys
sys.path.append('../power-system-mines/')

from merit_order import MeritOrder

from violations import isConstraintsViolation

NUKE_COST = 30

# nuke = 55%
# coal = 30%
# gas = 15%


def assign_gen_types(network):
        
    t1,t2 = np.percentile(network.gen['p_mw'],[40,90])
    #print(t1, t2)
    n_coal,n_gas,n_nuke = 0,0,0
    
    for i in network.gen.index:
        if network.gen.loc[i,'p_mw'] <= t1:
            network.gen.loc[i,'name'] = 'coal_{}'.format(n_coal)
            n_coal += 1
        elif t1 < network.gen.loc[i,'p_mw'] <= t2:
            network.gen.loc[i,'name'] = 'gas_{}'.format(n_gas)
            n_gas += 1
        else:
            network.gen.loc[i,'name'] = 'nuke_{}'.format(n_nuke)
            n_nuke += 1

    t1,t2 = np.percentile(network.sgen['p_mw'],[33,66])
    n_coal,n_gas,n_nuke = 0,0,0

    #print(network.gen)

    for source in ["nuke", "gas", "coal"]:
        p_mw = (sum(
                network.gen[network.gen.name.str.startswith(source)]["p_mw"]
            )
            )
        #print(source, ":", p_mw)

    return network
            

def append_costs(network, gas_cost, coal_cost):
    nuke_cost = NUKE_COST

    for i in network.gen.index:
        n_bus = network.gen.loc[i,'bus']
        
        if  network.gen.loc[i,'name'][0] == 'c':
            cost = coal_cost
        elif network.gen.loc[i,'name'][0] == 'g':
            cost = gas_cost
        elif network.gen.loc[i,'name'][0] == 'n':
            cost = nuke_cost

        network.poly_cost = network.poly_cost.set_index('element')
        network.poly_cost.loc[i, 'cp0_eur'] = cost
        network.poly_cost = network.poly_cost.reset_index()

    return network  
        
        #pandapower.create_pwl_cost(network, n_bus, 'gen', [[network.gen.min_p_mw.at[i], network.gen.max_p_mw.at[i], cost]])
        #pandapower.create_poly_cost(network, n_bus, 'gen', cp1_eur_per_mw=0, cp0_eur=cost)
        

# pandapower.plotting.simple_plot(network)



def create_and_run_network(gas_cost, coal_cost):
    net = pn.case_illinois200()
    net.poly_cost['cp0_eur'] = net.poly_cost['cp0_eur']*0
    net.poly_cost['cp1_eur_per_mw'] = net.poly_cost['cp1_eur_per_mw']*0
    net.poly_cost['cp2_eur_per_mw2'] = net.poly_cost['cp2_eur_per_mw2']*0
    net = assign_gen_types(net)
    #simple_plotly(net, on_map=False)
    net = append_costs(net, gas_cost, coal_cost)
    net.gen['scaling'] = net.gen['scaling']*0.98
    net.load['scaling'] = net.load['scaling'] * 0.98

    overall_load_ask  = net.load['p_mw'].sum()
    overall_gen_power = net.gen['p_mw'].sum()
    overall_trafo_ask = net.trafo['sn_mva'].sum()
    
    pandapower.rundcopp(net)
    return net



def calculate_cost(gas_cost, coal_cost):
    # calculates the production cost / MWh

    def _calculate_cost(gas_cost, coal_cost):
        net = create_and_run_network(gas_cost, coal_cost)
        any_violation = isConstraintsViolation(net)
        return net.res_cost

    if type(gas_cost) == np.ndarray and type(coal_cost) == np.ndarray:
        return np.vectorize(_calculate_cost)(gas_cost, coal_cost)
    else:
        return _calculate_cost(gas_cost, coal_cost)
        

def get_consumer_price(gas_cost, coal_cost, demand = 1650, plot = False):
    def _get_consumer_price(gas_cost, coal_cost):
        network = create_and_run_network(gas_cost, coal_cost)

        dict_pmax = {'nuke': network.gen[network['gen']['name'].str[:4] == 'nuke']['p_mw'].sum(),
                    'gas': network.gen[network['gen']['name'].str[:3] == 'gas']['p_mw'].sum(),
                    'coal': network.gen[network['gen']['name'].str[:4] == 'coal']['p_mw'].sum() }

        dict_price = {'nuke': NUKE_COST, 'gas': gas_cost, 'coal': coal_cost}

        meritOrder = MeritOrder(dict_pmax, dict_price, demand = demand) #demand = network.load['p_mw'].sum()?
        source, price_per_mw =  meritOrder.compute_electricity_price()
        if plot:
            meritOrder.plot()
        return price_per_mw
    if type(gas_cost) == np.ndarray and type(coal_cost) == np.ndarray:
        return np.vectorize(_get_consumer_price)(gas_cost, coal_cost)
    else:
        return _get_consumer_price(gas_cost, coal_cost)
        

]


if __name__ == "__main__":
    gas_cost = np.array([x for x in range(20, 40, 5)])
    coal_cost = np.array([x for x in range(10, 40, 5)])
    
    X,Y = np.meshgrid(gas_cost, coal_cost)
    Z = get_consumer_price(X, Y)
    
    #consumer_prices = get_consumer_price(gas_cost, coal_cost)
