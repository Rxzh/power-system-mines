# check constraints violation - voltage
def isVoltageViolation(net):
    vMin = 0.9
    vMax = 1.1
    v = net.res_bus['vm_pu']
    alert = sum(v > vMax) + sum(v < vMin)
    return alert > 0

# check constraints violation - current
def isCurrentViolation(net):
    # https://pandapower.readthedocs.io/en/v2.1.0/elements/line.html#result-parameters
    i = net.res_line['i_ka']
    iMax = net.line['max_i_ka']
    alert = sum(i>iMax)
    return alert > 0


def isTransformerViolation(net):
    # check constraints violation - transformer
    # https://pandapower.readthedocs.io/en/v2.1.0/elements/trafo.html#result-parameters
    load = net.res_trafo['loading_percent']
    
    alert = sum(load>100)
    print('alert = ', alert)
    return alert > 0


def isConstraintsViolation(net):
    # check constraints violation - all
    # Args: net:pandapower network
    # Returns boolean True or False (False means no constraint violation)
    testV = isVoltageViolation(net)
    testC = isCurrentViolation(net)
    testT = isTransformerViolation(net)
    alert = sum([testV,testC,testT])
    return alert > 0