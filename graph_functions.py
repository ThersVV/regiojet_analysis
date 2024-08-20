from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as mlines

from data_definitions import *
from statistics_functions import *

def changes_bargraph():
    x = [1, 2, 3]

    _f, ax = plt.subplots(figsize=(5.5, 2))
    ax.legend(handles=[red_patch, green_patch])

    plt.xlabel("Fare")
    plt.ylabel("Ticket count")
    plt.xticks([1, 2, 3], ["Low cost", "Standard", "Relax"])
    plt.xlim(0.5, 4.5)
    plt.bar(x, ticket_stats()[:3], color="green", alpha=0.5)
    plt.bar(x, ticket_stats()[3:], color="white")
    plt.bar(x, ticket_stats()[3:], color="red", alpha=0.5)

    plt.show()

def regio_through_time():
    x = [entry[0] for entry in rides]
    y = [entry[1] for entry in rides]
    color = ["red" if entry[2] else "green" for entry in rides]

    _fig, ax = plt.subplots(figsize=(10, 3))
    ax.legend(handles=[red_patch, green_patch])

    plt.xlabel("Date")
    plt.ylabel("Fare")
    plt.yticks([1, 2, 3], ["Low cost", "Standard", "Relax"])
    plt.ylim(0.5, 4.5)
    plt.scatter(x, y, s=105, c=color, alpha=0.4)

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))  # Monthly intervals
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))  # Format as Year-Month-Day
    plt.gcf().autofmt_xdate()

    _x = plt.xlim(left=datetime.datetime(2022, 6, 1))
    plt.show()

def regio_trend():
    starting_month = 9

    change_proportions = list(map(lambda x: x * 100, proportion_by_month(rides, starting_month)))

    x = range(0, len(change_proportions))
    p = np.polyfit(x,change_proportions,5)
    poly_y_5 = np.poly1d(p)(x)
    p = np.polyfit(x,change_proportions,1)
    poly_y_1 = np.poly1d(p)(x)

    m_range = month_range(datetime.datetime(2022, starting_month, 1), datetime.datetime(2024, 8, 11)).date

    plt.plot(m_range, change_proportions, color='#e5e5e5')
    plt.plot(m_range, poly_y_1, color='#df20df')
    plt.plot(m_range, poly_y_5, color='#dfdf00')

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    plt.gcf().autofmt_xdate()

    plt.xlabel('Date')
    plt.ylabel('Proportion of changes in %')
    plt.gca().legend(( 'Data', 'Trend', 'Approximation'))
    plt.show()

    print("Směrodatná odchylka: " + str(round(standard_deviation(change_proportions), 2)) + "%")

def fare_buy_time():
    x = bought_diffs
    y = [ride[1] for ride in unfiltered_rides]
    yellow = '#dfdf00'
    pink = '#df20df'
    pink_line = mlines.Line2D([], [], color=pink, label='1800 minutes')

    _fig, ax = plt.subplots(figsize=(10, 3))
    ax.legend(handles=[pink_line, mpatches.Patch(color=yellow, label='Ticket bought', alpha=0.5)])

    plt.xlabel("Minutes before planned departure")
    plt.ylabel("Ticket fare")
    plt.yticks([1, 2, 3], ["Low cost", "Standard", "Relax"])
    plt.ylim(0.5, 4.5)
    plt.scatter(x, y, s=155, c=yellow, alpha=0.4, marker="v")
    ax.set_xscale("log")
    plt.axvline(x = 30*60, color=pink, label = '1800 minutes before departure')
    plt.show()
    print_fare_buy_time_avgs(x, y)

def changes_time(cut=False, log=False):
    x = [change[1] for change in all_changes]
    y = [change[0] for change in all_changes]
    color = "red"

    _fig, ax = plt.subplots(figsize=(10, 3))
    ax.legend(handles=[mpatches.Patch(color=color, label='Emails informing of a change', alpha=0.5)])

    plt.xlabel("Minutes before planned departure")
    plt.ylabel("Ticket fare")
    plt.yticks([1, 2, 3], ["Low cost", "Standard", "Relax"])
    plt.ylim(0.5, 4.5)
    plt.scatter(x, y, s=155, c=color, alpha=0.4, marker="v")
    if log:
        ax.set_xscale("log")
    if cut:
        plt.xlim(-100,1800)
    plt.show()

def shady_graph():
    x = [1, 2, 3]

    fig, ax = plt.subplots(figsize=(5.5, 3))
    ax.legend(handles=[red_patch, green_patch])

    plt.xlabel("Fare")
    plt.ylabel("Ticket count")
    plt.xticks([1, 2, 3], ["Low cost", "Standard", "Relax"])
    plt.xlim(0.5, 4.5)
    plt.bar(x, ticket_stats()[:3], color="green", alpha=0.5)
    plt.bar(x, ticket_stats()[3:], color="white")
    plt.bar(x, ticket_stats()[3:], color="red", alpha=0.5)
    ax.set_yscale("log")

    plt.show()