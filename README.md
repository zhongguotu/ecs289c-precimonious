# ECS289C Precimonious

## Installation Instruction
### Requirement
* Scons build system. 
* LLVM 3.0. When building LLVM, use --enable-shared flag.
```
../llvm/configure --enable-shared
make
```
* Set the following environment variable.
```
CORVETTE_PATH=path/to/precimonious
LLVM_COMPILER=clang
LD_LIBRARY_PATH=path/to/llvm/Release/lib
PATH=$PATH:path/to/llvm/Release/bin
```

### Build Instruction
After setting up the requirement, you can build Precimonious LLVM Passes by

```
cd src
scons -Uc
scons -U
scons -U test // to run the regression test
```

## Running the Example
* Go inside _examples_ folder, take a look at the file funarc.c. This is the target program that we will tune precision on.

* Compile the program:
```
./compile.sh
```
This will create a bitcode file called funarc.bc.

* Generate search configuration files:
```
./config.sh
```
This will create search_funarc.json and config_funarc.json.

* Run Precimonious algorithm:
```
./search.sh
```
This will create a file called _spec.cov_, which contains the output and the error threshold in hex format.
Each iteration of the algorithm will create a valid or invalid configuration file, and update files _sat.cov_, _score.cov_, _log.cov_ and _log.dd_.
Finally, this will create two files: _dd2_diff_funarc.bc.json_ and _dd2_valid_funarc.bc.json_, if a faster and lower-precision type configuration of the program is found. 


