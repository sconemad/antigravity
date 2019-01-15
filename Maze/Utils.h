#ifndef _PI_WARS_UTILS_H_
#define _PI_WARS_UTILS_H_

#include <cmath>
#include <algorithm>
#include <vector>
#include <stdexcept>

constexpr double PI = 3.14159265359;

inline int toint(double v) {
  return static_cast< int >(round(v));
}

template <class T> class Vector2D
{
  std::size_t m_xsize;
  std::size_t m_ysize;
  std::vector<T> m_Vec;

public:
  Vector2D(int xsize, int ysize, const T& t = T()) :
    m_xsize(xsize),
    m_ysize(ysize),
    m_Vec(xsize * ysize, t)
  {}

  const size_t xsize() const { return m_xsize; }
  const size_t ysize() const { return m_ysize; }

  const T& Get(std::size_t x, std::size_t y) const
  {
    if (x >= m_xsize || y >= m_ysize) throw std::out_of_range("Vector2D");
    return m_Vec[x * m_xsize + y];
  }
  T& Get(std::size_t x, std::size_t y)
  {
    if (x >= m_xsize || y >= m_ysize) throw std::out_of_range("Vector2D");
    return m_Vec[x * m_xsize + y];
  }
};

class Angle
{
  double radians;

  void assign(double rad) {
    radians = remainder(rad, 2.0 * PI);
  }

public:
  explicit Angle(double r) : radians(0.0) {
    assign(r);
  }

  Angle(const Angle& a) : radians(a.radians) {}

  Angle& operator=(const Angle& a) {
    radians = a.radians;
    return *this;
  }

  Angle operator+(Angle a) const {
    a += *this;
    return a;
  }
  Angle operator-(Angle a) const {
    a -= *this;
    return a;
  }
  Angle operator-() const {
    Angle res = *this;
    res.assign(-res.radians);
    return res;
  }

  operator double() const { return radians; }

  void operator+=(const Angle& other) {
    assign(radians + other.radians);
  }
  void operator-=(const Angle& other) {
    assign(radians - other.radians);
  }
  void operator/=(double d) {
    assign(radians / d);
  }
};

const Angle pi(PI);
const Angle hpi(PI / 2.0);
const Angle qpi(PI / 4.0);


// get the angle from positive x axis
// positive is to the right, negative to the left
inline Angle AngleFromPos(double x, double y)
{
  return Angle(-(atan2(y, x) - hpi));
}

inline Angle Speed2Angle(double spdl, double spdr, double width, double distance)
{
  if (fabs(spdl - spdr) < 0.0001) return Angle(0.0);
  const bool right = spdl > spdr;
  const double maxs = std::max(spdr, spdl);
  const double mins = std::min(spdr, spdl);
  const double radius = (width / 2.0) + (mins * width) / (maxs - mins);
  return Angle(right ? asin(distance / radius) : -asin(distance / radius));
}

inline void Angle2Speed(Angle angle, double maxspd, double distance,
                        double width, double& spdl, double& spdr)
{
  if (angle == 0.0) {
    spdl = spdr = maxspd;
    return;
  }
  const double radius = distance / sin(fabs(angle));
  const double mins = maxspd * (radius - width / 2.0) / (radius + width / 2.0);
  if (angle > 0.0) {
    spdl = maxspd;
    spdr = mins;
  }
  else {
    spdr = maxspd;
    spdl = mins;
  }
}

inline double sq(double v) { return v * v; }

class Point
{
protected:
  double m_x;
  double m_y;

public:
  Point(double x = 0.0, double y = 0.0) : m_x(x), m_y(y) {}

  double x() const { return m_x; }
  double y() const { return m_y; }

  void setx(double x) { m_x = x; }
  void sety(double y) { m_y = y; }

  double Distance(const Point& other) const
  {
    return sqrt(sq(m_x - other.m_x) + sq(m_y - other.m_y));
  }

  void Move(Angle ang, double len)
  {
    m_x += sin(ang) * len;
    m_y += cos(ang) * len;
  }

  void operator+=(const Point& other) {
    m_x += other.m_x;
    m_y += other.m_y;
  }
  void operator-=(const Point& other) {
    m_x -= other.m_x;
    m_y -= other.m_y;
  }
  void operator*=(double d) {
    m_x *= d;
    m_y *= d;
  }

  Point operator+(const Point& other) const {
    Point tmp = *this;
    tmp += other;
    return tmp;
  }

  bool CheckBoundary(double x, double y, double margin) const {
    return m_x > margin && m_x < x - margin && m_y > margin && m_y < y - margin;
  }
};

class Pos : public Point
{
  Angle angle;

public: 
  Pos(double x, double y, double a) : Point(x, y), angle(a) {}

  Angle getAngle() const { return angle; }

  void Move(double len) {
    Point::Move(angle, len);
  }

  void Move(Angle ang, double len) {
    Point::Move(ang + angle, len);
  }

  Pos operator+(const Pos& other) const {
    Pos p = *this;
    p.m_x += other.m_x;
    p.m_y += other.m_y;
    p.angle += other.angle;
    return p;
  }
  Pos operator-(const Pos& other) const {
    Pos p = *this;
    p.m_x -= other.m_x;
    p.m_y -= other.m_y;
    p.angle -= other.angle;
    return p;
  }

  // speed in mm / sec
  void Curve(double spdl, double spdr, double ms, double wid)
  {
    const double speed = (spdl + spdr) / 2000.0;  // mm / ms
    const double dist = speed * 10.0;
    const Angle rad = Speed2Angle(spdl, spdr, wid - 15.0, dist);

    // Move in steps of 10ms, to create smooth circular paths
    while (ms > 0.0) {
      const double step = std::min(10.0, ms);
      ms -= step;
      angle += rad;
      Move(speed * step);
    }
  }
};

class Sensor {
  int num;
  Angle MoveAngle;
  double MoveDist;
  Angle angle;
  double mindist;

public:
  Sensor(int n, double x, double y, Angle a, double md = 50.0) :
    num(n),
    MoveAngle(atan2(x, y)),
    MoveDist(sqrt(x*x + y*y)),
    angle(a), mindist(md) {}

  int Num() const { return num; }

  const Angle& getAngle() const { return angle; }

  double getMinDist() const { return mindist; }

  void Process(Pos& pos) const {
    pos.Move(MoveAngle, MoveDist);
  }

  double DistanceToLast(Point ob) const {
    return m_last.Distance(ob);
  }

  void SetLast(Point ob) {
    m_last = ob;
  }

private:
  Point m_last;
};


///////////////  Bitmap helpers  ////////////////////////////

const int bytesPerPixel = 3; /// red, green, blue
const int fileHeaderSize = 14;
const int infoHeaderSize = 40;

unsigned char* createBitmapFileHeader(int height, int width);

unsigned char* createBitmapInfoHeader(int height, int width);

void generateBitmapImage(const std::vector< std::vector<bool> >& image,
                         int height, int width, const char* imageFileName);


#endif
