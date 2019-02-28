#ifndef _PI_WARS_COMMS_H_
#define _PI_WARS_COMMS_H_

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <mutex>

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
    // Make sure this operation doesn't block
    if (com_mtx.try_lock()) {
      setSpeedInternal(left, right);
      com_mtx.unlock();

      std::lock_guard<std::mutex> lg(speed_mtx);
      leftspeed = leftspeedrequest = left;
      rightspeed = rightspeedrequest = right;
    }
    else {
      std::lock_guard<std::mutex> lg(speed_mtx);
      leftspeedrequest = left;
      rightspeedrequest = right;
    }
  }
  
  int getDistance(char sensor)
  {
    char msg[256];
    int result = 0;

    std::lock_guard<std::mutex> clg(com_mtx);
    // Send request
    snprintf(msg, 256, "dist get %c\n", sensor);
    send(fd, msg, strlen(msg), 0);
    
    // Wait for result
    int n = recv(fd, msg, 256, 0);
    if (n > 0) {
      msg[n] = '\0';
      int d = 0;
      if (sscanf(msg, "%d\n", &d) == 1) result = d;
    }

    // Check if we also need to send new speeds, while com_mtx is locked
    std::lock_guard<std::mutex> slg(speed_mtx);
    if (leftspeed != leftspeedrequest || rightspeed != rightspeedrequest) {
      leftspeed = leftspeedrequest;
      rightspeed = rightspeedrequest;
      setSpeedInternal(leftspeed, rightspeed);
    }

    return result;
  }

  static const char ECHO_CENTRE = 'C';
  static const char ECHO_LEFT = 'L';
  static const char ECHO_RIGHT = 'R';

private:
  // We need to make sure com_mtx is locked when this is called
  void setSpeedInternal(double l, double r)
  {
    char msg[256];
    snprintf(msg, 256, "drive setLR %f %f\n", l, r);
    send(fd, msg, strlen(msg), 0);
  }

  double leftspeed = -999.0;
  double rightspeed = -999.0;
  double leftspeedrequest = -999.0;
  double rightspeedrequest = -999.0;
  
  int fd = -1;
  std::mutex com_mtx;
  std::mutex speed_mtx;
};

#endif
