#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <conio.h>

#define CMD 0xff  // Command indicator for Telnet commands
#define BUFSIZE 1024

// Function to initialize Winsock
void init_winsock() {
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("Failed. Error Code: %d\n", WSAGetLastError());
        exit(EXIT_FAILURE);
    }
}

// Function to clean up Winsock
void cleanup_winsock() {
    WSACleanup();
}

// Function to create a socket
SOCKET create_socket() {
    SOCKET sock;
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        printf("Could not create socket: %d\n", WSAGetLastError());
        exit(EXIT_FAILURE);
    }
    return sock;
}

// Function to connect to the server
void connect_to_server(SOCKET sock, char* ip, int port) {
    struct sockaddr_in server;
    server.sin_addr.s_addr = inet_addr(ip);
    server.sin_family = AF_INET;
    server.sin_port = htons(port);

    if (connect(sock, (struct sockaddr*)&server, sizeof(server)) == SOCKET_ERROR) {
        printf("Connection failed: %d\n", WSAGetLastError());
        exit(EXIT_FAILURE);
    }
    printf("Connected to server: %s:%d\n", ip, port);
}

// Function to handle Telnet negotiation commands
void negotiate(SOCKET sock, unsigned char* buf, int len) {
    int i;
    for (i = 0; i < len; i++) {
        if (buf[i] == CMD) {
            printf("Negotiating Telnet options...\n");
            buf[i] = CMD;  // Placeholder: Implement actual negotiation here
        }
    }
    if (send(sock, buf, len, 0) == SOCKET_ERROR) {
        printf("Error sending Telnet negotiation response: %d\n", WSAGetLastError());
        exit(EXIT_FAILURE);
    }
}

// Main function: Telnet client implementation
int main() {
    char ip[100];
    int port;
    SOCKET sock;
    char buffer[BUFSIZE];
    int bytes_received;
    
    // Initialize Winsock
    init_winsock();

    // Get IP and port from user
    printf("Enter server IP: ");
    scanf("%s", ip);
    printf("Enter server port: ");
    scanf("%d", &port);

    // Create socket and connect to server
    sock = create_socket();
    connect_to_server(sock, ip, port);

    // Main loop to send/receive data
    while (1) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(sock, &read_fds);  // Only monitor the socket

        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;

        int activity = select(0, &read_fds, NULL, NULL, &timeout);

        if (activity == SOCKET_ERROR) {
            printf("Select failed. Error: %d\n", WSAGetLastError());
            break;
        }

        // Check if data is available from server
        if (FD_ISSET(sock, &read_fds)) {
            bytes_received = recv(sock, buffer, BUFSIZE, 0);
            if (bytes_received == SOCKET_ERROR) {
                printf("recv failed: %d\n", WSAGetLastError());
                break;
            } else if (bytes_received == 0) {
                printf("Connection closed by the server.\n");
                break;
            }
            buffer[bytes_received] = '\0';
            printf("%s", buffer);
        }

        // Handle user input outside of select()
        if (_kbhit()) {  // Non-blocking check for user input
            fgets(buffer, BUFSIZE, stdin);  // Get full line of input
            buffer[strcspn(buffer, "\n")] = 0;  // Remove newline character

            if (strcmp(buffer, "quit") == 0) {
                printf("Exiting client...\n");
                break;
            }

            // Send input to server
            if (send(sock, buffer, strlen(buffer), 0) == SOCKET_ERROR) {
                printf("Send failed: %d\n", WSAGetLastError());
                break;
            }
        }
    }

    // Close socket and clean up
    closesocket(sock);
    cleanup_winsock();
    return 0;
}