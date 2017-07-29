#!/usr/local/bin/python3

import sys
import time
from prometheus_client import start_http_server, Metric, REGISTRY, Summary
from requests import Session
import pprint

class InterfaceCollector(object):

    REQUEST_TIME = Summary('request_processing_seconds', 'Time spent gathering junos interface data')

    def __init__(self, instance, rpc_url, user, password):
        self.instance = instance
        self.rpc_url = rpc_url
        self.user = user
        self.password = password
        self.prefix='junos_'

    def start_connection(self):
        http_session = Session()
        return http_session

    def state_to_int(self, state):
        if state == "up":
            return 1
        if state == "down":
            return 0

        return -1

    def iterate_interfaces(self, interface_json, metric):
        json = interface_json["interface-information"][0]["physical-interface"]
        for phys_interface in json:
            self.parse_and_report_ifstat(phys_interface, metric)
            if 'logical-interface' in phys_interface.keys():
                for log_if in phys_interface['logical-interface']:
                    self.parse_and_report_ifstat(log_if, metric)

    def parse_and_report_ifstat(self, junos_interface, metric):
        self.metric = metric
        ifname = junos_interface['name'][0]["data"]
        default_labels = {'instance': self.instance, 'interface': ifname}

        if 'input-error-list' in junos_interface.keys():
            for input_error in junos_interface['input-error-list']:
                for key in input_error.keys():
                    metric.add_sample(self.prefix+key.replace('-', '_'),
                                      value=int(input_error[key][0]['data']),
                                      labels=default_labels)

        if 'output-error-list' in junos_interface.keys():
            for output_error in junos_interface['output-error-list']:
                for key in output_error.keys():
                    metric.add_sample(self.prefix+key.replace('-', '_'),
                                      value=int(output_error[key][0]['data']),
                                      labels=default_labels)

        if 'traffic-statistics' in junos_interface.keys():
            for trafstat in junos_interface['traffic-statistics']:
                for key in trafstat.keys():
                    if key == 'attributes':
                        pass
                    elif key == 'ipv6-transit-statistics':
                        for v6_transit in trafstat['ipv6-transit-statistics']:
                            for v6key in v6_transit:
                                metric.add_sample(self.prefix+'ipv6_'+v6key.replace('-', '_'),
                                                  value=int(trafstat[v6key][0]['data']),
                                                  labels=default_labels)
                    else:
                        metric.add_sample(self.prefix+key.replace('-', '_'),
                                          value=int(trafstat[key][0]['data']),
                                          labels=default_labels)

        if 'admin-status' in junos_interface.keys():
            admin_status = self.state_to_int(junos_interface['admin-status'][0]['data'])
            metric.add_sample(self.prefix+'admin_status', value=admin_status, labels=default_labels)

        if 'oper-status' in junos_interface.keys():
            oper_status = self.state_to_int(junos_interface['oper-status'][0]['data'])
            metric.add_sample(self.prefix+'oper_status',
                              value=oper_status, labels=default_labels)

    @REQUEST_TIME.time()
    def handle_if_statistics(self, http_session, metric):
        uri = self.rpc_url+"get-interface-information?extensive="
        headers = {'Accept': 'application/json'}
        result = http_session.get(uri, auth=(self.user, self.password), headers=headers)
        interface_json = result.json()
        self.iterate_interfaces(interface_json, metric)

    def collect(self):
        metric = Metric('interface_counters', 'Interface Counters', 'counter')
        http_session = self.start_connection()
        self.handle_if_statistics(http_session, metric)
        yield metric

