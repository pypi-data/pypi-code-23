from __init__ import Overwatch

def main():
    overwatch = Overwatch(battletag="Okush#11324", hero="dva", filter="miscellaneous")
 

    stats = overwatch()

    print(stats)


main()