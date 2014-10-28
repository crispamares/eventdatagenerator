#!/usr/bin/env python
'''
Copyright (c) May 28, 2012, Juan Morales <juanmoralesdelolmo@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of copyright holders nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
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
        ''' Changes the date of the event '''
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
        ''' Changes the staring date of the event '''
        duration = self.end - self.start
        self.start = new_date
        self.end = self.start + duration


class Record(object):
    '''A Record represent a related serie of events'''
    def __init__(self, id):
        self.id = id
        self.events = {}  # {event_type : [events]}
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

    def __init__(self, records_count, events_count, nodes_count, years, only_points, events=None):
        '''
        Keyword Arguments:
        @param int records_count:  -- The number of records to include in the dataset
        @param int events_count:   -- The number of events per record
        @param int nodes_count:    -- The number of nodes per record (exlusive with events_count)
        @param int years:          -- The time span as numer of years where the events are distributed
        @param bool only_points:   -- All events are considered Milestones
        @param dict events:        -- The menu of events to choose from
        '''
        self.records_count = records_count
        self.events_count = events_count
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
        """
        Returns a timedelta based on the number of nodes/events requested and the given time span
        """
        items = self.events_count if self.events_count else self.nodes_count
        delta_inter_events = dt.timedelta(days=self.years * 365) / items
        seconds = delta_inter_events.total_seconds()
        return dt.timedelta(seconds=random.gauss(seconds, STDDEV * seconds))

    def _create_events_distribution(self, events):
        """
        Ceates a bag of event definitions. This is a list that includes all
        the definitions in the described proportion.
        """
        events_bag = []
        for event in events:
            prop = event.get('prop', None)
            if prop is None:
                return events
            else:
                events_bag += [event] * prop
        return events_bag

    def next_event(self):
        """
        Uniform random selection of events definitions. Extracts a "ball"
        from the "bag"
        """
        return random.choice(self.events_bag)

    def run(self, keepit=False):
        """
        Execute the generation of the requested records.

        @param bool keepit: If false the records are printed to the
        stdout otherwise records are returned in a list.
        """
        records = []  # Used if keepit == True

        for nid in range(self.records_count):
            record = Record(nid)
            date = dt.datetime.today()

            if self.events_count == None and self.nodes_count:
                self._run_for_nodes(record, date)
            elif self.nodes_count == None and self.events_count:
                self._run_for_events(record, date)
            else:
                raise(Exception('You need to specify number of events (%s) OR number of nodes (%s)'% (self.events_count, self.nodes_count)))

            if keepit:
                records.append(record)
            else:
                print record

        return records


    def _run_for_nodes(self, record, date, exit_count_threshold=500):
        '''
        Fill the record with a certain number of nodes.

        @param record: the record to fill
        @param date: the date of the last node
        @param exit_count_threshold: the retrial number of times the algorithm will look for a new event that fits the constraints.
        '''
        nodes_count = self.nodes_count

        # Use the next line insetad if you whant some randomness in the number of nodes per record
        #
        # nodes_count = random.gauss(self.nodes_count, STDDEV*self.nodes_count)

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


    def _run_for_events(self, record, date):
        '''
        Fill the record with a certain number of events.

        @param record: the record to fill
        @param date: the date of the last node
        '''
        events_count = self.events_count

        # Use the next line insetad if you whant some randomness in the number of events per record
        #
        # events_count = random.gauss(self.events_count, STDDEV*self.events_count)

        for _e in range(events_count):
            event_def = self.next_event()

            date = date - self.random_delta()

            if event_def['class'].is_interval():
                event = event_def['class'](date - self.random_delta(), date)
            else:
                event = event_def['class'](date)

            record.add(event_def['type'], event)


def run(args, fd=sys.stdout):
    """
    This function is a wrapper of DataGenerator.run method. Configures
    the DataGenerator and also makes the requested copies of the
    generated records if necessary.

    @param args: A namespace object. Expects an object like the one
    returned by the ArgumentParser.
    @param fd: The file descriptor where records are printed.
    """
    global STDDEV
    STDDEV = args.stddev

    dg = DataGenerator(records_count=args.num_of_patterns,
                       events_count=args.num_of_events,
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
                       help='Desired number of events per record in the dataset')
    group.add_argument('-n', '--num_of_nodes', dest='num_of_nodes', type=int,
                       help='Desired number of nodes per record in the dataset')

    parser.add_argument('--years', dest='num_of_years', type=int, default=2,
                        help='the total of years of records')
    parser.add_argument('--stddev', dest='stddev', type=float, default=0.0,
                        help='Standard deviation affects random elections such as time shifts')
    parser.add_argument('--repeat', dest='copies', type=int, default=0,
                        help='The numbers of copies of generated records to ensure aggregation in EventFlow')
    parser.add_argument('--only_points', dest='only_points', action='store_true', default=False,
                        help='Generate dataset with only point events (A.K.A. Milestones)')

    args = parser.parse_args()

    args.events = None

    run(args)
