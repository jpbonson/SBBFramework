#include "sbbMisc.h"

double gasdev()
{
	static int iset = 0;
	static double gset;
	double fac, rsq, v1, v2;

	if(iset == 0)
	{
		/* Extra deviate is not available from previous calculation. */

		do
		{
			v1 = 2.0 * drand48() - 1.0;
			v2 = 2.0 * drand48() - 1.0;
			rsq = v1 * v1 + v2 * v2;
		} while(rsq >= 1.0 || rsq == 0.0);

		fac = sqrt(-2.0 * log(rsq) / rsq);

		gset = v1 * fac;
		iset = 1;

		return v2 * fac;
	}
	else
	{
		/* Extra deviate is available from previous calculation. */

		iset = 0;

		return gset;
	}
}

void die(const char *file, 
		const char *func,
		const int line,
		const char *msg)
{
	cerr << "error in file " << string(file) << " function " << string(func);
	cerr << " line " << line << ": " << string(msg) << "... exiting" << endl;
	abort();
}

double EuclideanDistSqrd(double *x,
		double *y,
		int dim)
{
	double dist = 0;

	for(int i = 0; i < dim; i++)
		dist += (x[i] - y[i]) * (x[i] - y[i]);

	return dist;
}

double EuclideanDistSqrd(vector < double > &x,
		vector < double > &y)
{
	double dist = 0;
	vector < double > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end();
			xiter != enditer; xiter++, yiter++)
		dist += (*xiter - *yiter) * (*xiter - *yiter);

	return dist;
}

double EuclideanDistSqrdNorm(vector < double > &x,
		vector < double > &y)
{
	double dist = 0;
	int numFeatures = 0;
	vector < double > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end();
			xiter != enditer; xiter++, yiter++){
		dist += (*xiter - *yiter) * (*xiter - *yiter);
		numFeatures++;
	}
	return dist/numFeatures;
}

double EuclideanDist(vector < double > &x,
		vector < double > &y)
{
	double dist = 0;
	vector < double > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end(); xiter != enditer; xiter++, yiter++)
		dist += (*xiter - *yiter) * (*xiter - *yiter);

	return (double)sqrt(dist);
}

int hammingDist(vector < int > &x, 
		vector < int > &y)
{
	int dist = 0;
	vector < int > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end();
			xiter != enditer; xiter++, yiter++)
		dist += *xiter == *yiter? 0 : 1;

	return dist;
}

bool isEqual(vector < int > &x, 
		vector < int > &y)
{
	if(x.size() != y.size()) return false;

	vector < int > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end();
			xiter != enditer; xiter++, yiter++)
		if(*xiter != *yiter) return false;

	return true;
}

bool isEqual(vector < double > &x,
		vector < double > &y,
		double e)
{
	if(x.size() != y.size()) return false;

	vector < double > :: iterator xiter, yiter, enditer;

	for(xiter = x.begin(), yiter = y.begin(), enditer = x.end();
			xiter != enditer; xiter++, yiter++)
		if(isEqual(*xiter, *yiter, e) == false) return false;

	return true;
}

int stringToInt(string s)
{
	istringstream buffer(s);

	int i;

	buffer >> i;

	return i;
}

long stringToLong(string s)
{
	istringstream buffer(s);

	long l;

	buffer >> l;

	return l;
}

double stringTodouble(string s)
{
	istringstream buffer(s);

	double d;

	buffer >> d;

	return d;
}

int readMap(string fileName, 
		map < string, string > &args)
{
	ostringstream o;
	o << "cannot open map file: " << fileName;
	int pairs = 0;

	ifstream infile(fileName.c_str(), ios::in);

	if(infile == 0)
		die(__FILE__, __FUNCTION__, __LINE__, o.str().c_str());

	do
	{
		string key, value;

		if(infile) infile >> key; else break;
		if(infile) infile >> value; else break;

		args.insert(map < string, string > :: value_type(key, value));
		pairs++;

	} while(true);

	infile.close();

	return pairs;
}

bool getusage(double &sys,double &usr)
{
	struct rusage res;

	if(getrusage(RUSAGE_SELF, &res) == -1)
		return false;

	sys = (double) res.ru_stime.tv_sec + res.ru_stime.tv_usec * 1e-6;
	usr = (double) res.ru_utime.tv_sec + res.ru_utime.tv_usec * 1e-6;

	return true;
}

// random generator function:
ptrdiff_t myrandom (ptrdiff_t i)
{
	return lrand48()%i;
}

double vecMedian(vector<double> vec)
{
	typedef vector<double>::size_type vec_sz;

	vec_sz size = vec.size();

	if (size == 0)
		die(__FILE__, __FUNCTION__, __LINE__, "trying to get median of empty vector");

	sort(vec.begin(), vec.end());

	vec_sz mid = size/2;

	return size % 2 == 0 ? (vec[mid] + vec[mid-1]) / 2 : vec[mid];
}

int vecMedian(vector<int> vec)
{
	typedef vector<int>::size_type vec_sz;

	vec_sz size = vec.size();

	if (size == 0)
		die(__FILE__, __FUNCTION__, __LINE__, "trying to get median of empty vector");

	sort(vec.begin(), vec.end());

	vec_sz mid = size/2;

	return size % 2 == 0 ? (vec[mid] + vec[mid-1]) / 2 : vec[mid];
}

double vecMean(vector<double> vec)
{
	typedef vector<double>::size_type vec_sz;

	vec_sz size = vec.size();

	if (size == 0)
		return 0.0;

	double sum = accumulate(vec.begin(), vec.end(), 0.0);

	return sum/size;
}

double vecMean(vector<int> vec)
{
	typedef vector<int>::size_type vec_sz;

	vec_sz size = vec.size();

	if (size == 0)
		return 0.0;

	double sum = accumulate(vec.begin(), vec.end(), 0.0);

	return sum/size;
}

double stdDev(vector<double> vec){
	double sum = std::accumulate(vec.begin(), vec.end(), 0.0);
	double mean = sum / vec.size();
	vector<double> diff(vec.size());
	transform(vec.begin(), vec.end(), diff.begin(),
			bind2nd(std::minus<double>(), mean));
	double sq_sum = inner_product(diff.begin(), diff.end(), diff.begin(), 0.0);
	double stdev = sqrt(sq_sum / (vec.size()-1));
	return stdev;
}

/////////////////

double normalizedCompressionDistance(vector<int>&v1,vector<int>&v2){ // v1 = myBehaviourSequence, v2 = theirBehaviourSequence
	if (v1 == v2)
		return 0;
	ostringstream o;
	o << vecToStrNoSpace(v1);
	int Zx = compressedLength((char*) o.str().c_str());
	o.str("");
	o << vecToStrNoSpace(v2);
	int Zy = compressedLength((char*) o.str().c_str());
	o.str("");
	o << vecToStrNoSpace(v1) << vecToStrNoSpace(v2);
	int Zxy = compressedLength((char*) o.str().c_str());
	o.str("");
	int nom = Zxy-min(Zx,Zy);
	int denom = max(Zx,Zy);
	return ((double)nom/denom)/MAX_NCD;
}

template < class vtype > string vecToStrNoSpace(vector < vtype > &v){ 
	ostringstream oss;
	for(int i = 0; i < v.size(); i++) { 
		oss << v[i]; 
	}
	return oss.str();
}

#define MAX_NCD 1.2

int compressedLength(char * source){
	ostringstream oss;
	int blockSize100k = 9;
	int verbosity = 0;
	int workFactor = 30; // 0 = USE THE DEFAULT VALUE
	unsigned int sourceLength = strlen(source);
	unsigned int destLength = 1.01 * sourceLength + 600;    // Official formula, Big enough to hold output.  Will change to real size.
	char *dest = (char*)malloc(destLength);
	int returnCode = BZ2_bzBuffToBuffCompress( dest, &destLength, source, sourceLength, blockSize100k, verbosity, workFactor );

	if (returnCode == BZ_OK)
	{
		free(dest);
		return destLength;
	}
	else
	{
		free(dest);
		cout << " Can't get compressed length. " << "Error code:" << returnCode;
		return returnCode;
	}
}

/////////////////

vector<string> &split(const string &s, char delim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}

vector<string> split(const string &s, char delim) {
    vector<string> elems;
    split(s, delim, elems);
    return elems;
}

/***********************************************************************************************************/


