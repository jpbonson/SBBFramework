//g++ -g ncd.cpp -lbz2 -o myNcd
#include <stdlib.h>
#include <bzlib.h>
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <cstring>
#include <sstream>
// #include <fstream>
// #include <iostream>
// #include <cmath>
// #include <map>
// #include <algorithm>
// #include <numeric>
// #include <iterator>
// #include <bzlib.h>
// #include <cmath>
// #include <limits>
// #include <sys/resource.h>

using namespace std;

template < class vtype > string vecToStrNoSpace(vector < vtype > &v){ 
	ostringstream oss;
	for(int i = 0; i < v.size(); i++) { 
		oss << v[i]; 
	}
	return oss.str();
}

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

double normalizedCompressionDistance(vector<int>&v1,vector<int>&v2){ // v1 = myBehaviourSequence, v2 = theirBehaviourSequence
	double MAX_NCD = 1.2;
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

int main(int argc, char* argv[])
{
	if (argc < 2){
		cout << "gimme 2 args!" << endl;
		exit(0);
	}
	string s1 = argv[1];
	string s2 = argv[2];
	ostringstream o;
	vector < int > sequenceA;
	for (int i = 0; i < s1.length(); i++)
		sequenceA.push_back(s1[i]-'0');

	vector < int > sequenceB;
	for (int i = 0; i < s2.length(); i++)
		sequenceB.push_back(s2[i]-'0');
	cout << normalizedCompressionDistance(sequenceA,sequenceB) << endl;
}

