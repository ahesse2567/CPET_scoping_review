import re

# these functions require the article text as one long string
def oxygen_uptake_re(text):
    o2_uptake_consupmtion_re = re.compile(r'oxygen.{0,5}(uptake|consumption)', re.DOTALL)
    vo2max_peak_re = re.compile(r'(v)?o2.{0,2}(max|peak)?', re.DOTALL)
    aerobic_re = re.compile(r'(?<!an)aerobic.{0,2}(power|capacity)', re.DOTALL)
    
    mo_list = [
        o2_uptake_consupmtion_re.search(text),
        vo2max_peak_re.search(text),
        aerobic_re.search(text)]
    
    mentions_o2_uptake = any(mo is not None for mo in mo_list)
    
    return mentions_o2_uptake

def gas_collection_methods_re(text):
    bbb_re = re.compile(r'breath.{0,5}breath', re.DOTALL)
    douglas_bag_re = re.compile(r'douglas.{0,5}bag', re.DOTALL)
    mixing_chamber_re = re.compile(r'mixing.{0,5}chamber', re.DOTALL)
    
    mo_list = [bbb_re.search(text), douglas_bag_re.search(text), mixing_chamber_re.search(text)]
    
    gas_methods = any(mo is not None for mo in mo_list)
    
    return gas_methods

def vo2_units_re(text):
    vo2_rel_re = re.compile(r'ml([^a-zA-Z]*kg[^a-zA-Z]*min|[^a-zA-Z]*min[^a-zA-Z]*kg)')
    # mL_min_kg_re = re.compile(r'ml[^a-zA-Z]*min[^a-zA-Z]*kg')
    
    # L_mL_min = re.compile(r'(m)?l[^a-zA-Z]*min')

    mo_list = [vo2_rel_re.search(text)]
    
    vo2_units = any(mo is not None for mo in mo_list)
    
    return vo2_units

# this finds articles that estimated VO2 by using proxy tests, but also finds articles that made people exercise 
# at esetimated percentages of VO2. It needs refining
def estimated_vo2_re(text):
    est_o2_uptake_re = re.compile(r'''(
    (estimat|indirect|calculat).{0,30}oxygen.{0,2}(uptake|consumption)|
    oxygen.{0,2}(uptake|consumption).{0,30}(estimat|indirect|calculat)
    )''',
                                           re.DOTALL | re.VERBOSE)
    
    est_vo2_re = re.compile(r'''(
    (estimat|indirect|calculat).{0,30}(v)?o2.{0,2}(max|peak)|
    (v)?o2.{0,2}(max|peak).{0,30}(estimat|indirect|calculat)
    )''',
                            re.DOTALL | re.VERBOSE)
    
    est_vo2_units_re = re.compile(r'''(
    (estimat|indirect|calculat).{0,30}ml([^a-zA-Z]*kg[^a-zA-Z]*min|[^a-zA-Z]*min[^a-zA-Z]*kg)|
    ml([^a-zA-Z]*kg[^a-zA-Z]*min|[^a-zA-Z]*min[^a-zA-Z]*kg).{0,30}(estimat|indirect|calculat)
    )''',
                            re.DOTALL | re.VERBOSE)
    
    mo_list = [est_o2_uptake_re.search(text), est_vo2_re.search(text), est_vo2_units_re.search(text)]
    est_vo2 = any(mo is not None for mo in mo_list)
    
    return est_vo2
    # assessment of aerobic capacity