
import datetime
import pandas as pd
import matplotlib.patches as mpatches

class Ticket:
    train_time: int
    thing: int

    def __init__(self, train_time: int, thing: int = 0):
        self.train_time = train_time
        self.thing = thing

    def __eq__(self, other):
        if isinstance(other, Ticket):
            return self.train_time == other.train_time and self.thing == other.thing
        return False

    def __hash__(self):
        return hash(self.train_time, self.thing)
    
class Event:
    event_time: int
    event_kind: str

    def __init__(self, event_time: int, event_kind: str):
        self.event_time = event_time
        self.event_kind = event_kind

    def __lt__(self, other):
        if isinstance(other, Event):
        
            if self.event_time != other.event_time:
                return self.event_time < other.event_time
            
            return self.event_kind < other.event_kind
        return NotImplemented

def get_data(filename: str, result: list, filtered=False):
    rides_dev = {}
    read_file(filename, rides_dev)

    for key in rides_dev.keys():
        rides_dev[key] = sorted(rides_dev[key])

    split_canceled_tickets(rides_dev)

    format_onto_list(rides_dev, result, filtered)

def split_canceled_tickets(storage: dict):
    storage_cpy = list(storage.items())
    for (key, value) in storage_cpy:
        thing_counter = 1
        event_i = 0
        last_event_i = -1
        for v in value:
            if v.event_kind == "Cancel" and event_i != len(value) -1:
                new_key = (key[0], thing_counter)
                storage[new_key] = list(value[last_event_i+1:event_i+1])
                storage[key] = list(value[event_i+1:])
                thing_counter += 1
                last_event_i = event_i
            event_i += 1

def read_file(filename: str, storage: dict):
    with open(filename, 'rt') as file:
            tickets_done = False
            changes_done = False
            i = 1
            lines = file.readlines()
            while i < len(lines):
                line = lines[i]
                if line.startswith("##") and not tickets_done:
                    tickets_done = True
                    i += 1
                elif line.startswith("##") and not changes_done:
                    changes_done = True
                    i += 1
                else:
                    ticket = (int(lines[i+1]), 0)
                    if not tickets_done:
                        if ticket not in storage:
                            storage[ticket] = []

                        storage[ticket].append(Event(int(line), "Bought-Fare " + lines[i+2]))

                        i += 3
                    elif not changes_done:
                        storage[ticket].append(Event(int(line), "Change"))

                        i += 2
                    else:
                        storage[ticket].append(Event(int(line), "Cancel"))

                        i += 2

def format_onto_list(storage: dict, result: list, filtered: bool):
    for (key, value) in storage.items():
        train_time = key[0]

        is_changed = any(v.event_kind == "Change" for v in value)
        if not value[0].event_kind.startswith("Bought"):
            # this can happen if someone buys a ticket, cancels it and then 
            # buys a ticket from somewhere else, but in the same train, and 
            # changes happen. A very rare case... Cant be solved easily though, 
            # because in the "change" email the time specified is from the 
            # "true beginning" station, not from the beginning from the user
            # perspective... 
            continue
        fare = int(value[0].event_kind.split()[1])
        if fare == 0:
            #sometimes they forget to specify it... only like once or twice... idk...
            continue
        if filtered:        
            cancelled_soon = value[-1].event_kind == "Cancel" and key[0] - value[-1].event_time > 30*60*60
            bought_shortly = key[0] - value[0].event_time < 10 or (value[-1].event_kind == "Cancel" and key[0] - value[-1].event_time < 10)
            if cancelled_soon or bought_shortly:
                continue
            result.append((datetime.datetime.fromtimestamp(train_time), fare, is_changed))
        else:         
            change_times = [datetime.datetime.fromtimestamp(e.event_time) for e in list(filter(lambda v: v.event_kind == "Change", value))]
            bought_diff = (train_time - value[0].event_time) / 60.0
            result.append((datetime.datetime.fromtimestamp(train_time), fare, is_changed, change_times, bought_diff))
        
def month_range(date1, date2):
    date_range = pd.date_range(date1, date2)
    date_range = date_range[date_range.day==1]
    return date_range

def split_changes(rides: list):
    result = []
    for ride in rides:
        for change in ride[3]:
            result.append((ride[1], (ride[0] - change).total_seconds() / 60.0))
    return result

def get_unfiltered_rides():
    rides = []
    get_data("stats_V2.txt", rides)
    get_data("stats_V3.txt", rides)
    all_changes = split_changes(rides)
    rides = [(entry[0], entry[1], entry[2], entry[4]) for entry in rides]
    bought_diffs = [ride[3] for ride in rides]
    return (rides, all_changes, bought_diffs)

def get_filtered_rides():
    rides = []
    get_data("stats_V2.txt", rides, True)
    get_data("stats_V3.txt", rides, True)
    rides = list(dict.fromkeys(rides)) # remove duplicates
    return rides

unfiltered_rides, all_changes, bought_diffs = get_unfiltered_rides()
rides = get_filtered_rides()

red_patch = mpatches.Patch(color='red', label='Changed tickets', alpha=0.5)
green_patch = mpatches.Patch(color='green', label='Unchanged tickets', alpha=0.5)