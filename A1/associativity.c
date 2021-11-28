///***********************************************************************
// CS6600 Assignment-1 (Jul-Nov 2021)
//
// File name: associativity.c
//
// Team members: Karthikeyan R (EE18B015)
//               Nithin Babu   (EE18B021)
//
// Description: - Collect latency data by iteratively accessing blocks that
//                correspond to the same set of cache. This data can then 
//                be analysed to determine our cache associativity.
//              - This program generates associativity.csv containing 
//                access latency data which can be analysed later.
//
// Instructions: Run using the following commands
//               $taskset -c 1 gcc -O0 -mclflushopt associativity.c -o a1
//               $taskset -c 1 ./a1
//
//***********************************************************************

#include<stdio.h>
#include<x86intrin.h>
#include<stdint.h>
#include<stdlib.h>

//
// PRAGMA noprefetch to disable prefetching
// This improves interpretability of latency data
//
#pragma noprefetch

//
// Cache parameters which are needed to determine associativity
//
#define CACHE_SIZE (1024 * 128)
#define BLOCK_OFFSET_BITS 6      // Block offset found out using blocksize.c is used here
#define ASSOCIATIVITY 8          // Associativity is assumed and assumption is verified using collected data          
#define INDEX_BITS 8             // Number of index bits corresponding to our assumed associativity

//
// main function
//
int main(){

	long int i;
	char val;
	uint64_t entry_, exit_, latency, temp;
	char * array;
	char * access_location;
	FILE* fp;

	//
	// Dynamic memory allocation
	//
	array = (char *)malloc(CACHE_SIZE * sizeof(char));

	//
	// Opening a file to save collected latency data
	//
	fp = fopen("associativity.csv","w");
	fprintf(fp, "Latency, Address\n");

	//
	// Disabling cache non-blocking to improve interpretability of latency data
	//
	_mm_sfence();

	//
	// Flushing cache blocks before accessing
	//
	for(i = 1; i <= ASSOCIATIVITY + 2; i++){
		temp = ((uint64_t)(array)) >> (BLOCK_OFFSET_BITS + INDEX_BITS);
		temp += i;
		access_location = (char *)(temp << (BLOCK_OFFSET_BITS + INDEX_BITS));
		_mm_clflushopt(access_location);
	}
	_mm_sfence();

	//
	// Collecting latency data by iteratively accessing blocks that
	// correspond to the same set of cache
	//
	for(i = 1; i <= ASSOCIATIVITY + 2; i++){
	
		//
		// Computing the memory location to be accessed by changing only the tag bits
		//
		temp = ((uint64_t)(array)) >> (BLOCK_OFFSET_BITS + INDEX_BITS);
		temp += i;
		access_location = (char *)(temp << (BLOCK_OFFSET_BITS + INDEX_BITS));

		//
		// Disabling cache non-blocking to improve interpretability of latency data
		//
		_mm_lfence();
		entry_ = _rdtsc();
		_mm_lfence();
		val = *access_location;
		_mm_lfence();
		exit_ = _rdtsc();
		_mm_lfence();
		
		//
		// Calculating and recording latency data
		//
		latency = exit_ - entry_;
		fprintf(fp, "%ld, %p\n", latency, (void *)access_location);		
		printf("Byte No: %ld; Time Taken: %ld\n", i, latency);		
	}

	//
	// Closing the file
	//
	fclose(fp);
	return 0;
}
