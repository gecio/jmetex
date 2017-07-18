#!/usr/local/bin/python3

import sys
import time
from prometheus_client import start_http_server, Metric, REGISTRY, Summary
from requests import Session


class InterfaceCollector(object):

    REQUEST_TIME = Summary('request_processing_seconds', 'Time spent gathering junos data')

    def __init__(self):
        pass

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
        default_labels = {'instance': instance, 'interface': ifname}

        print("Name: %s" % (ifname))
        if 'input-error-list' in junos_interface.keys():
            for input_error in junos_interface['input-error-list']:
                for key in input_error.keys():
                    metric.add_sample(key.replace('-', '_'),
                                      value=int(input_error[key][0]['data']),
                                      labels=default_labels)
                    print(key+": "+input_error[key][0]['data'])
        if 'output-error-list' in junos_interface.keys():
            for output_error in junos_interface['output-error-list']:
                for key in output_error.keys():
                    metric.add_sample(key.replace('-', '_'),
                                      value=int(output_error[key][0]['data']),
                                      labels=default_labels)
                    print(key+": "+output_error[key][0]['data'])
        if 'traffic-statistics' in junos_interface.keys():
            for trafstat in junos_interface['traffic-statistics']:
                for key in trafstat.keys():
                    if key == 'attributes':
                        pass
                    else:
                        metric.add_sample(key.replace('-', '_'),
                                          value=int(trafstat[key][0]['data']),
                                          labels=default_labels)
                        print(key+": "+trafstat[key][0]['data'])
        if 'admin-status' in junos_interface.keys():
            admin_status = self.state_to_int(junos_interface['admin-status'][0]['data'])
            metric.add_sample('admin_status', value=admin_status, labels=default_labels)
            print('Admin State: '+str(admin_status))

        if 'oper-status' in junos_interface.keys():
            oper_status = self.state_to_int(junos_interface['oper-status'][0]['data'])
            metric.add_sample('oper_status',
                              value=oper_status, labels=default_labels)
            print('Admin State: '+str(oper_status))

    @REQUEST_TIME.time()
    def handle_if_statistics(self, http_session, metric):
        uri = rpc_url+"get-interface-information?extensive="
        headers = {'Accept': 'application/json'}
        result = http_session.get(uri, auth=(user, password), headers=headers)
        interface_json = result.json()
        self.iterate_interfaces(interface_json, metric)

    def collect(self):
        metric = Metric('interface_counters', 'Interface Counters', 'counter')
        http_session = self.start_connection()
        self.handle_if_statistics(http_session, metric)
        yield metric

if __name__ == '__main__':
    start_http_server(int(sys.argv[1]))
    instance = sys.argv[2]
    rpc_url = sys.argv[3]
    user = sys.argv[4]
    password = sys.argv[5]
    REGISTRY.register(InterfaceCollector())

    while True:
        time.sleep(1)
