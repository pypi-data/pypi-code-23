import pickle
from athletelist import AthleteList
#import athletelist

def get_coach_data(filename):
    try:
        with open(filename) as f:
            data = f.readline()
        temp=data.strip().split(',')
        return(AthleteList(temp.pop(0),temp.pop(0),temp))
    except IOError as ioerr:
        print("File Error (get_coach_data): " + str(ioerr))
        return(None)
def put_to_store(file_list):
    all_athletes = {}
    for each_file in file_list:
        ath=get_coach_data(each_file)
        all_athletes[ath.name]=ath
    try:
        with open('athletes.pickle','wb') as athf:
            pickle.dump(all_athletes,athf)
    except IOError as ioerr:
        print("File error (put_to_store): " +str(ioerr))
    return(all_athletes)
def get_from_store():
    all_athletes={}
    try:
        with open('athletes.pickle','rb') as athf:
            all_athletes=pickle.load(athf)
    except IOError as ioerr:
        print("File error (get_from_store): " + str(ioerr))
    return(all_athletes)





