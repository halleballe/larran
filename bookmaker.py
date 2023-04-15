from app import *
from datetime import datetime, timedelta, time
import pickle
import random

path_to_timeslots = "database/timeslots"
path_to_template = "database/timeslot_template"
path_to_max_bookings = "database/max_bookings"

class Timeslot:
    # takes datetime object as start time
    def __init__(self, start_time, duration=2):
        self.start_time = start_time  # int hr
        self.end_time = start_time + timedelta(hours=duration)
        self.duration = duration
        # can it be booked?
        self.rooms_left = 2

        # booker 1 and two are the room nr for the people having booked laundry room 1 and 2 respectively
        self.booker = [None, None]

    # function that tries to book the timeslot for room 1 or two for a booker
    def book(self, room, booker):
        room -= 1
        if not self.booker[room]:
            self.booker[room] = booker
            print(self.booker)
            # check if it is still bookable
            self.rooms_left -= 1
            update_timeslot(self)

            return f"succesfully booked room {room+1}"
        else:
            return "that room is already booked"

    def cancel(self, room, booker):
        room-=1
        if self.booker[room]==booker:
            self.booker[room]=None
            self.rooms_left+=1
            update_timeslot(self)
            return

    def __repr__(self):
        start_hour = self.start_time.strftime("%H")
        end_hour = self.end_time.strftime("%H")
        thing = f"{start_hour}-{end_hour}"
        thing2 = f"{start_hour}"
        return thing

def save_template(template):
    with open(path_to_template, "wb") as tf:
        pickle.dump(template, tf)


def get_template():
    try:
        with open(path_to_template, "rb") as tf:
            all_timeslots = pickle.load(tf)

        all_timeslots.sort(key=lambda x: x.start_time, reverse=False)
        return all_timeslots

    except:
        return []


# the template is a list of timeslots, made beforehand. it has start times and duration premade. the times that are
# blocked off are blocked off.
# but their dates are different. they have
def generate_generic_template(start_hour=8, duration=2, end_hour=22):
    template = []
    timeslots_per_day = (end_hour-start_hour)//duration
    # add one day to the timedelta(mon+0, tue+1 wed+2..)
    for day in range(0, 7):
        for slot in range(0, timeslots_per_day):
            hour = start_hour + duration * slot
            # the templates start time is irrelevant since it will never be used
            monday = get_next_monday(datetime.now())

            delta = timedelta(days=day, hours=hour)
            new_timeslot = Timeslot(monday + delta)
            new_timeslot.timedelta = delta
            template.append(new_timeslot)

    save_template(template)


# this function returns the date of next monday. It will be added to all timeslots in the template and then sent to the timeslots file
def get_next_monday(date):
    days_to_monday = (7 - date.weekday()) % 7
    next_monday = date + timedelta(days=days_to_monday)
    return datetime.combine(next_monday, time.min)


def generate_timeslots():
    timeslots = get_all_timeslots()
    if len(timeslots)>0:
        last_timeslot = timeslots[-1]
    else:
        last_timeslot = Timeslot(datetime.now())
    # get the next monday
    monday = get_next_monday(last_timeslot.start_time)

    # iterate through the template, change the start_times and end_times with monday + delta
    template = get_template()
    for timeslot in template:
        timeslot.start_time = monday + timeslot.timedelta
        timeslot.end_time = timeslot.start_time + timedelta(hours=timeslot.duration)

    timeslots += template

    save_timeslots(timeslots)

def get_max_bookings():
    with open(path_to_max_bookings, "r") as f:
        t = f.read()
        t = int(t)
        return t

def set_max_bookings(x):
    with open(path_to_max_bookings, "w") as f:
        f.write(str(x))

# function that reads timeslots file and returrn all timeslots in one bog list (chronological order)
def get_all_timeslots():

    try:
        with open(path_to_timeslots, "rb") as tf:
            all_timeslots = pickle.load(tf)
            all_timeslots.sort(key=lambda x: x.start_time, reverse=False)
        return all_timeslots

    except:
        return []




# function to update timeslots file
def update_timeslot(updated_timeslot):
    timeslots = get_all_timeslots()

    # check if user already exists
    for timeslot in timeslots:
        if timeslot.start_time == updated_timeslot.start_time:
            timeslots.remove(timeslot)
            print("found it.. updating")
    timeslots.append(updated_timeslot)

    with open(path_to_timeslots, "wb") as tf:
        pickle.dump(timeslots, tf)
        print("fully updated")


# function to delete a user
def delete_user(user_to_delete):
    timeslots = get_all_timeslots()

    # check if user already exists
    for timeslot in timeslots:
        if timeslot.start_time == user_to_delete.start_time:
            timeslots.remove(timeslot)

    with open(path_to_timeslots, "wb") as tf:
        pickle.dump(timeslots, tf)


def save_timeslots(all_timeslots):
    with open(path_to_timeslots, "wb") as tf:
        pickle.dump(all_timeslots, tf)

def delete_all_timeslots():
    with open(path_to_timeslots, "wb") as tf:
        pickle.dump([], tf)

def clear_up():
    all_timeslots=get_all_timeslots()
    # remove the old slots
    # this_week=datetime.today().isocalendar().week
    this_week = datetime.today().isocalendar().week
    new_slots = []
    for slot in all_timeslots:
        if slot.start_time.isocalendar().week >= this_week:
            new_slots.append(slot)
    print("så här många slots är det ", len(new_slots))
    # replace old slots with unbookable ones
    now = datetime.now()

    for slot in new_slots:
        if slot.end_time<now:
            slot.rooms_left = 0
            slot.booker = ["tidens gång", "tidens gång"]

    save_timeslots(new_slots)
