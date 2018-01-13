# -*- coding: utf-8 -*-
from icalendar import Calendar, Event, vDDDTypes, cal
from mccalfix import McCalFixer
from dateutil import parser
import datetime
import os
import json


week = datetime.timedelta(days=7)
zero = datetime.timedelta(minutes=0)

class CalEditor(object):
    
    def __init__(self):
        self.cal = Calendar()
        self.fixer = McCalFixer()
        self.cal_str = None
        
    def load_calendar(self, filename):
        with open(filename, 'r') as icalfile:
            self.cal_str = self.cal.from_ical(icalfile.read())
            
    def export_json(self, filename):
        json_str = self.export_json_str(self.cal)
        self._write_file(filename, json_str)
        
            
    def export_json_str(self, cal):
        events = []
        for event in cal.subcomponents:
            json_event = {}
            for key in event:
                if isinstance(event[key], vDDDTypes):
                    json_event[key] = event[key].dt.isoformat()
                else:
                    json_event[key] = event[key]
            events.append(json_event)
        json_events = json.dumps(events, ensure_ascii=False)
        return json_events
    
    def json_to_ical(self, json_events):
        self.cal = Calendar()
        events_list = json.loads(json_events, object_hook=self._datetime_parser)
        print(events_list)
        for event_dict in events_list:
            event = Event()
            for key in event_dict:
                event.add(key, event_dict[key])
            self.cal.add_component(event)
        return self.cal
            
            
    def export_calendar(self, filename):
        self.cal.add("prodid", "-//Fixed MyCourses ical export//")
        self.cal.add("version", "2.0")
        self.print_cal(self.cal)
        self._write_file(filename, self.cal.to_ical())
        
    def fix_calendar(self):
        if self.cal_str:
            self.cal_str = self.fixer.fix_calendar(self.cal_str)
        self.cal = self.cal_str
            
    def print_cal(self, cal):
        print(str(cal.to_ical()).replace('\\r\\n', '\n').strip())
        
    def merge_recurring_events(self):
        self.cal = Calendar()
        grouped = self._group_events(self.cal_str.subcomponents)
        for group in grouped:
            group.sort(key=lambda event: event.decoded("dtstart"))
            t = [event.decoded("dtstart") for event in group]
            days_between = [j-i for i, j in zip(t[:-1], t[1:])]
            self._add_recurrence(days_between, group)
            for event in group:
                if "rrule" in event:
                    self.cal.add_component(event)
                    
    def _write_file(self, filename, str):
        directory = 'export'
        if not os.path.exists(directory):
            os.makedirs(directory)
        f = open(os.path.join(directory, filename), 'wb')
        f.write(str)
        f.close()
                
    def _group_events(self, events):
        sim_list = []
        for event in events:
            sim_list = self._append_event(event, sim_list)
        return sim_list
    '''
                if self._same_categ(event1, event2):
                    start1 = event1.decoded("dtstart").replace(tzinfo=None)
                    start2 = event2.decoded("dtstart").replace(tzinfo=None)
                    print(start1 - start2)
                    print((start1 - start2) == datetime.timedelta(days=7))
    '''
                
    def _append_event(self, event, lst):
        for events in lst:
            for pre_event in events:
                if (event["description"] == pre_event["description"] and
                     event["categories"] == pre_event["categories"] and
                     abs(event.decoded("dtstart") - pre_event.decoded("dtstart")) % week == zero):
                    events.append(event)
                    return lst
        lst.append([event])
        return lst
    
    def _add_recurrence(self, days_between, events):
        event_num = 0
        occur = 1
        for days in days_between:
            if days == week:
                occur += 1
            elif days > week:
                events[event_num].add("rrule", {"FREQ": "WEEKLY", "COUNT": occur})
                event_num = occur
                occur = 1
        events[event_num].add("rrule", {"FREQ": "WEEKLY", "COUNT": occur})
        
    def _datetime_parser(self, json_dict):
        for (key, value) in json_dict.items():
            try:
                json_dict[key] = parser.parse(value)
            except:
                pass
        return json_dict
    
    
editor = CalEditor()
editor.load_calendar("icalexport.ics")
editor.fix_calendar()
editor.merge_recurring_events()
editor.export_json("jsontest.json")
#json_events = editor.export_json_str(editor.cal)
#cal = editor.json_to_ical(json_events)
#editor.export_calendar("testcal.ics")
