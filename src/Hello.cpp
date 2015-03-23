#include "llvm/Pass.h"
#include "llvm/Function.h"
#include "llvm/Support/raw_ostream.h"
#include <llvm/Support/CommandLine.h>
#include <fstream>
#include <set>
using namespace std;
using namespace llvm;
extern cl::opt<string> ExcludedFunctionsFileName;

namespace {
  class Hello : public FunctionPass {
    private:
    set<string> excludedFunctions;

    public:
    static char ID;
    Hello() : FunctionPass(ID) {
    	ifstream inFile(ExcludedFunctionsFileName.c_str());
		string name;
		errs() << "try to open " << ExcludedFunctionsFileName << '\n';
		if (!inFile) {
			errs() << "Unable to open " << ExcludedFunctionsFileName << '\n';
		} else {
			while(inFile >> name) {
				excludedFunctions.insert(name);
			}
			inFile.close();
		}		
    }

    bool runOnFunction(Function &func) {
    	bool not_excluded = (excludedFunctions.find(func.getName()) == excludedFunctions.end());
    	if (!func.isDeclaration() && not_excluded) {
    		errs() << "Hello: ";
    		errs().write_escaped(func.getName()) << '\n';
            for (Function::iterator i = func.begin(), e = func.end(); i != e; ++i) {
                errs() << "Basic block (name=" << i->getName() << ") has " 
                       << i->size() << " instructions.\n";
            }
            for (Function::iterator b = func.begin(), e = func.end(); b != e; ++b) {
                for (BasicBlock::iterator i = b->begin(), e = b->end(); i != e; ++i)
                    errs() << *i << "\n";
            }
              
    	}
      return false;
    }
  };
}

char Hello::ID = 0;
static RegisterPass<Hello> X("hello", "Hello World Pass", false, false);