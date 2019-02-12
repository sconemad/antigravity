#ifndef _PI_WARS_COMMS_H_
#define _PI_WARS_COMMS_H_

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>

class Comms
{
public:
  Comms()
  {
    const char* SOCKET = "/tmp/robot";
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET, sizeof(addr.sun_path) - 1);
    fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
      close(fd);
      fd = -1;
    }
  }

  ~Comms()
  {
    if (fd >= 0) close(fd);
  }

  void setSpeed(double left, double right)
  {
    char msg[256];
    snprintf(msg, 256, "drive setLR %f %f\n", left, right); 
    send(fd, msg, strlen(msg), 0);
  }
  
  int getDistance(char sensor)
  {
    char msg[256];
    snprintf(msg, 256, "dist get %c\n", sensor);
    send(fd, msg, strlen(msg), 0);
    
    int n = recv(fd, msg, 256, 0);
    if (n > 0) {
      msg[n] = '\0';
      int d = 0;
      if (sscanf(msg, "%d\n", &d) == 1) return d;
    }
    return 0;
  }

  static const char ECHO_CENTRE = 'C';
  static const char ECHO_LEFT = 'L';
  static const char ECHO_RIGHT = 'R';
  
  int fd = -1;
};

#endif
