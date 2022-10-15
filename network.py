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
COAL_COST = 50


# nuke = 55%
# coal = 30%
# gas = 15%


def assign_gen_types(network):
        
    t1,t2 = np.percentile(network.gen['p_mw'],[40,90])
    print(t1, t2)
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

    print(network.gen)

    for source in ["nuke", "gas", "coal"]:
        p_mw = (sum(
                network.gen[network.gen.name.str.startswith(source)]["p_mw"]
            )
            )
        print(source, ":", p_mw)

    return network
            

def append_costs(network, gas_cost):
    coal_cost = COAL_COST
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

def calculate_cost(gas_cost):
    net = pn.case_illinois200()
    net.poly_cost['cp0_eur'] = net.poly_cost['cp0_eur']*0
    net.poly_cost['cp1_eur_per_mw'] = net.poly_cost['cp1_eur_per_mw']*0
    net.poly_cost['cp2_eur_per_mw2'] = net.poly_cost['cp2_eur_per_mw2']*0
    net = assign_gen_types(net)
    #simple_plotly(net, on_map=False)
    net = append_costs(net, gas_cost)
    net.gen['scaling'] = net.gen['scaling']*0.98
    net.load['scaling'] = net.load['scaling'] * 0.98

    overall_load_ask  = net.load['p_mw'].sum()
    overall_gen_power = net.gen['p_mw'].sum()
    overall_trafo_ask = net.trafo['sn_mva'].sum()
      
    print('========================================================')
    print('overall_load_ask = {}'.format(overall_load_ask))
    print('overall_gen_power = {}'.format(overall_gen_power))
    print('overall_trafo_ask = {}'.format(overall_trafo_ask))

    pandapower.rundcopp(net)
    pf_res_plotly(net)
    
    any_violation = isConstraintsViolation(net)
    overall_load_power = sum(net.res_load['p_mw'])
    overall_load_mvar  = sum(net.res_load['q_mvar'])

    overall_trafo_load = (net.res_trafo['loading_percent']/100*net.trafo['sn_mva']).sum()

    # sum(net.res_trafo['p_hv_mw']) + sum(net.res_load['p_mw'])
    # = (net.res_trafo['loading_percent']/100*net.trafo['sn_mva']).sum() - sum(net.res_load['p_mw'])

    dict_pmax = {'nuke': net.gen[net['gen']['name'].str[:4] == 'nuke']['p_mw'].sum(),
                 'gas': net.gen[net['gen']['name'].str[:3] == 'gas']['p_mw'].sum(),
                 'coal': net.gen[net['gen']['name'].str[:4] == 'coal']['p_mw'].sum()                
                }
    dict_price = {'nuke': NUKE_COST, 'gas': gas_cost, 'coal': COAL_COST}

    meritOrder = MeritOrder(dict_pmax, dict_price, demand = 1500)
    meritOrder.compute_electricity_price()
    #meritOrder.plot()
    
    
    print('overall_load_power_after_run: {}'.format(overall_load_power))
    print('overall_load_mvar_after_run: {}'.format(overall_load_mvar))
    print('overall_trafo_load_after_run: {}'.format(overall_trafo_load))
    
    print('============================')

    net.res_cost
    return net.res_cost, any_violation

if __name__ == "__main__":
    gas_cost = [x for x in range(20, 70, 5)]
    price,Vs = list(),list()

    for g in gas_cost:
        cost, v = calculate_cost(g)
        price.append(cost)
        Vs.append(v)

    plt.scatter(gas_cost, price, c=['red' if v else 'blue' for v in Vs])
    plt.show()
<<<<<<< Updated upstream
    # gas_cost = 18.5
    # price = calculate_cost(gas_cost)
    # print(price)
    
=======
    
>>>>>>> Stashed changes
