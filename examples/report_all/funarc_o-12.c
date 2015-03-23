#include "cov_log.h"
#include "cov_checker.h"
#include "cov_serializer.h"

#include <time.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

extern uint64_t current_time_ns(void);
#define INPUT_SIZE 10

double fun(double x)
{
  int i;
  double t1;
  float d1 = 1.0;

  t1 = x;

  for (i = 1; i <= 5; i++)
  {
    d1 = 2.0 * d1;
    t1 = t1 + sin (d1 * x) / d1;
  }

  return t1;
}

double arclength(int n)
{
  int i;
  double h, s1, t1, t2, dppi;

  t1 = -1.0;
  dppi = acos(t1);
  s1 = 0.0;
  t1 = 0.0;
  h = dppi / n;

  for (i = 1; i <= n; i++)
  {
    t2 = fun(i * h);
    s1 = s1 + sqrt(h * h + (t2 - t1) * (t2 - t1));
    t1 = t2;
  }

  return s1;
}

int main()
{
  uint64_t start, end;
  uint64_t diff = 0;

  int j;

  // variables for logging/checking
  long double outputs[INPUT_SIZE];
  long double threshold = 1e-4;

  // 0. read input from the file final_inputs
  int finputs[INPUT_SIZE] = {100, 200, 1000, 2000, 10000, 20000, 100000, 200000, 1000000, 2000000};

  // 1. compute and record results
  start = current_time_ns();
  for (j = 0; j < INPUT_SIZE; j++)
  {
    outputs[j] = arclength(finputs[j]);
  }
  end = current_time_ns();
  diff = (end-start);

  // 3. print score (diff) to a file
  FILE* file;
  file = fopen("score.cov", "a");
  fprintf(file, "o-12: %lu\n", diff);
  fclose(file);
  printf("o-12: %lu\n", diff);

  return 0;

}


