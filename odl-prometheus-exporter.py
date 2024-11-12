import requests
import json
from prometheus_client import start_http_server, Gauge
import time
import sys

# Define Prometheus metrics for OpenDaylight stats
PACKETS_SENT = Gauge(
    "opendaylight_packets_sent_total",
    "Total packets sent by each node connector",
    ["node_id", "port_number"],
)
PACKETS_RECEIVED = Gauge(
    "opendaylight_packets_received_total",
    "Total packets received by each node connector",
    ["node_id", "port_number"],
)
BYTES_SENT = Gauge(
    "opendaylight_bytes_sent_total",
    "Total bytes sent by each node connector",
    ["node_id", "port_number"],
)
BYTES_RECEIVED = Gauge(
    "opendaylight_bytes_received_total",
    "Total bytes received by each node connector",
    ["node_id", "port_number"],
)

def fetch_opendaylight_data(controller_ip, controller_port):
    """
    Fetch stats from an OpenDaylight controller and update Prometheus metrics.

    Args:
        controller_ip (str): The IP address of the OpenDaylight controller.
        controller_port (str): The port number of the OpenDaylight controller.
    """
    url = f"http://{controller_ip}:{controller_port}/restconf/operational/opendaylight-inventory:nodes"
    auth = ("admin", "admin")  # Default credentials for OpenDaylight

    try:
        # Make the request to the OpenDaylight REST API
        print(f"Fetching data from {url}...")
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an error for bad responses (4xx/5xx)

        # Parse the response JSON
        data = response.json()
        nodes = data.get("nodes", {}).get("node", [])

        if not nodes:
            print("No nodes found in the response.")
            return

        # Process each node in the response
        for node in nodes:
            node_id = node.get("id")
            if not node_id.startswith("openflow:"):
                # Only process OpenFlow-based nodes
                continue

            print(f"Processing stats for Node: {node_id}")

            # Process each connector in the node
            for connector in node.get("node-connector", []):
                port_number = connector.get("port-number") or connector.get("id") or connector.get("name")
                if not port_number:
                    print(f"Could not identify port for node {node_id}. Skipping.")
                    continue

                # Extract and update Prometheus metrics
                stats = connector.get("opendaylight-port-statistics:flow-capable-node-connector-statistics", {})
                packets_sent = int(stats.get("packets", {}).get("transmitted", 0))
                packets_received = int(stats.get("packets", {}).get("received", 0))
                bytes_sent = int(stats.get("bytes", {}).get("transmitted", 0))
                bytes_received = int(stats.get("bytes", {}).get("received", 0))

                PACKETS_SENT.labels(node_id=node_id, port_number=port_number).set(packets_sent)
                PACKETS_RECEIVED.labels(node_id=node_id, port_number=port_number).set(packets_received)
                BYTES_SENT.labels(node_id=node_id, port_number=port_number).set(bytes_sent)
                BYTES_RECEIVED.labels(node_id=node_id, port_number=port_number).set(bytes_received)

                if packets_sent == 0 and packets_received == 0:
                    print(f"No traffic on port {port_number} for node {node_id}.")

    except requests.RequestException as e:
        print(f"Error connecting to OpenDaylight: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure the user provides the required arguments
    if len(sys.argv) != 3:
        print("Usage: python3 script_name.py <controller_ip> <port>")
        sys.exit(1)

    controller_ip = sys.argv[1]
    controller_port = sys.argv[2]

    # Start the Prometheus HTTP server
    print(f"Starting Prometheus exporter on port 8000...")
    start_http_server(8000)

    print(f"Monitoring OpenDaylight at {controller_ip}:{controller_port}.")
    while True:
        fetch_opendaylight_data(controller_ip, controller_port)
        time.sleep(30)  # Update every 30 seconds
