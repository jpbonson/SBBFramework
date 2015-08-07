#ifndef SBBMISC_H
#define SBBMISC_H
//#define MYDEBUG
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <fstream>
#include <string>
#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include <algorithm>
#include <numeric>
#include <iterator>
#include <bzlib.h>
#include <cmath>
#include <limits>
#include <sys/resource.h>

using std::numeric_limits;
using namespace std;

#define NEARZERO 10e-12
#define EPSILON_SBB 1e-5
#define MAX_NCD 1.2

/* Returns a normally distributed deviate with zero mean and unit variance
   based on Section 7.2 of 'Numerical Recipes in C'.*/
double gasdev();

/* Gaussian probability function with mean 'mu' and standard deviation 'sd'. */
inline double GaussPF(double x, double mu, double sd)
{ return exp( - ( x - mu ) * ( x - mu ) / ( 2 * sd * sd ) ) / ( sd * sqrt( 2 * M_PI ) ); }

/* We can use this as a cheaper bid activation function. */
inline double GaussPF(double x)
{ return exp(- x * x); }

void die(const char*, const char *, const int, const char *);

double EuclideanDistSqrd(double *, double *, int);
double EuclideanDistSqrd(vector < double > &, vector < double > &);
double EuclideanDistSqrdNorm(vector < double > &, vector < double > &);
double EuclideanDist(vector < double > &, vector < double > &);

int hammingDist(vector < int > &, vector < int > &);

inline bool isEqual(double x, double y)
{ return fabs(x - y) < EPSILON_SBB; }

inline bool isEqual(double x, double y, double e)
{ return fabs(x - y) < e; }

bool isEqual(vector < int > &, vector < int > &);
bool isEqual(vector < double > &, vector < double > &, double);

int stringToInt(string);
long stringToLong(string);
double stringTodouble(string);

int readMap(string, map < string, string > &);

bool getusage(double &, double &);
ptrdiff_t myrandom (ptrdiff_t );

template < class vtype > string vecToStr(vector < vtype > &v)
{ ostringstream oss; oss.precision(numeric_limits<double>::digits10+1); 
   for(int i = 0; i < v.size(); i++) { 
     oss << v[i];
     if (i < v.size() - 1) 
       oss << " "; 
   } 
   return oss.str(); 
}

template < class vtype > string vecToStrNoSpace(vector < vtype > &v)
{ ostringstream oss; for(int i = 0; i < v.size(); i++) { oss << v[i]; } return oss.str(); }

inline bool fileExists(const char *fileName)
{
	ifstream infile(fileName);
	return infile.good();
}

double vecMedian(vector<double>);
int vecMedian(vector<int>);
double vecMean(vector<double>);
double vecMean(vector<int>);
double stdDev(vector<double>);
int compressedLength(char *);
double normalizedCompressionDistance(vector<int>&v1,vector<int>&v2);
inline double sas(double s1,double s2, double a){
	return sqrt(pow(s1,2) + pow(s2,2) - (2*s1*s2*cos(a*(3.14159265/180.0))));
}
inline double discretize(double f,double min, double max, int steps){
	double d = round(((f - min)/(max - min))*(steps-1));
	return d>steps?steps-1:d;
}

struct noveltyDescriptor {
	double novelty;
	vector < int > profile;
	vector < long > profileLong;
	//noveltyDescriptor(double n,vector < int > &p, vector < int > &pL):novelty(n),profile(p),profileLong(pL) {}
} ;

vector<string> &split(const string &s, char delim, vector<string> &elems);
vector<string> split(const string &s, char delim);
#endif
