# -*- coding: utf-8 -*-
'''
Created on Oct 29, 2012

@author: crispamares
'''

import cgi
import webapp2
import jinja2
import os
from collections import namedtuple
import datagen as dg
import StringIO


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render())

    def post(self):
        
        patterns = int(self.request.get('numberOfRecords', 10))
        nodes = int(self.request.get('numberOfNodes', 10))
        events = int(self.request.get('numberOfEvents', 10))
        
        Args = namedtuple('DataGenArgs', 'num_of_patterns num_of_events num_of_nodes num_of_years only_points stddev copies')
        args = Args(num_of_patterns=patterns, num_of_events=None, num_of_nodes=nodes, 
                    num_of_years=2, only_points=False, stddev=0.0, copies=1)

        
        result = StringIO.StringIO()
        dg.run(args, result)

        if self.request.get('preview') and not self.request.get('download'):
            self.preview(result)
        if self.request.get('download') and not self.request.get('preview'):
            self.download(result)

    def preview(self, result):
        template_values = {
            'result': result.getvalue().replace('\n', '<br>'),
            'number_of_records': self.request.get('numberOfRecords'), 
            'number_of_nodes': self.request.get('numberOfNodes'), 
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

    def download(self, result):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(result.getvalue())



app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)