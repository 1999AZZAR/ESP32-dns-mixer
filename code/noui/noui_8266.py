import network
import socket
import machine
import time

# Constants
WIFI_SSID = "bayar"
WIFI_PASSWORD = "drowssap"
STATIC_IP = "192.168.8.180"
DNS_PROVIDERS_IPV4 = ["9.9.9.9", "1.1.1.1", "8.8.8.8", "94.140.14.14", "76.76.19.19", "76.76.2.0", "185.228.168.9",
                     "208.67.222.222", "80.80.80.80"]

# Pin configuration
LED_PIN = machine.Pin(2, machine.Pin.OUT)

# Function to connect to WiFi
def connect_to_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.ifconfig((STATIC_IP, "255.255.255.0", "192.168.8.1", "8.8.8.8"))
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    while not sta_if.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)

    print("Connected to WiFi")

# Function to handle DNS requests
def handle_dns_request(data, addr):
    print("Received DNS request from:", addr)

    # Blink LED for 0.05 seconds on new request
    LED_PIN.off()
    time.sleep(0.05)
    LED_PIN.on()

    success = False

    # Iterate through each DNS provider and try to resolve using the first one that responds
    for dns_provider in DNS_PROVIDERS_IPV4:
        print("Trying DNS provider:", dns_provider)

        # Create a UDP socket to forward the DNS request
        dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_socket.settimeout(0.03)

        try:
            dns_socket.sendto(data, (dns_provider, 53))
            response, _ = dns_socket.recvfrom(1024)
            # Forward the DNS response to the original requester
            server_socket.sendto(response, addr)
            # Blink LED for 0.07 second on success
            LED_PIN.off()
            time.sleep(0.07)
            LED_PIN.on()
            success = True
            break
        except:
            print("Failed to resolve using DNS provider:", dns_provider)
        finally:
            dns_socket.close()

    if not success:
        # Blink LED for half second on failure
        LED_PIN.off()
        time.sleep(0.5)
        LED_PIN.on()
        print("Failed to forward DNS request")

    return success

# Main script

# Connect to WiFi
connect_to_wifi()

# Create a UDP socket for DNS
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("0.0.0.0", 53))

# Main loop to handle DNS requests
while True:
    data, addr = server_socket.recvfrom(1024)
    handle_dns_request(data, addr)

    # Sleep for a short duration to handle requests
    time.sleep(0.05)
