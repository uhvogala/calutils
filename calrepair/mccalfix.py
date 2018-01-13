# -*- coding: utf-8 -*-
from icalendar import Calendar
import re

class McCalFixer(object):
    
    def __init__(self):
        self.cal = Calendar()
        
    def fix_calendar(self, ical):
        for event in ical.subcomponents:
            event = self._fix_address(event)
            event = self._fix_description(event)
            event = self._fix_categories(event)            
            event = self._fix_summary(event)
            
        return ical
    
    def _replace_event_data(self, sep, event, key, *args):
        event[key] = sep.join([x for x in args if x != ''])
        return event
    
    def _fix_summary(self, event):
        orig = event["summary"].split(",")
        course_name = self._get_course_name(orig)
        event_number = self._get_event_number(orig)
        course_code = self._get_course_code(orig)
        event = self._replace_event_data(', ', event, "summary",
                                 course_name, event_number,
                                  course_code)
        return event
    
    def _fix_description(self, event):
        summary = event["summary"].split(",")
        addit_descr = self._get_additional_description(summary)
        event_type = self._get_event_type(summary)
        room = self._get_class_room(summary)
        building = self._get_building(summary)
        event = self._replace_event_data(', ', event, "description",
                                 addit_descr, event_type,
                                 room, building)
        return event
    
    def _fix_categories(self, event):
        summary = event["summary"].split(",")
        course_code = self._get_course_code(summary)
        event_number = self._get_event_number(summary)
        event = self._replace_event_data(' ', event, "categories",
                                         course_code, event_number)
        return event
    
    def _fix_address(self, event):
        summary = event["summary"].split(",")
        room = self._get_class_room(summary)
        building = self._get_building(summary)
        address = self._get_address(summary)
        event = self._replace_event_data(", ", event, "location",
                                         room, building, address)
        return event
        
    
    def _search_from_list(self, pattern, lst):
        for item in lst:
            matched = re.search(pattern, item)
            if matched:
                return matched.group("word").strip()
        return ''
    
    def _get_course_code(self, summary):
        pattern = r'(?<=\()(?P<word>\S+?)(?=\s-)'
        return self._search_from_list(pattern, summary)
    
    def _get_event_type(self, summary):
        pattern = r'(?<=\s)(?P<word>\S+?/.+?/[^\(]+)'
        return self._search_from_list(pattern, summary)
    
    def _get_course_name(self, summary):
        pattern = r'(?<=\()(?:\S+\s-\s)(?P<word>[\s\w-]+)'
        return self._search_from_list(pattern, summary)

    def _get_event_number(self, summary):
        pattern = r'(?P<word>\S+)(\s)(\S+?/.+?/[^\(]+)'
        return self._search_from_list(pattern, summary)
    
    def _get_class_room(self, summary):
        pattern = r'(\s*)(?P<word>^[^\.]*$)'
        if len(summary) > 1:
            return self._search_from_list(pattern, [summary[1]])
        return ''
    
    def _get_building(self, summary):
        pattern = r'(?P<word>.+)'
        if len(summary) > 4:
            return self._search_from_list(pattern, [summary[2]])
        return ''
    
    def _get_address(self, summary):
        pattern = r'(?P<word>.+)(?=\()(\S+?)(?=\s-)'
        if len(summary) > 3:
            return self._search_from_list(pattern, [summary[-2]])
        return ''
    
    def _get_additional_description(self, summary):
        pattern = r'(?P<word>.+)(?=\()(\S+?)(?=\s-)'
        if len(summary) < 3:
            return self._search_from_list(pattern, summary)
        return ''
        
                