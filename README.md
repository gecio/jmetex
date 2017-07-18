JunOS Metering Exporter
=======================

JMetEx is a tool to export data from JunOS Devices to Prometheus

About
-----
Later JunOS versions have the ability to expose control and statistics functions via an REST-API.
This data is usually more useful and less painful to access in comparison to using SNMP.
This tool is meant to expose this data towards an prometheus server, instead of trying to get
data out of snmp and using the snmp_exporter. Especially as some data is not avail via snmp.

Requirements
------------
The Junos API has to be enabled, see (https://www.juniper.net/documentation/en_US/junos/information-products/pathway-pages/rest-api/rest-api.html) for this.
A system user is required to access the API, read-only user class is sufficient.

Usage
-----
Start the jmetex2.py with following command line options:
- instance name
- rpc endpoint (e.g. http://my.router.tld:3000/rpc/)
- username
- password

For each router you want to instrument you need the script running on a unique port,
as per now multiple routers in the same instance are not planned and implemented.

Security
--------
jmetex itself has no implemented security of any kind, you should not expose this to the internet,
and I highly recommend setting some kind of proxy (eg nginx) in front and using the latest TLS version.