from scapy.all import IP, ICMP, sr1
import time
import socket

def tracert(dest_ip, max_ttl=30, timeout=2, packet_size=64, pings_per_hop=1, delay_between_pings=0, file_output=None):
    # Error Handling
    try:
        socket.gethostbyname(dest_ip)  # Check if the IP/hostname is valid
    except socket.gaierror:
        print(f"Invalid destination IP: {dest_ip}")
        return

    if max_ttl <= 0:
        print("Invalid max TTL value. It must be a positive integer.")
        return

    if packet_size < 1:
        print("Invalid packet size. It must be greater than zero.")
        return

    if timeout < 0:
        print("Invalid timeout value. It must be a non-negative number.")
        return

    results = []

    for ttl in range(1, max_ttl + 1):
        successes = 0
        total_rtt = 0
        hop_ip = "*"
        
        for _ in range(pings_per_hop):
            packet = IP(dst=dest_ip, ttl=ttl) / ICMP() / ("X" * packet_size)
            start_time = time.time()
            reply = sr1(packet, verbose=0, timeout=timeout)
            rtt = (time.time() - start_time) * 1000  # in ms

            if reply:
                successes += 1
                total_rtt += rtt
                hop_ip = reply.src
            
            time.sleep(delay_between_pings)

        if successes > 0:
            avg_rtt = total_rtt / successes
            packet_loss = (1 - successes / pings_per_hop) * 100
            result = f"{ttl}   {hop_ip}   RTT: {avg_rtt:.2f} ms   Loss: {packet_loss:.1f}%"
        else:
            result = f"{ttl}   *   Request timed out"

        results.append(result)
        print(result)

        if hop_ip != "*" and reply and reply.type == 0:  # ICMP Echo Reply
            break

    # Save to file if file_output is specified
    if file_output:
        with open(file_output, 'w') as f:
            for line in results:
                f.write(line + '\n')

# Function to take user inputs
def take_user_input():
    dest_ip = input("Enter destination IP or domain (e.g., google.com): ")
    
    try:
        max_ttl = int(input("Enter max TTL (default is 30): ") or 30)
        timeout = float(input("Enter timeout in seconds (default is 2): ") or 2)
        packet_size = int(input("Enter packet size (default is 64 bytes): ") or 64)
        pings_per_hop = int(input("Enter number of pings per hop (default is 1): ") or 1)
        delay_between_pings = float(input("Enter delay between pings (default is 0 seconds): ") or 0)
        file_output = input("Enter output file name (leave empty to print to console): ") or None
    except ValueError:
        print("Invalid input, please enter appropriate values.")
        return None
    
    return dest_ip, max_ttl, timeout, packet_size, pings_per_hop, delay_between_pings, file_output

# Main script
if __name__ == "__main__":
    user_input = take_user_input()
    if user_input:
        dest_ip, max_ttl, timeout, packet_size, pings_per_hop, delay_between_pings, file_output = user_input
        tracert(dest_ip, max_ttl, timeout, packet_size, pings_per_hop, delay_between_pings, file_output)
