### FUNCTION DEFINITIONS ###

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import datetime
import pandas as pd
import numpy as np
import scipy.stats as st
import random

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
def grouped_by_month(l: list):
    #returns dict of month -> [changed tickets, tickets total]
    fractions = {}

    for ride in l:
        month = (ride[0].year-2022)*12 + ride[0].month
        if not month in fractions:
            fractions[month] = [0, 0]

        fractions[month][1] += 1

        if ride[2]:
            fractions[month][0] += 1
    return fractions

def get_random_specimen(fraction: float):
    bool_array = [random.random() < fraction for _ in range(0, len(rides))]
    fares_specimen = []
    changes_specimen = []
    for i in range(0, len(rides)):
        if bool_array[i]:
            fares_specimen.append(rides[i][1])
            changes_specimen.append(rides[i][2])
    return (fares_specimen, changes_specimen)

def proportion_by_month(l: list, starting_month: int = 0):
    fractions = grouped_by_month(l)
    result = [0]
    for month in (range(starting_month, max(fractions.keys()))):
        if not month in fractions:
            result.append(result[-1])
            continue
        fraction = fractions[month]
        result.append(fraction[0]/fraction[1])
    return result

def get_data(filename: str, result: list):
    rides_dev = {}
    read_file(filename, rides_dev)

    for key in rides_dev.keys():
        rides_dev[key] = sorted(rides_dev[key])

    split_canceled_tickets(rides_dev)

    format_onto_list(rides_dev, result)

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

def format_onto_list(storage: dict, result: list):
    for (key, value) in storage.items():
        if value[-1].event_kind == "Cancel" and key[0] - value[-1].event_time > 2*24*60*60:
            continue

        train_time = key[0]

        is_changed = any(v.event_kind == "Change" for v in value)
        if not value[0].event_kind.startswith("Bought"):
            # this can happen if someone buys a ticket, cancels it and then 
            # buys a ticket from somewhere else, but in the same train and 
            # changes happen. A very rare case... Cant be solved easily though, 
            # because in the "change" email the time specified is from the 
            # "true beginning" station, not from the beginning from the user
            # perspective... 
            continue
        fare = int(value[0].event_kind.split()[1])
        if fare == 0:
            #sometimes they forget to specify it... only like once or twice
            continue

        result.append((datetime.datetime.fromtimestamp(train_time), fare, is_changed))
        
def month_range(date1, date2):
    date_range = pd.date_range(date1, date2)
    date_range = date_range[date_range.day==1]
    return date_range

def standard_deviation(values: list):
    np_values = np.array(values)
    average_sqrd = np.mean(np_values) * np.mean(np_values)
    average_of_sqrd = np.mean(np_values * np_values)
    return np.sqrt(average_of_sqrd - average_sqrd)

def print_change_percentage(fare: int = 0):
    changed = 0
    total = 0
    for ride in rides:
        if fare == 0 or ride[1] == fare:
            total += 1
            if ride[2]:
                changed += 1
    result = round(changed/total*100, 2)
    if fare == 0:    
        print(f"Percentage of changed tickets: {result}%")
    else:
        fare_s = ""
        if fare == 1:
            fare_s = "low cost"
        elif fare == 2:
            fare_s = "standard"
        elif fare == 3:
            fare_s = "relax"
        print(f"Percentage of changed tickets for fare \"{fare_s}\": {result}%")


rides = []
get_data("stats_V2.txt", rides)
get_data("stats_V3.txt", rides)
rides = list(dict.fromkeys(rides)) # remove duplicates
red_patch = mpatches.Patch(color='red', label='Changed tickets')
green_patch = mpatches.Patch(color='green', label='Unchanged tickets')