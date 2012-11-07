#!/usr/bin/env python
'''
Created on May 28, 2012

@author: crispamares
'''

import datetime as dt
import sys
import random
import argparse

STDDEV = 0.0


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + dt.timedelta(seconds=random_second))


class Milestone(object):
    ''' This event is represented by 1 node in EventFlow '''
    nodes_count = 1  
    def __init__(self, date):
        self.date = date
    def __str__(self):
        return '%s' % (self.date.strftime('%m/%d/%Y'))
    def shift(self, new_date):
        self.date = new_date
    @classmethod
    def is_interval(cls):
        return False
    @property
    def start(self):
        return self.date
    @property
    def end(self):
        return self.date
    
    
class Interval(object):
    ''' This event is represented by 2 nodes in EventFlow '''
    nodes_count = 2 
    def __init__(self, start, end):
        self.start = start
        self.end = end 
    def __str__(self):
        return '%s\t%s' % (self.start.strftime('%m/%d/%Y'),
                             self.end.strftime('%m/%d/%Y'))
    @classmethod
    def is_interval(cls):
        return True
    def shift(self, new_date):
        duration = self.end - self.start
        self.start = new_date
        self.end = self.start + duration

class Record(object):
    def __init__(self, id):
        self.id = id
        self.events = {}
        self.total_nodes = 0
    
    def add(self, event_type, event):
        ''' @param event: is Milestone or Interval '''
        event_dates = self.events.get(event_type, [])
        event_dates.append(event)
        self.events[event_type] = event_dates
        self.total_nodes += event.nodes_count
    
    def __str__(self):
        msg = ''
        for event_type in self.events:
            event_dates = self.events[event_type]
            for event in event_dates:
                msg += '%s\t%s\t%s\n' %(self.id, event_type, event)
        return msg[:-1]


class DataGenerator(object):    

    def __init__(self, records_count, avg_events_count, nodes_count, years, only_points, events=None):
        self.records_count = records_count
        self.avg_events_count = avg_events_count
        self.nodes_count = nodes_count
        self.years = years
        self.only_points = only_points
        
        if events is None:
            self.events = []
            self.events.append({'type':'Stroke', 'class':Milestone})
            self.events.append({'type':'Admitted', 'class':Milestone})
            self.events.append({'type':'Diagnosed', 'class':Milestone})
            self.events.append({'type':'Drug A', 'class':Milestone if self.only_points else Interval})
            self.events.append({'type':'Drug B', 'class':Milestone if self.only_points else Interval})
        else:
            self.events = events
        
        self.events_bag = self._create_events_distribution(self.events)
        
            
    def random_delta(self):
        items = self.avg_events_count if self.avg_events_count else self.nodes_count
        delta_inter_events = dt.timedelta(days=self.years*365) / items
        seconds = delta_inter_events.total_seconds()
        return dt.timedelta(seconds=random.gauss(seconds, STDDEV*seconds))
    
    def _create_events_distribution(self, events):
        events_bag = []
        for event in events:
            prop = event.get('prop', None)
            if prop is None:
                return events
            else:
                events_bag += [event] * prop
        return events_bag
    
    def next_event(self):
        return random.choice(self.events_bag)

    def run(self, keepit=False):
        records = []  # Used if keepit == True

        for nid in range(self.records_count):
            record = Record(nid)    
            date = dt.datetime.today()

            if self.avg_events_count == None and self.nodes_count:
                self._run_for_nodes(record, date)
            elif self.nodes_count == None and self.avg_events_count:
                self._run_for_events(record, date)
            else:
                raise(Exception('Bad number of events %s or nodes %s'% (self.avg_events_count, self.nodes_count)))
            
            if keepit: 
                records.append(record)
            else:
                print record
                
        return records


    def _run_for_nodes(self, record, date, exit_count_threshold=500):
        '''
        Fill the record with a certain number of nodes
        @param record: the record to fill
        @param date: the date of the last node
        @param exit_count_threshold: the algorithm will look at most this number of times for a new event  
        '''
        nodes_count = self.nodes_count#random.gauss(self.nodes_count, STDDEV*self.nodes_count)

        while(record.total_nodes < nodes_count):
            event_def = self.next_event()
            exit_count = 0
            while (nodes_count - record.total_nodes - event_def['class'].nodes_count < 0):
                event_def = self.next_event()
                exit_count += 1
                if exit_count >= exit_count_threshold: return
            exit_count = 0
            
            date = date - self.random_delta()

            if event_def['class'].is_interval():
                event = event_def['class'](date - self.random_delta(), date)
            else:
                event = event_def['class'](date)
            
            record.add(event_def['type'], event)


    def _run_for_events(self, record, pos):
        events_count = self.avg_events_count#random.gauss(self.avg_events_count, STDDEV*self.avg_events_count)

        for _e in range(events_count):
            event_def = self.next_event()
                    
            date = pos - self.random_delta()
            pos = date

            if event_def['class'].is_interval():
                event = event_def['class'](date - self.random_delta(), date)
            else:
                event = event_def['class'](date)
                
            record.add(event_def['type'], event)

def run(args, fd=sys.stdout):
    STDDEV = args.stddev

    dg = DataGenerator(records_count=args.num_of_patterns,
                       avg_events_count=args.num_of_events,
                       nodes_count=args.num_of_nodes,
                       years=args.num_of_years,
                       only_points=args.only_points,
                       events=args.events)
    
    if args.copies:
        records = dg.run(True)
        for nid in xrange(args.num_of_patterns * args.copies):
            record = records[nid % args.num_of_patterns]
            record.id = nid
            print >> fd, record
    else:
        records = dg.run(True)
        for record in records:
            print >> fd, record

    
if __name__ == '__main__':
    #TODO: Interface needed for the events definition
    parser = argparse.ArgumentParser(description='Generate EventFlow datasets.')
    parser.add_argument('num_of_patterns', metavar='R', type=int, default=100,
                        help='the number of records in the dataset')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--num_of_events', dest='num_of_events', type=int,
                        help='Average of events per record in the dataset')
    group.add_argument('-n', '--num_of_nodes', dest='num_of_nodes', type=int,
                        help='Average of nodes per record in the dataset')

    parser.add_argument('--years', dest='num_of_years', type=int, default=2, 
                        help='the total of years of records')
    parser.add_argument('--stddev', dest='stddev', type=float, default=0.0,
                        help='Standard deviation of all randomness')
    parser.add_argument('--repeat', dest='copies', type=int, default=0,
                        help='The numbers of copies of generated records')
    parser.add_argument('--only_points', dest='only_points', action='store_true', default=False,
                        help='Generate dataset with only point events')
    
    in_args = parser.parse_args()
    args = {'events': None}
    args.update(args)

    run(args)

    