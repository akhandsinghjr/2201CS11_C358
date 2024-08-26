from scapy.all import *
import sys

def ping(destination, count=4, packet_size=64, ttl=64, timeout=2):
    # Validate and prepare the destination IP
    try:
        ip = IP(dst=destination, ttl=ttl)
    except Exception as e:
        print(f"Error: Could not resolve destination IP '{destination}'. Please check the address and try again.")
        return
    
    # Basic input validation for count, packet size, and TTL
    if not isinstance(count, int) or count <= 0:
        print("Error: 'count' should be a positive integer.")
        return
    if not isinstance(packet_size, int) or packet_size <= 0:
        print("Error: 'packet_size' should be a positive integer.")
        return
    if not isinstance(ttl, int) or ttl <= 0:
        print("Error: 'ttl' should be a positive integer.")
        return

    # Loop to send the specified number of ping requests
    for i in range(count):
        # Build the ICMP packet with the desired payload size
        packet = ip / ICMP() / (b'Q' * packet_size)
        try:
            # Send the packet and wait for a reply (timeout set by user)
            reply = sr1(packet, timeout=timeout, verbose=0)
            if reply:
                # Calculate and display round-trip time (in milliseconds)
                rtt = (reply.time - packet.sent_time) * 1000
                print(f"Reply from {reply.src}: bytes={packet_size} time={rtt:.2f}ms TTL={reply.ttl}")
            else:
                print("Request timed out.")
        except Exception as e:
            # Handle any exceptions that occur during packet send/receive
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    # Ensure at least the destination is provided
    if len(sys.argv) < 2:
        print("Usage: python ping.py <destination> [count] [packet_size] [ttl] [timeout]")
    else:
        # Parse command-line arguments
        destination = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        packet_size = int(sys.argv[3]) if len(sys.argv) > 3 else 64
        ttl = int(sys.argv[4]) if len(sys.argv) > 4 else 64
        timeout = int(sys.argv[5]) if len(sys.argv) > 5 else 2
        
        # Run the ping function with provided arguments
        ping(destination, count, packet_size, ttl, timeout)
