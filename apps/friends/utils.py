from datetime import time
import random
import string

from apps.timetables.models import TimeTable


def get_random_code(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def is_valid_code(code: str, length: int = 8) -> bool:
    return code.isalnum() and len(code) == length


"""
    get_hangout_intervals
        Given two sets of meetings, return the set of intervals where two people are both free

    inputs:
        - *meetings: each argument is expected to be a set of meeting tuples - (day of week, start time, end time) (set[tuple[str, time, time]])

    output:
        - list[tuple[str, time, time]] - a list of intervals where two people are both available
"""
def get_hangout_intervals(*meetings: set[tuple[str, time, time]]) -> list[tuple[str, time, time]]:
    # union all the meetings
    all_meetings = set()
    for meeting_set in meetings:
        all_meetings = all_meetings.union(meeting_set)

    # divide the meetings by day of week (Mon, Tue, ..., Fri)
    meetings_by_day = {
        "M": set(),
        "Tu": set(),
        "W": set(),
        "Th": set(),
        "F": set(),
    }
    for meeting in all_meetings:
        day = meeting[0]
        if day not in meetings_by_day:
            continue
        meetings_by_day[day].add(meeting)

    # add a bogus meeting for each day of week, that is 00:00 ~ 07:00, 22:00 ~ 24:00
    for day in meetings_by_day:
        meetings_by_day[day].add((day, time(0, 0), time(7, 0)))
        meetings_by_day[day].add((day, time(22, 0), time(23, 59)))
    
    coalesced_meetings_by_day: dict[str, list[tuple[str, time, time]]] = {}
    # coalesce overlapping meetings
    for day in meetings_by_day:
        coalesced_meetings_by_day[day] = coalesce_overlapping_intervals(meetings_by_day[day])

    hangout_by_day = {
        "M": [],
        "Tu": [],
        "W": [],
        "Th": [],
        "F": [],
    }

    for day in coalesced_meetings_by_day:
        meetings = coalesced_meetings_by_day[day]
        for i in range(len(meetings) - 1):
            hangout_interval = (day, meetings[i][2], meetings[i + 1][1]) # hangout can be done in between two meetings
            hangout_by_day[day].append(hangout_interval)
    
    # union the hangout intervals
    ret = []
    for day in hangout_by_day:
        ret += hangout_by_day[day]

    return ret

"""
    coalesce_overlapping_intervals
        Given a set of intervals of the same day, coalesce the overlapping intervals

    inputs:
        - intervals_of_day: set[tuple[str, time, time]] - a set of intervals of the same day

    output:
        - list[tuple[str, time, time]] - a list of coalesced intervals
"""
def coalesce_overlapping_intervals(intervals_of_day: set[tuple[str, time, time]]) -> list[tuple[str, time, time]]:
    # sort the intervals by start time
    intervals = sorted(intervals_of_day, key=lambda x: x[1])

    is_coalesced = False
    # coalesce the intervals
    coalesced_intervals = []
    for i in range(len(intervals) - 1):
        if is_coalesced:
            is_coalesced = False
            continue

        prev = intervals[i]
        next = intervals[i + 1]

        if prev[2] >= next[1]: # prev[2]: prev.end_time, next[1]: next.start_time
            # overlap
            coalesced_intervals.append((prev[0], prev[1], next[2])) # prev[0]: day, prev[1]: prev.start_time, next[2]: next.end_time
            is_coalesced = True
        else:
            coalesced_intervals.append(prev)
            is_coalesced = False
    
    if not is_coalesced:
        coalesced_intervals.append(intervals[-1])
    
    return coalesced_intervals

def get_hangout_intervals_of_users(semester: str, user_ids: list[int]) -> list[tuple[str, time, time]]:
    # get the timetables of the users
    timetables = TimeTable.objects.filter(user__in=user_ids, semester__code=semester, order=0)
    if timetables.count() != len(user_ids):
        raise ValueError("Some users do not have a timetable for the given semester")
    
    meetings = set()
    for timetable in timetables:
        meetings.update(
                timetable.opened_section_entries.values_list(
                    "opened_section__meeting__day__day",
                    "opened_section__meeting__duration__start_time",
                    "opened_section__meeting__duration__end_time",
                )
            )

    return get_hangout_intervals(meetings)