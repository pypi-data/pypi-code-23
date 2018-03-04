from os.path import dirname, join, realpath


directory_of_this_file = dirname(realpath(__file__))
directory_of_data = join(directory_of_this_file, "data")

def get_list_from_file(filepath):
    with open(filepath) as f:
        return f.read().strip().split("\n")

def get_country_codes():
    directory_of_country_codes = join(directory_of_data, "country_codes.txt")
    return sorted(get_list_from_file(directory_of_country_codes))

def get_geonames_feature_classes():
    directory_of_geonames_feature_classes = join(directory_of_data, "geonames_feature_classes.txt")
    return sorted(get_list_from_file(directory_of_geonames_feature_classes))

def get_geonames_feature_codes():
    directory_of_geonames_feature_codes = join(directory_of_data, "geonames_feature_codes.txt")
    return sorted(get_list_from_file(directory_of_geonames_feature_codes))

def get_timezones():
    directory_of_timezones = join(directory_of_data, "timezones.txt")
    return sorted(get_list_from_file(directory_of_timezones))


