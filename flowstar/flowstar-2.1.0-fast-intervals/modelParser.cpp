/*---
  Flow*: A Verification Tool for Cyber-Physical Systems.
  Authors: Xin Chen, Sriram Sankaranarayanan, and Erika Abraham.
  Email: Xin Chen <chenxin415@gmail.com> if you have questions or comments.
  
  The code is released as is under the GNU General Public License (GPL).
---*/

#include "modelParser.h"
#include "Continuous.h"
#include "Interval.h"
#include <string.h>

extern int fyyparse();

// int main(int argc, const char *argv[]) {
//   fyydebug = 1;
//   // parseSetting.clear();
//   // parseSetting.strODE = "nonpolynomial center { 1 }";
//   // parseODE();

//   printf("strExpansion = %s\n", parseResult.strExpansion.c_str());
//   std::vector<std::string> odes;
//   odes.push_back("1");
  
//   std::vector<flowstar::Flowpipe> initialFPs;
//   std::vector<flowstar::Interval> initials;
//   initials.push_back(flowstar::Interval(0));
//   initialFPs.push_back(flowstar::Flowpipe(initials, flowstar::Interval(0)));
//   flowstar::ContinuousSystem cs(odes, initialFPs);

//   printf("strExpansion = %s\n", parseResult.strExpansion.c_str());

//   return 0;
// }

int main(int argc, const char *argv[])
{
  fyydebug = 1;
	fyyparse();

	return 0;
}



