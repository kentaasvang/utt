import io
import itertools
from datetime import date, timedelta
from typing import Dict, List

from pytz.tzinfo import DstTzInfo

from . import formatter
from ..data_structures.activity import Activity
from .common import (clip_activities_by_range, filter_activities_by_type,
                     print_dicts)


class ActivitiesModel:
    def __init__(self, activities: List[Activity], start_date: date,
                 end_date: date, local_timezone: DstTzInfo):
        activities = clip_activities_by_range(start_date, end_date, activities,
                                              local_timezone)
        self.names_work = _groupby_name(
            filter_activities_by_type(activities, Activity.Type.WORK))
        self.names_break = _groupby_name(
            filter_activities_by_type(activities, Activity.Type.BREAK))


class ActivitiesView:
    def __init__(self, model: ActivitiesModel):
        self._model = model

    def render(self, output: io.TextIOWrapper) -> None:
        print(file=output)
        print(formatter.title('Activities'), file=output)
        print(file=output)

        print_dicts(self._model.names_work, output)

        print(file=output)

        print_dicts(self._model.names_break, output)


def _groupby_name(activities: List[Activity]) -> List[Dict]:
    def key(act):
        return act.name.name

    result = []
    sorted_activities = sorted(activities, key=key)
    # pylint: disable=redefined-argument-from-local
    for _, activities in itertools.groupby(sorted_activities, key):
        activities = list(activities)
        project = activities[0].name.project
        result.append({
            'project':
            project,
            'duration':
            formatter.format_duration(
                sum((act.duration for act in activities), timedelta())),
            'name':
            ", ".join(sorted(set(act.name.task for act in activities)))
        })

    return sorted(
        result, key=lambda act: (act['project'].lower(), act['name'].lower()))
