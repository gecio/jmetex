#!/usr/local/bin/python3

import sys
import time
from prometheus_client import start_http_server, Metric, REGISTRY, Summary
from requests import Session

class OpticalCollector(object):

    REQUEST_TIME = Summary('request_processing_seconds_optical', 'Time spent gathering junos optical data')

    def __init__(self, instance, rpc_url, user, password):
        self.instance = instance
        self.rpc_url = rpc_url
        self.user = user
        self.password = password
        self.prefix = 'junos_'

    def start_connection(self):
        http_session = Session()
        return http_session

    def state_to_int(self, state):
        if state == "on":
            return 1
        if state == "off":
            return 0

    def parse_and_report_optical(self, phys_interface, metric):
        self.metric = metric
        ifname = phys_interface['name'][0]["data"]
        default_labels = {'instance': self.instance, 'interface': ifname}
        if_diag = phys_interface['optics-diagnostics'][0]
        for key in if_diag:
            if key.startswith('laser') or key.startswith('rx'):
                if key.endswith('warn') or key.endswith('alarm'):
                    if_diag[key][0]['data'] = self.state_to_int(if_diag[key][0]['data'])
                try:
                    metric.add_sample(self.prefix+key.replace('-', '_'),
                                      value=float(if_diag[key][0]['data']),
                                      labels=default_labels)
                except:
                    pass
            if key.startswith('module'):
                if 'attributes' in if_diag[key][0].keys():
                    value = if_diag[key][0]['attributes']['junos:celsius']
                    metric.add_sample(self.prefix+key.replace('-', '_'),
                                      value=float(value),
                                      labels=default_labels)
                else:
                    if key.endswith('warn') or key.endswith('alarm'):
                        if_diag[key][0]['data'] = self.state_to_int(if_diag[key][0]['data'])
                    metric.add_sample(self.prefix+key.replace('-', '_'),
                                      value=float(if_diag[key][0]['data']),
                                      labels=default_labels)

    def iterate_interfaces(self, interface_json, metric):
        self.metric = metric
        json = interface_json["interface-information"][0]["physical-interface"]
        for phys_interface in json:
            self.parse_and_report_optical(phys_interface, metric)

    @REQUEST_TIME.time()
    def handle_if_statistics(self, http_session, metric):
        uri = self.rpc_url+"get-interface-optics-diagnostics-information"
        headers = {'Accept': 'application/json'}
        result = http_session.get(uri, auth=(self.user, self.password), headers=headers)
        interface_json = result.json()
        self.iterate_interfaces(interface_json, metric)

    def collect(self):
        metric = Metric('optical_interface_values', 'optical_interface_values', 'gauge')
        http_session = self.start_connection()
        self.handle_if_statistics(http_session, metric)
        yield metric
