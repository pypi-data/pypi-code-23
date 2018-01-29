import urllib.request
import time
from icalendar import Calendar

bin_event_list = []
unordered_date_list = []
ordered_date_list = []


def get_bin_data():
    req = urllib.request.Request('https://s3-eu-west-1.amazonaws.com/fs-downloads/GM/binfeed.ical')
    response = urllib.request.urlopen(req)
    data = response.read()
    return data


def sort_lists_of_bin_data(data):
    index = 0
    calendar_of_bin_collections = Calendar.from_ical(data)
    for event in calendar_of_bin_collections.walk('vevent'):
        date = event.decoded('dtstart')
        bin_event_list.append([event.decoded('summary')])
        ordered_date_list.append([date.strftime('%m/%d/%Y'), index])
        unordered_date_list.append(date.strftime('%m/%d/%Y'))
        index += 1
    ordered_date_list.sort()


def count_the_mode_date_occurrences(date_list):
    temp_count = 1
    max_occurrence = 1
    for i in range(len(date_list)-1):
        temp = date_list[i][0]
        if temp == date_list[i+1][0]:
            temp_count += 1
            if temp_count > max_occurrence:
                max_occurrence = temp_count
        else:
            temp_count = 1
    return max_occurrence


def find_all_occurrences_of_input_date(date_input, count):
    first_position_of_date_input = is_date_on_calendar(date_input)
    if first_position_of_date_input:
        positions_of_date_input_in_unordered_list = []
        for sublist in ordered_date_list:
            if sublist[1] == unordered_date_list.index(date_input):
                index_of_date_input_in_ordered_list = ordered_date_list.index(sublist)
                break
        positions_of_date_input_in_unordered_list.append(ordered_date_list[index_of_date_input_in_ordered_list][1])
        for i in range(1, count):
            if index_of_date_input_in_ordered_list + i < len(ordered_date_list):
                if ordered_date_list[index_of_date_input_in_ordered_list][0] == ordered_date_list[index_of_date_input_in_ordered_list+i][0]:
                    positions_of_date_input_in_unordered_list.append(ordered_date_list[index_of_date_input_in_ordered_list+1][1])
                else:
                    break
        return positions_of_date_input_in_unordered_list


def is_date_valid(date):
        try:
            if time.strptime(date, '%m/%d/%Y'):
                return True
        except ValueError:
            print('Invalid date form!  Please use the format mm/dd/YYYY')


def is_date_on_calendar(date):
    try:
        return unordered_date_list.index(date)
    except ValueError:
        print("No collection on this day")
        return False


def print_results(indexs):
    for index in indexs:
        print((bin_event_list[index][0].decode()), "on", unordered_date_list[index])


def menu():
    while True:
        user_choice = input("Enter date in format [mm/dd/YYYY] or 'q' to quit: ")
        if user_choice == 'q':
            quit()
        else:
            if is_date_valid(user_choice):
                return user_choice


def run_program():
    bin_data = get_bin_data()
    sort_lists_of_bin_data(bin_data)
    user_input = menu()
    count = count_the_mode_date_occurrences(ordered_date_list)
    indexs = find_all_occurrences_of_input_date(user_input, count)
    if indexs:
        print_results(indexs)

def run_program_test():
    bin_data = get_bin_data()
    sort_lists_of_bin_data(bin_data)

if __name__ == '__main__':
    run_program()
