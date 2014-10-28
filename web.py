# -*- coding: utf-8 -*-
'''
Copyright (c) Oct 29, 2012, Juan Morales <juanmoralesdelolmo@gmail.com>
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

import webapp2
import jinja2
import os
from collections import namedtuple
import datagen as dg
import StringIO
import json


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render())

class Download(webapp2.RequestHandler):
    def get(self):
        patterns = self.request.get('numberOfRecords', '')
        n_nodes = self.request.get('numberOfNodes', '')
        n_events = self.request.get('numberOfEvents', '')
        n_years = self.request.get('numberOfYears', '')
        stddev = self.request.get('stddev', 0.0)
        copies = self.request.get('copies', 1)
        events = json.loads(self.request.get('events'))

        patterns = int(patterns) if patterns.isdigit() else None
        n_nodes = int(n_nodes) if n_nodes.isdigit() else None
        n_events = int(n_events) if n_events.isdigit() else None
        n_years = int(n_years) if n_years.isdigit() else None
        stddev = float(stddev) if stddev.isdigit() else None
        copies = int(copies) if copies.isdigit() else None
        events = self._prepare_events(events)

        Args = namedtuple('DataGenArgs', 'num_of_patterns num_of_events num_of_nodes num_of_years only_points stddev copies events')
        args = Args(num_of_patterns=patterns, num_of_events=n_events, num_of_nodes=n_nodes,
                    num_of_years=n_years, only_points=False, stddev=stddev, copies=copies,
                    events=events)


        result = StringIO.StringIO()
        dg.run(args, result)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(result.getvalue())

    def _prepare_events(self, events):
        for event in events:
            event_class = event['class']
            if event_class == 'Milestone':
                event['class'] = dg.Milestone
            elif event_class == 'Interval':
                event['class'] = dg.Interval
            else:
                raise Exception('Unespected class %s' %event_class)
        return events

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/download', Download)],
                              debug=True)
