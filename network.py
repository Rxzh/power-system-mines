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
    coal_cost = 30
    nuke_cost = 5
    
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
    net = append_costs(net, gas_cost)
    net.gen['scaling'] = net.gen['scaling']*0.98
    net.load['scaling'] = net.load['scaling'] * 0.98
    pandapower.rundcopp(net)
    return net.res_cost

if __name__ == "__main__":
    gas_cost = [x for x in range(20, 70, 5)]
    price = [calculate_cost(g) for g in gas_cost]
    plt.scatter(gas_cost, price)
    plt.show()
    # gas_cost = 18.5
    # price = calculate_cost(gas_cost)
    # print(price)
    
