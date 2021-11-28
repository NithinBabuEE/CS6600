# Assignment-1

## Problem
The objective of the assignment is to identify the cache block size as well as the associativity of the L1 cache. In order to find the block size and the associativity, you can exploit the fact that a cache hit takes low latency whereas a miss takes high latency. To find the latency, you can use suitable instruction from the ISA (for example, RDTSC instruction on Intel processors).

You can use any programming language to write your program. You must upload your program and a one page writeup explaining your results in detail.

## Instructions to run
Run the following commands  
  $taskset -c 1 gcc -O0 -mclflushopt associativity.c -o a1
  
  $taskset -c 1 ./a1

- time_taken.csv file will be genertaed containing access time data
