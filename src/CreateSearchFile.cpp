#include "CreateSearchFile.hpp"
#include "CreateIDBitcode.hpp"

#include <llvm/Analysis/DebugInfo.h>
#include <llvm/Argument.h>
#include <llvm/Instructions.h>
#include <llvm/Module.h>
#include <llvm/Support/CommandLine.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/ValueSymbolTable.h>

#include <fstream>
#include <sstream>

using namespace llvm;

cl::opt<bool> StartFromOriginalType("original-type", cl::value_desc("flag"), cl::desc("Start from the original types"), cl::init(false));


static void printDimensions(vector<unsigned> &dimensions, raw_fd_ostream &outfile) {
  for(unsigned i = 0; i < dimensions.size(); i++) {
    outfile << "[" << dimensions[i] << "]";
  }
  return;
}


static void printAll(string asterisk, raw_fd_ostream &outfile) {
  outfile << "[\"float" << asterisk << "\", \"double" << asterisk << "\", \"longdouble" << asterisk << "\"]\n";
  return;
}


static void printAllArray(vector<unsigned> &dimensions, raw_fd_ostream &outfile) {
  outfile << "[";
  outfile << "\"float";
  printDimensions(dimensions, outfile);
  outfile << "\", ";

  outfile << "\"double";
  printDimensions(dimensions, outfile);
  outfile << "\", ";

  outfile << "\"longdouble";
  printDimensions(dimensions, outfile);
  outfile << "\"]\n";
  return;
}


static void printType(Type *type, raw_fd_ostream &outfile) {
  unsigned int typeID = type->getTypeID();

  switch(typeID) {

  case Type::FloatTyID:
    if (StartFromOriginalType) {
      outfile << "[\"float\"]\n";
    } else {
      printAll("", outfile);
    }
    break;

  case Type::DoubleTyID:
    if (StartFromOriginalType) {
      outfile << "[\"float\", \"double\"]\n";
    } else {
      printAll("", outfile);
    }
    break;

  case Type::X86_FP80TyID:
  case Type::PPC_FP128TyID:
    printAll("", outfile);
    break;

  case Type::IntegerTyID:
    outfile << "\"int\"\n";
    break;

  case Type::PointerTyID: {
    PointerType *pointer = dyn_cast<PointerType>(type);
    Type *elementType = pointer->getElementType();
    unsigned int typeElementID = elementType->getTypeID();
    switch(typeElementID) {
    case Type::FloatTyID:
      if (StartFromOriginalType) {
        outfile << "[\"float*\"]\n";
      } else {
        printAll("*", outfile);
      }
      break;

    case Type::DoubleTyID:
      if (StartFromOriginalType) {
        outfile << "[\"float*\", \"double*\"]\n";
      } else {
        printAll("*", outfile);
      }
      break;

    case Type::X86_FP80TyID:
      printAll("*", outfile);
      break;

    default:
      outfile << "\"pointer\"\n";
      break;
    }
    break;
  }

  case Type::StructTyID:
    outfile << "\"struct\"\n"; // complete type
    break;

  case Type::ArrayTyID: {
    vector<unsigned> dimensions;
    while(ArrayType* arrayType = dyn_cast<ArrayType>(type)) {
      type = arrayType->getElementType();
      dimensions.push_back(arrayType->getNumElements());
    }

    if (type->isFloatingPointTy()) {
      unsigned int elementTypeID = type->getTypeID();

      switch(elementTypeID) {
      case Type::FloatTyID:
      	if (StartFromOriginalType) {
      	  outfile << "[";
      	  outfile << "\"float";
      	  printDimensions(dimensions, outfile);
      	  outfile << "\"]\n";
      	} else {
      	  printAllArray(dimensions, outfile);
      	}
      	break;

      case Type::DoubleTyID:
      	if (StartFromOriginalType) {
      	  outfile << "[";
      	  outfile << "\"float";
      	  printDimensions(dimensions, outfile);
      	  outfile << "\", ";

      	  outfile << "\"double";
      	  printDimensions(dimensions, outfile);
      	  outfile << "\"]\n";
      	} else {
      	  printAllArray(dimensions, outfile);
      	}
      	break;

      case Type::X86_FP80TyID:
      case Type::PPC_FP128TyID:
      	printAllArray(dimensions, outfile);
      	break;

      default:
      	// do nothing
      	break;
      }
    } else {
      outfile << "\"" << *type;
      printDimensions(dimensions, outfile);
      outfile << "\"\n";
    }
    break;
  }

  default:
    errs() << "WARNING: Variable of type " << *type << "\n";
    break;
  }

  return;
}


static string getID(Instruction &inst) {
  string id = "";
  if (MDNode *node = inst.getMetadata("corvette.inst.id")) {
    if (Value *value = node->getOperand(0)) {
      MDString *mdstring = cast<MDString>(value);
      id = mdstring->getString();
    }
  }
  else {
    errs() << "WARNING: Did not find metadata\n";
  }
  return id;
}


static bool isFPArray(Type *type) {
  if (ArrayType *array = dyn_cast<ArrayType>(type)) {
    type = array->getElementType();
    if (type->isFloatingPointTy()) {
      return true;
    }
    else {
      return isFPArray(type);
    }
  }
  else if (PointerType *pointer = dyn_cast<PointerType>(type)) {
    type = pointer->getElementType();
    if (type->isFloatingPointTy()) {
      return true;
    }
    else {
      return isFPArray(type);
    }
  }
  return false;
}


static bool isFPScalar(Type *type) {
  return type->isFloatingPointTy();
}

static bool isFPArith(Instruction *inst) {
  if (BinaryOperator::classof(inst)) {
    switch(inst->getOpcode()) {
      case Instruction::FAdd:
      case Instruction::FSub:
      case Instruction::FMul:
      case Instruction::FDiv: {
        return true;
      }

      default:
        return false;
    }
  }
  else if (FCmpInst::classof(inst)) {
    return true;
  }

  return false;
}


static Value* findAllocaForArg(Function &function, Argument* arg) {
  for(Function::iterator b = function.begin(), be = function.end(); b != be; b++) {
    for(BasicBlock::iterator i = b->begin(), ie = b->end(); i != ie; i++) {
      if (const StoreInst * const storeInst = dyn_cast<StoreInst>(i)) { 
        if (storeInst->getOperand(0) == arg) {
          return storeInst->getOperand(1);
        }
      }
    }
  }
  return NULL;
}


void CreateSearchFile::printGlobal(raw_fd_ostream &outfile, string name, Type *type) {
  if (first) {
    first = false;
  } else {
    outfile << ",\n";
  }

  outfile << "\t{\"globalVar\": {\n";
  outfile << "\t\t\"name\": \"" << name << "\",\n";
  outfile << "\t\t\"type\": ";
  printType(type, outfile);
  outfile << "\t}}";
  return;
}


void CreateSearchFile::findGlobalVariables(Module &module, raw_fd_ostream &outfile) {
  for (Module::global_iterator it = module.global_begin(); it != module.global_end(); it++) {
    Value *value = it;
    if (GlobalVariable *global = dyn_cast<GlobalVariable>(value)) {
      string name = global->getName();
      if (includedGlobalVars.find(name) != includedGlobalVars.end() && (name.find('.') == string::npos)) {
      	PointerType* pointerType = global->getType();
      	Type* elementType = pointerType->getElementType();
      	if (isFPScalar(elementType) || isFPArray(elementType)) {
          globalVars.insert(name);
    	    printGlobal(outfile, name, elementType);
      	}
      }
    }
  }
  return;
}


bool CreateSearchFile::doInitialization(Module &) {
  ifstream inFile(ExcludedFunctionsFileName.c_str());
  string name;

  // reading functions to exclude
  if (!inFile) {
    errs() << "Unable to open " << ExcludedFunctionsFileName << '\n';
    exit(1);
  }

  while(inFile >> name) {
    excludedFunctions.insert(name);
  }
  inFile.close();

  // reading functions to include
  inFile.open (IncludedFunctionsFileName.c_str(), ifstream::in);
  if (!inFile) {
    errs() << "Unable to open " << IncludedFunctionsFileName << '\n';
    exit(1);
  }

  while(inFile >> name) {
    includedFunctions.insert(name);
  }
  inFile.close();

  // reading global variables to include
  inFile.open (IncludedGlobalVarsFileName.c_str(), ifstream::in);
  if (!inFile) {
    errs() << "Unable to open " << IncludedGlobalVarsFileName << '\n';
    exit(1);
  }

  while(inFile >> name) {
    includedGlobalVars.insert(name);
  }
  inFile.close();

  // reading local variables to exclude
  // assuming unique names given by LLVM, so no need to include function name
  inFile.open (ExcludedLocalVarsFileName.c_str(), ifstream::in);
  while(inFile >> name) {
    excludedLocalVars.insert(name);
  }
  inFile.close();

  // populating function calls
  //functionCalls.insert("log");
  //functionCalls.insert("sqrt");
  functionCalls.insert("cos"); //FT
  functionCalls.insert("sin"); //FT
  functionCalls.insert("acos"); //funarc

  return false;
}


bool CreateSearchFile::runOnModule(Module &module) {
  doInitialization(module);

  string errorInfo;
  raw_fd_ostream outfile(FileName.c_str(), errorInfo);
  outfile << "{\"config\": [\n";

  first = true;

  findGlobalVariables(module, outfile);

  for(Module::iterator f = module.begin(), fe = module.end(); f != fe; f++) {
    string name = f->getName().str();
    if (!f->isDeclaration()  && (includedFunctions.find(name) != includedFunctions.end()) && (excludedFunctions.find(name) == excludedFunctions.end())) {
      runOnFunction(*f, outfile);
    }
  }
  outfile << "\n]}\n";
  return false;
}


void CreateSearchFile::printLocal(Function &function, raw_fd_ostream &outfile, string name, Type *type) {
  if (first) {
    first = false;
  } else {
    outfile << ",\n";
  }

  outfile << "\t{\"localVar\": {\n";

  if (Instruction *i = function.getEntryBlock().getTerminator()) {
    if (MDNode *node = i->getMetadata("dbg")) {
      DILocation loc(node);
      outfile << "\t\t\"file\": \"" << loc.getFilename() << "\",\n";
    }
  }

  outfile << "\t\t\"function\": \"" << function.getName() << "\",\n";
  outfile << "\t\t\"name\": \"" << name << "\",\n";
  outfile << "\t\t\"type\": ";
  printType(type, outfile);
  outfile << "\t}}";
  return;
}


void CreateSearchFile::findLocalVariables(Function &function, raw_fd_ostream &outfile) {
  const ValueSymbolTable& symbolTable = function.getValueSymbolTable();
  ValueSymbolTable::const_iterator it = symbolTable.begin();

  for(; it != symbolTable.end(); it++) {
    Value *value = it->second;
    string name = value->getName();

    if (excludedLocalVars.find(name) == excludedLocalVars.end() && (name.find('.') == string::npos)) {
      Type *type;
      if (AllocaInst* alloca = dyn_cast<AllocaInst>(value)) {
        type = alloca->getAllocatedType();

        if (isFPScalar(type) || isFPArray(type)) {
          printLocal(function, outfile, name, type);
          localVars.insert(name);
          allocaToVars[alloca] = name;
        }

      } else if (Argument* arg = dyn_cast<Argument>(value)) {
        type = arg->getType();

        if (isFPScalar(type) || isFPArray(type)) {
          printLocal(function, outfile, name, type);
          Value *allocaForArg;
          localVars.insert(name);
          allocaForArg = findAllocaForArg(function, arg);
          allocaToVars[allocaForArg] = name;
        }
      }
    }
  }
  return;
}


void CreateSearchFile::printOperator(Function &function, raw_fd_ostream &outfile, Instruction &op, vector<string> &operands) {
  if (first) {
    first = false;
  } else {
    outfile << ",\n";
  }

  outfile << "\t{\"op\": {\n";
  outfile << "\t\t\"id\": \"" << getID(op) << "\",\n";
  outfile << "\t\t\"function\": \"" << function.getName() << "\",\n";
  outfile << "\t\t\"name\": \"" << op.getOpcodeName() << "\",\n";
  outfile << "\t\t\"type\": [\"float\", \"double\", \"longdouble\"],\n";
  outfile << "\t\t\"operands\": ["; 
  if (operands.size() > 0) {
    outfile << "\"" << operands.at(0) << "\"";
  }
  size_t i;
  for (i=1; i < operands.size(); i++) {
    outfile << ", \"" << operands.at(i) << "\"";
  } 
  outfile << "]\n\t}}";
}


string CreateSearchFile::findOperandName(Value *value) {
  if (value->hasName()){
    if (localVars.count(value->getName()) != 0 || globalVars.count(value->getName()) != 0) {
      //outfile << value->getName();
      return value->getName();
    }
  }
  if (Instruction::classof(value)) {
    Instruction *i = dyn_cast<Instruction>(value);
    if (UnaryInstruction::classof(i)) {
      //outfile << *i ;
      if (AllocaInst *alloca = dyn_cast<AllocaInst>(value)) {
        return allocaToVars[alloca];
      } else {
        return findOperandName(i->getOperand(0));
      }
    } 
    else if (isFPArith(i)) {
      return getID(*i);
    }
    else if (CallInst::classof(i)) {
      /*if (CallInst *callInst = dyn_cast<CallInst>(i)) {
        Function *callee = callInst->getCalledFunction();
        if (callee) {
          return callee->getName();
        }
      }*/
    }
  }
  return "";
}

void CreateSearchFile::findOperators(Function &function, raw_fd_ostream &outfile) {
  for(Function::iterator b = function.begin(), be = function.end(); b != be; b++) {
    for(BasicBlock::iterator i = b->begin(), ie = b->end(); i != ie; i++) {

      if (isFPArith(i)) {
        // operator and its operands
        string operand0, operand1;
        operand0 = findOperandName(i->getOperand(0));
        operand1 = findOperandName(i->getOperand(1));
        vector<string> operands;
        if (!operand0.empty()) {
          operands.push_back(operand0);
        }
        if (!operand1.empty()) {
          operands.push_back(operand1);
        }
        printOperator(function, outfile, *i, operands);
      }
      
    }
  }
  return;
}


void CreateSearchFile::findFunctionCalls(Function &function, raw_fd_ostream &outfile) {

  for(Function::iterator b = function.begin(), be = function.end(); b != be; b++) {
    for(BasicBlock::iterator i = b->begin(), ie = b->end(); i != ie; i++) {

      if (CallInst *callInst = dyn_cast<CallInst>(i)) {
        Function *callee = callInst->getCalledFunction();

        if (callee) {
      	  string name = callee->getName();
      	  if (functionCalls.find(name) != functionCalls.end()) {
      	    if (first) {
      	      first = false;
      	    } else {
      	      outfile << ",\n";
      	    }

      	    outfile << "\t{\"call\": {\n";
      	    outfile << "\t\t\"id\": \"" << getID(*i) << "\",\n";
      	    outfile << "\t\t\"function\": \"" << function.getName() << "\",\n";
      	    outfile << "\t\t\"name\": \"" << name << "\",\n";
      	    outfile << "\t\t\"switch\": " << "[\"" << name << "f\",\"" << name << "\"]" << ",\n";
      	    outfile << "\t\t\"type\": " << "[[\"float\",\"float\"], [\"double\",\"double\"]]"<< "\n";
      	    outfile << "\t}}";
      	  }
        }
      }
    }
  }

  return;
}


void CreateSearchFile::runOnFunction(Function &function, raw_fd_ostream &outfile) {
  localVars.clear();
  allocaToVars.clear();

  findLocalVariables(function, outfile);

  if (ListOperators) {
    findOperators(function, outfile);
  }

  if (ListFunctions) {
    findFunctionCalls(function, outfile);
  }

  return;
}


void CreateSearchFile::getAnalysisUsage(AnalysisUsage &AU) const {
  AU.setPreservesAll();
  AU.addRequired<CreateIDBitcode>();
}


char CreateSearchFile::ID = 0;
static const RegisterPass<CreateSearchFile> registration("search-file", "Creating initial search file");

