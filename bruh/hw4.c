#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <strings.h>
#include <unistd.h>

int main(int argc, char *argv[])
{

    //parse cmd line arguments
    char *server_hostname = argv[1];
    unsigned short server_port = atoi(argv[2]);
    int n = atoi(argv[3]);
    int values[n + 1];
    values[0] = htonl(n);
    for (int i = 1; i <= n; i++)
    {
            values[i] = htonl(atoi(argv[3 + i]));
    }

    /* create TCP client socket (endpoint) */
    int sd = socket(AF_INET, SOCK_STREAM, 0);
    if (sd == -1)
    {
        perror("socket() failed");
        exit(EXIT_FAILURE);
    }
    // connect to server
    struct hostent *hp = gethostbyname(server_hostname);

    if (hp == NULL)
    {
        fprintf(stderr, "ERROR: gethostbyname() failed\n");
        return EXIT_FAILURE;
    }

    struct sockaddr_in tcp_server;
    tcp_server.sin_family = AF_INET;
    memcpy((void *)&tcp_server.sin_addr, (void *)hp->h_addr_list[0], hp->h_length);
    tcp_server.sin_port = htons(server_port);
    if (connect(sd, (struct sockaddr *)&tcp_server, sizeof(tcp_server)) == -1)
    {
        perror("connect() failed");
        return EXIT_FAILURE;
    }
    printf("CLIENT: Successfully connected to server\n");
// application protocol section begins
    printf("CLIENT: Sending %d integer value%s\n", n, n == 1 ? "" : "s" );

    //send int values
    send(sd, &values, (n + 1) * sizeof(int), 0);

    //receive first packet from server
    int intBuffer[1];
    int num = recv(sd, intBuffer, sizeof(int), 0);
    if (num == -1)
    {
        perror("first recv() failed");
        return EXIT_FAILURE;
    }
    printf("CLIENT: Rcvd result: %d\n", ntohl(intBuffer[0]));
    //receive second packet from server
    int r, len = 0, cap = 256;
    char b;
    char *outline = (char*) malloc(cap);
    sleep(1);
    if (!outline) return EXIT_FAILURE;
     do
    {
        // printf("sdfds\n");
        r = recv(sd, &b, sizeof(char), MSG_DONTWAIT);
        if (r <= 0) // didn't read anything or error
        {
            break;
        }

        if (len == cap)
        {
            cap += 256;
            char *newline = (char*) realloc(outline, cap);
            if (!newline)
            {
                free(outline);
                return EXIT_FAILURE;
            }
            outline = newline;
        }

        outline[len] = b;
        ++len;
    }while (1);
    printf("CLIENT: Rcvd secret message: \"%s\"\n",outline);

    close(sd);
    printf("CLIENT: Disconnected from server\n");

}