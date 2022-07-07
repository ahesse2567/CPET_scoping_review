import re

def oxygen_uptake_re(text):
    o2_uptake_re = re.compile(r'oxygen.*{0,5}uptake')
    
    mo_list = [o2_uptake_re.search(text)]
    
    mentions_o2_uptake = any(mo is not None for mo in mo_list)
    
    return mentions_o2_uptake

def gas_collection_methods_re(text):
    bbb_re = re.compile(r'breath.{0,5}breath', re.DOTALL)
    douglas_bag_re = re.compile(r'douglas.{0,5}bag', re.DOTALL)
    
    mo_list = [bbb_re.search(text), douglas_bag_re.search(text)]
    
    gas_methods = any(mo is not None for mo in mo_list)
    
    return gas_methods

def vo2_units_re(text):
    mL_kg_min_re = re.compile(r'ml[^a-zA-Z]*kg[^a-zA-Z]*min')
    mL_min_kg_re = re.compile(r'ml[^a-zA-Z]*min[^a-zA-Z]*kg')
    
    # L_mL_min = re.compile(r'(m)?l[^a-zA-Z]*min')

    mo_list = [mL_kg_min_re.search(text), mL_min_kg_re.search(text)]
    
    vo2_units = any(mo is not None for mo in mo_list)
    
    return vo2_units