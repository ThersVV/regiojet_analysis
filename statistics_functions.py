import numpy as np
import scipy.stats as st
import random

from data_definitions import *

def print_fare_buy_time_avgs(diffs: list, fares: list):
    avg_diffs = [[0, 0], [0, 0], [0, 0]]
    for i in range(0, len(diffs)):
        avg_diffs[fares[i]-1][0] += diffs[i]
        avg_diffs[fares[i]-1][1] += 1
    print(f"Průměrný čas před lowcost odjezdem: {round(avg_diffs[0][0]/avg_diffs[0][1])}")
    print(f"Průměrný čas před standard odjezdem: {round(avg_diffs[1][0]/avg_diffs[1][1])}")
    print(f"Průměrný čas před relax odjezdem: {round(avg_diffs[2][0]/avg_diffs[2][1])}")

def print_change_percentage(rides, fare: int = 0):
    changed = 0
    total = 0
    for ride in rides:
        if fare == 0 or ride[1] == fare:
            total += 1
            if ride[2]:
                changed += 1
    result = round(changed/total*100, 2)
    if fare == 0:    
        print(f"Podíl změněných jízdenek: {result}%")
    else:
        fare_s = ""
        if fare == 1:
            fare_s = "low cost"
        elif fare == 2:
            fare_s = "standard"
        elif fare == 3:
            fare_s = "relax"
        print(f"Podíl změněných jízdenek tarifu \"{fare_s}\": {result}%")
        

def standard_deviation(values: list):
    np_values = np.array(values)
    average_sqrd = np.mean(np_values) * np.mean(np_values)
    average_of_sqrd = np.mean(np_values * np_values)
    return np.sqrt(average_of_sqrd - average_sqrd)

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

def ticket_stats():
    lowcosts = 0
    standards = 0
    relaxs = 0
    c_lowcosts = 0
    c_standards = 0
    c_relaxs = 0
    for ride in rides:
        changed = ride[2]
        ride_type = ride[1]
        
        if ride_type == 1:
            lowcosts += 1
        elif ride_type == 2:
            standards += 1
        else:
            relaxs += 1

        if changed:
            if ride_type == 1:
                c_lowcosts += 1
            elif ride_type == 2:
                c_standards += 1
            else:
                c_relaxs += 1
    return (lowcosts, standards, relaxs, c_lowcosts, c_standards, c_relaxs)

def get_phacked_indices():
    min_p = 1
    min_i = -1
    min_j = -1
    for i in range(0, len(rides)):
        for j in range(i+130, len(rides)):
            fares = list(map(lambda r: r[1], rides))[i:j]
            changes = list(map(lambda r: 0 if r[2] else 1, rides))[i:j]

            result = st.spearmanr(fares, changes)
            if result.pvalue < min_p:
                min_p = result.pvalue
                min_i = i
                min_j = j

    print(f"p-hacked p-value: {min_p}")
    return (min_i, min_j)

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