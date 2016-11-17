/* C++ header file  Sun_position_algorithms.h



last modified : 9 Sept. 2014

List of modifications:
9 Sept. 2014: since function fmod returns also negative values on some compilers, a check was added after using it



This file contains the 5 algorithms to calculate the sun position described in the paper "Five new algorithms for the computation of sun position from 2010 to 2110", Solar Energy 86 (2012) 1323-1337.


Use of the algortihms:

- This header file must be included in the program.

- At the beginning, before starting calculations, a class of type sunpos must be declared. The constructor of the class accepts also initial values for the input parameters of the algorithms, but they can be omitted (default values are used) and given later.

Examples of declarations:

  sunpos Sun_Position;

or

  sunpos Sun_Position(UT, Day, Month, Year, Dt, Long, Lat, P, T);
  
In this second example, variables UT, Month, etc. show the parameters that can be given to the constructor: UT is the time UT (double, in hours), Day, Month and Year are the date (all integers), Dt is the difference TT-UT (double, in seconds), Long and Lat are the geographical longitude and latitude (double, in radians), P is the pressure (double, in atm), T is the temperature (double, in Celsius degrees).

- Before every position calculations, the input data can be set simply assigning new values to the members of the class: es. to change the hour UT in the class declared as above, assigning the value NewUT, the command is

  Sun_Position.UT = NewUT;

Input members in the class are named UT, Day, Month, Year, Dt, Longitude, Latitude, Pressure, Temperature.
The variables not assigned before the calculation are left unchanged, This is convenient, since usually changes in the input data concern only the time, while coordinates are kept fixed. Parameters left unchanged can be declared at the beginning, e.g. using the constructor, and then left unchanged through all the computations.

- once the input variables are set, the calculations (e.g. using Algorithm 3) can be performed simply with the command

  Sun_Position.Algorithm3();
  
or

  Sun_Position.Algorithm3('s');

In the first case the long algorithm is used, while in the second case (with the parameter 's') the short algorithm is used.
Other algorithms (1,2,4,5) can be used simply changing the final number.
This command does not return any values, but writes the output values computed in the corresponding class members, which can be read and used as usual variables. In order to output on the screen the value of the Zenith, for example, the command

  cout<<Sun_Position.Zenith<<endl;
  
can be used. Output members in the class are named RightAscension, Declination, HourAngle, Zenith, Azimuth.

Note that all the class members are public; no access control to variables, neither consistency controls are made, since the maximum computational efficiency and versatility are the aim. A bit of caution should be employed (e.g. when changing input parameters, outputs does not change automatically and remains at the old values until the function AlgorithmN is called; or, when using short algorithms, quantities not computed (Zenith and Azimuth) are left with the previous values).

The following code performs the computation of the position at every hour (from 1 to 24) on 1st January 2012, at Rome, using Algorithm 5, writing a table of the zenith and azimuth on the output screen. All the input parameters except UT are left unchanged as declared in the constructor, while the hour is changed at every calculation.

  (...)
  sunpos Sun_Position(0.0,	// initial hour (arbitrary - not used)
		      1,1,2012,	// date
		      65.0,	// Dt
		      0.21787,	// Longitude in radians
		      0.73117,	// Latitude in radians
		      1, 20);	// Pressure (atm) and Temperature (Celsius)
  cout<<endl<<"Hour\tZen\tAz"<<endl;
  for (double hour = 1.0; hour < 24.1; hour += 1.0) {
    Sun_Position.UT = hour-1.0; 	// correct UT ("hour" is the time of Rome)
    Sun_Position.Algorithm5();
    cout<<hour<<"\t"<<Sun_Position.Zenith<<"\t"<<Sun_Position.Azimuth<<endl;
  }
  (...)
    
*/


#include<cmath>

#ifndef PI
#define PI 3.14159265358979
#endif

#define PI2 6.28318530717959 // 2*PI
#define PIM 1.57079632679490 // PI/2

class sunpos {

public:

  // input data:
  double UT;
  int Day;
  int Month;
  int Year;
  double Dt;
  double Longitude;
  double Latitude;
  double Pressure;
  double Temperature;

  //output data
  double RightAscension;
  double Declination;
  double HourAngle;
  double Zenith;
  double Azimuth;
  
  //auxiliary
  double t, te, wte, s1, c1, s2, c2, s3, c3, s4, c4,
    sp, cp, sd, cd, sH, cH, se0, ep, De, lambda, epsi,
    sl, cl, se, ce, L, nu, Dlam;
  int yt, mt;

  // constructor
  sunpos(double h = 0.0, int  d = 1, int m = 1, int y = 2010,
    double Dt = 65.0, double Long = 0.0, double lat = 0.0,
    double P = 1.0, double T = 20.0);
  
  // algorithms
  void Algorithm1(char flag = 'l');
  void Algorithm2(char flag = 'l');
  void Algorithm3(char flag = 'l');
  void Algorithm4(char flag = 'l');
  void Algorithm5(char flag = 'l');

};



sunpos::sunpos(double h, int d, int m, int y, double dt, double Long, double lat, double P, double T) {
  UT = h;
  Day = d;
  Month = m;
  Year = y;
  Dt = dt;
  Longitude = Long;
  Latitude = lat;
  Pressure = P;
  Temperature = T;
}



void sunpos::Algorithm1(char flag) {
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = double(int(365.25*double(yt-2000)) + int(30.6001*double(mt+1)) - int(0.01*double(yt)) + Day) + 0.0416667*UT - 21958.0;
  te = t + 1.1574e-5*Dt;

  wte = 0.017202786*te;

  s1 = sin(wte);
  c1 = cos(wte);
  s2 = 2.0*s1*c1;
  c2 = (c1+s1)*(c1-s1);

  RightAscension = -1.38880 + 1.72027920e-2*te + 3.199e-2*s1 - 2.65e-3*c1 + 4.050e-2*s2 + 1.525e-2*c2;
  RightAscension = fmod(RightAscension, PI2);
  if (RightAscension < 0.0) RightAscension += PI2;

  Declination = 6.57e-3 + 7.347e-2*s1 - 3.9919e-1*c1 + 7.3e-4*s2 - 6.60e-3*c2;

  HourAngle = 1.75283 + 6.3003881*t + Longitude - RightAscension;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  if (flag == 's') return;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

}



void sunpos::Algorithm2(char flag) {
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = double(int(365.25*double(yt-2000)) + int(30.6001*double(mt+1)) - int(0.01*double(yt)) + Day) + 0.0416667*UT - 21958.0;
  te = t + 1.1574e-5*Dt;

  wte = 0.017202786*te;

  s1 = sin(wte);
  c1 = cos(wte);
  s2 = 2.0*s1*c1;
  c2 = (c1+s1)*(c1-s1);
  s3 = s2*c1 + c2*s1;
  c3 = c2*c1 - s2*s1;
  s4 = 2.0*s2*c2;
  c4 = (c2+s2)*(c2-s2);

  RightAscension = -1.38880 + 1.72027920e-2*te + 3.199e-2*s1 - 2.65e-3*c1 + 4.050e-2*s2 + 1.525e-2*c2 + 1.33e-3*s3 + 3.8e-4*c3 + 7.3e-4*s4 + 6.2e-4*c4;
  RightAscension = fmod(RightAscension, PI2);
  if (RightAscension < 0.0) RightAscension += PI2;

  Declination = 6.57e-3 + 7.347e-2*s1 - 3.9919e-1*c1 + 7.3e-4*s2 - 6.60e-3*c2 + 1.50e-3*s3 - 2.58e-3*c3 + 6e-5*s4 - 1.3e-4*c4;

  HourAngle = 1.75283 + 6.3003881*t + Longitude - RightAscension;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  if (flag == 's') return;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

}



void sunpos::Algorithm3(char flag) {
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = double(int(365.25*double(yt-2000)) + int(30.6001*double(mt+1)) - int(0.01*double(yt)) + Day) + 0.0416667*UT - 21958.0;
  te = t + 1.1574e-5*Dt;

  wte = 0.0172019715*te;

  lambda = -1.388803 + 1.720279216e-2*te + 3.3366e-2*sin(wte - 0.06172) + 3.53e-4*sin(2.0*wte - 0.1163);

  epsi = 4.089567e-1 - 6.19e-9*te;

  sl = sin(lambda);
  cl = cos(lambda);
  se = sin(epsi);
  ce = sqrt(1-se*se);

  RightAscension = atan2(sl*ce, cl);
  if (RightAscension < 0.0) 
    RightAscension += PI2;

  Declination = asin(sl*se);

  HourAngle = 1.7528311 + 6.300388099*t + Longitude - RightAscension;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  if (flag == 's') return;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

}



void sunpos::Algorithm4(char flag) {
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = double(int(365.25*double(yt-2000)) + int(30.6001*double(mt+1)) - int(0.01*double(yt)) + Day) + 0.0416667*UT - 21958.0;
  te = t + 1.1574e-5*Dt;

  wte = 0.0172019715*te;

  L = 1.752790 + 1.720279216e-2*te + 3.3366e-2*sin(wte - 0.06172) + 3.53e-4*sin(2.0*wte - 0.1163);

  nu = 9.282e-4*te - 0.8;
  Dlam = 8.34e-5*sin(nu);
  lambda = L + PI + Dlam;

  epsi = 4.089567e-1 - 6.19e-9*te + 4.46e-5*cos(nu);

  sl = sin(lambda);
  cl = cos(lambda);
  se = sin(epsi);
  ce = sqrt(1-se*se);

  RightAscension = atan2(sl*ce, cl);
  if (RightAscension < 0.0) 
    RightAscension += PI2;

  Declination = asin(sl*se);

  HourAngle = 1.7528311 + 6.300388099*t + Longitude - RightAscension + 0.92*Dlam;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  if (flag == 's') return;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

}



void sunpos::Algorithm5(char flag) {
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = double(int(365.25*double(yt-2000)) + int(30.6001*double(mt+1)) - int(0.01*double(yt)) + Day) + 0.0416667*UT - 21958.0;
  te = t + 1.1574e-5*Dt;

  wte = 0.0172019715*te;

  s1 = sin(wte);
  c1 = cos(wte);
  s2 = 2.0*s1*c1;
  c2 = (c1+s1)*(c1-s1);
  s3 = s2*c1 + c2*s1;
  c3 = c2*c1 - s2*s1;

  L = 1.7527901 + 1.7202792159e-2*te + 3.33024e-2*s1 - 2.0582e-3*c1 + 3.512e-4*s2 - 4.07e-5*c2 + 5.2e-6*s3 - 9e-7*c3 -8.23e-5*s1*sin(2.92e-5*te) + 1.27e-5*sin(1.49e-3*te - 2.337) + 1.21e-5*sin(4.31e-3*te + 3.065) + 2.33e-5*sin(1.076e-2*te - 1.533) + 3.49e-5*sin(1.575e-2*te - 2.358) + 2.67e-5*sin(2.152e-2*te + 0.074) + 1.28e-5*sin(3.152e-2*te + 1.547) + 3.14e-5*sin(2.1277e-1*te - 0.488);

  nu = 9.282e-4*te - 0.8;
  Dlam = 8.34e-5*sin(nu);
  lambda = L + PI + Dlam;

  epsi = 4.089567e-1 - 6.19e-9*te + 4.46e-5*cos(nu);

  sl = sin(lambda);
  cl = cos(lambda);
  se = sin(epsi);
  ce = sqrt(1-se*se);

  RightAscension = atan2(sl*ce, cl);
  if (RightAscension < 0.0) 
    RightAscension += PI2;

  Declination = asin(sl*se);

  HourAngle = 1.7528311 + 6.300388099*t + Longitude - RightAscension + 0.92*Dlam;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  if (flag == 's') return;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

}  
