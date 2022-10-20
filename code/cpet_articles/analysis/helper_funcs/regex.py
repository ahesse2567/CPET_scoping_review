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

def non_OPRR_re(text):
    invited_review_re = re.compile(r'''(invited.{0,30}review)''', re.DOTALL | re.VERBOSE)
    # letter_to_editor_re = re.compile(r'''(invited.{0,30}review)''', re.DOTALL | re.VERBOSE)
    commentary_re = re.compile(r'''(commentary)''', re.DOTALL | re.VERBOSE)

    mo_list = [invited_review_re.search(text), commentary_re.search(text)]
    res = any(mo is not None for mo in mo_list)
    return res

def methods_res_disc(text):
    # checks to see if all four of the most comment original research paper sections exist
    # if all exist, then it's probably original research
    # intro_re = re.compile(r'introduction|background')
    methods_re = re.compile(r'm.{0,2}.{0,2}e.{0,2}t.{0,2}h.{0,2}o.{0,2}d', re.DOTALL)
    results_re = re.compile(r'r.{0,2}e.{0,2}s.{0,2}u.{0,2}l.{0,2}t.{0,2}s', re.DOTALL)
    discussion_re = re.compile(r'd.{0,2}i.{0,2}s.{0,2}c.{0,2}u.{0,2}s.{0,2}s.{0,2}i.{0,2}o.{0,2}n', re.DOTALL)

    mo_list = [
        methods_re.search(text),
        results_re.search(text),discussion_re.search(text)
    ]
    res = all(mo is not None for mo in mo_list)
    return res

def non_human(text):
    animal_re = re.compile(r'a.{0,2}n.{0,2}i.{0,2}m.{0,2}a.{0,2}l', re.DOTALL)
    mo_list = [animal_re.search(text)]
    res = any(mo is not None for mo in mo_list)
    return res

# for some reason, this does NOT work when you try to import it
def get_surrounding_text(phrase, text, chars=100):
    esc_phrase = re.escape(phrase) # prevent escape character issues

    surrounding_text_re = re.compile(
        fr'''(.{{0,{chars}}}{esc_phrase}.{{0,{chars}}})''',
        re.IGNORECASE | re.DOTALL)
    
    if surrounding_text_re.search(text):
        return surrounding_text_re.findall(text)