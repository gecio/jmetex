import sys
import time
import argparse
from prometheus_client import start_http_server, Metric, REGISTRY, Summary
from .interfacecollector import InterfaceCollector
from .opticalcollector import OpticalCollector

def main():

    parser = argparse.ArgumentParser(description='JunOS API to Prometheus exporter')
    parser.add_argument('--port', type=int, required=True,
                        help='listen port')
    parser.add_argument('--instance', type=str, required=True,
                        help='instance name')
    parser.add_argument('--rpc_url', type=str, required=True,
                        help='URL of the junos RPC endpoint')
    parser.add_argument('--user', type=str, required=True,
                        help='junos user name')
    parser.add_argument('--password', type=str, required=True,
                        help='junos password')
    args = parser.parse_args()
    start_http_server(args.port)

    REGISTRY.register(InterfaceCollector(args.instance, args.rpc_url, args.user, args.password))
    REGISTRY.register(OpticalCollector(args.instance, args.rpc_url, args.user, args.password))

    while True:
        time.sleep(1)
