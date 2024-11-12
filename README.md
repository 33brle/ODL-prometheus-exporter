# ODL-Prometheus-exporter
ODL exporter job for Prometheus <br> 
Environment - Ubuntu 64-bit 22.04 <br>
ODL version - 2.0.0 <br>
Mininet - 2.3.1b4 <br> 

## Installing Mininet 
- git clone https://github.com/mininet/mininet.git
- cd  mininet/util
- ./install.sh -a

## Mininet Topology Scripts 
To run the mininet scripts use the following:
- sudo python3 /path/to/chosen_topology.py [controller-ip] [controller-port] [num-hosts]

## Using ODL-Prometheus-exporter 
Run Prometheus and make sure to edit prometheus.yml to fit the requirements. <br>
You can use Grafana to view the exported data. <br>
To run the exporter: 
- sudo python3 /path/to/odl-prometheus-exporter.py <br>
<br>
Prometheus should be on port 9090 out of box <br>
Metrics pulled will be on port 8000 <br>
To view if the exporter is functioning and scrape time is adequate check the Status/Targets tab to ensure job is up. <br> 
For this exporter, bytes sent and bytes received metrics are collected from OpenDaylight's REST API response, specifically from the opendaylight-port-statistics:flow-capable-node-connector-statistics object under each node-connector. <br>


