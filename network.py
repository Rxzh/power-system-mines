import pandas as pd
import matplotlib.pyplot as plt
import pandapower
import pandapower.networks as pn
import pandapower.topology
import pandapower.plotting
import pandapower.converter
import pandapower.estimation
import pandapower.test
import numpy as np


def assign_gen_types(network):
        
    t1,t2 = np.percentile(network.gen['p_mw'],[33,66])
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

    for i in network.sgen.index:
        if network.sgen.loc[i,'p_mw'] <= t1:
            network.sgen.loc[i,'name'] = 'coal_{}'.format(n_coal)
            n_coal += 1
        elif t1 < network.sgen.loc[i,'p_mw'] <= t2:
            network.sgen.loc[i,'name'] = 'gas_{}'.format(n_gas)
            n_gas += 1
        else:
            network.sgen.loc[i,'name'] = 'nuke_{}'.format(n_nuke)
            n_nuke += 1

    return network
            

def append_costs(network):
    coal_cost = 30
    gas_cost  = 18.5
    nuke_cost = 0
    
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
        

# network = pn.case_illinois200()
# assign_gen_types(network)
# append_costs(network)
# print(network.gen)
# pandapower.plotting.simple_plot(network)
# pandapower.rundcopp(network)

if __name__ == "__main__":
    net = pn.case_illinois200()
    #pandapower.rundcopp(net)
    net.poly_cost['cp0_eur'] = net.poly_cost['cp0_eur']*0
    net = assign_gen_types(net)
    net = append_costs(net)
    net.poly_cost['cp1_eur_per_mw'] = net.poly_cost['cp1_eur_per_mw']*0
    net.poly_cost['cp2_eur_per_mw2'] = net.poly_cost['cp2_eur_per_mw2']*0
    print(net.poly_cost)
    net.gen['scaling'] = net.gen['scaling']*0.98
    net.load['scaling'] = net.load['scaling'] * 0.98
    pandapower.rundcopp(net)
    print(net.res_cost)
    
