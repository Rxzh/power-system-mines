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
            



if __name__ == "__main__":
    network = pn.case_illinois200()
    assign_gen_types(network)
    print(network.gen)
    pandapower.plotting.simple_plot(network)

