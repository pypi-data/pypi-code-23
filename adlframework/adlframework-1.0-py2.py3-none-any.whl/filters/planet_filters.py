######################
####   FILTERS  ######
######################
def check_planethood(planetfilede, is_it_planet):
    label = planetfilede.get_labels()
    is_planet = is_planet = label['label'].tolist()[0].strip().lower() == 'c'
    if is_it_planet:
        return is_planet
    else:
        return not is_planet

def is_planet(planetfilede):
    return check_planethood(planetfilede, True)

def is_other(planetfilede):
    return check_planethood(planetfilede, False)