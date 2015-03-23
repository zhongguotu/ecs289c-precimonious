#ifndef CREATE_SEARCH_FILE_GUARD
#define CREATE_SEARCH_FILE_GUARD 1

#include <llvm/Pass.h>
#include <llvm/Instructions.h>
#include <llvm/Support/CommandLine.h>

#include <map>
#include <set>
#include <vector>

namespace llvm {
  class GlobalVariable;
  class raw_fd_ostream;
  class Type;
  class Value;
}

using namespace std;
using namespace llvm;
extern cl::opt<string> ExcludedFunctionsFileName;
extern cl::opt<string> IncludedFunctionsFileName;
extern cl::opt<string> IncludedGlobalVarsFileName;
extern cl::opt<string> ExcludedLocalVarsFileName;
extern cl::opt<bool> ListOperators;
extern cl::opt<bool> ListFunctions;
extern cl::opt<bool> OnlyScalars;
extern cl::opt<bool> OnlyArrays;
extern cl::opt<string> FileName;


class CreateSearchFile : public ModulePass {
  
public:
  CreateSearchFile() : ModulePass(ID) {}
  
  virtual bool runOnModule(Module &module);

  virtual void getAnalysisUsage(AnalysisUsage &AU) const;

  static char ID; // Pass identification, replacement for typeid

private:
  bool doInitialization(Module &);

  void runOnFunction(Function &function, raw_fd_ostream &outfile);

  void findFunctionCalls(Function &function, raw_fd_ostream &outfile);

  void findGlobalVariables(Module &module, raw_fd_ostream &outfile);

  void findLocalVariables(Function &function, raw_fd_ostream &outfile);

  void findOperators(Function &function, raw_fd_ostream &outfile);

  string findOperandName(Value *value);

  void printGlobal(raw_fd_ostream &outfile, string name, Type *type);

  void printLocal(Function &function, raw_fd_ostream &outfile, string name, Type *type);

  void printOperator(Function &function, raw_fd_ostream &outfile, Instruction &op, vector<string> &operands);

  set<string> excludedFunctions;

  set<string> includedFunctions;

  set<string> includedGlobalVars;

  set<string> excludedLocalVars;

  set<string> functionCalls;

  set<string> globalVars;

  set<string> localVars;

  map<Value*, string> allocaToVars;

  bool first;

};

#endif // CREATE_SEARCH_FILE_GUARD
