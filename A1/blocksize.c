//***********************************************************************
// CS6600 Assignment-1 (Jul-Nov 2021)
//
// File name: blocksize.c
//
// Team members: Karthikeyan R (EE18B015)
//               Nithin Babu   (EE18B021)
//
// Description: - Collect latency data by iteratively accessing bytes. 
//                This data can then be analysed to determine our cache 
//                blocksize.
//              - This program generates blocksize.csv containing 
//                access latency data which can be analysed later.
//
// Instructions: Run using the following commands
//               $taskset -c 1 gcc -O0 -mclflushopt blocksize.c -o a1
//               $taskset -c 1 ./a1
//***********************************************************************

#include<stdio.h>
#include<x86intrin.h>
#include<stdlib.h>

//
// PRAGMA noprefetch to disable prefetching
// This improves interpretability of latency data
//
#pragma noprefetch

#define CACHE_SIZE (1024 * 128)

//
// main function
//
int main(){

	int i;
	unsigned int entry_, exit_, latency;
	char * array;
	char val;
	FILE * fp;

	//
	// Dynamic memory allocation
	//
	array = (char *)malloc(CACHE_SIZE * sizeof(char));

	//
	// Opening a file to save collected latency data
	fp = fopen("blocksize.csv", "w");
	fprintf(fp, "Byte Number, Latency, Address\n");

	//
	// Disabling cache non-blocking to improve interpretability of latency data
	//
	_mm_sfence();

	//
	// Flushing cache blocks before accessing
	//	
	for(i = 0; i < CACHE_SIZE; i++){
		_mm_clflushopt(&array[i]);
	}
	_mm_sfence();

	//
	// Collecting latency data by iteratively accessing bytes
	//
	for(i = 0; i < 300; i++){
	
		//
		// Disabling cache non-blocking to improve interpretability of latency data
		//		
		_mm_lfence();
		entry_ = _rdtsc();
		_mm_lfence();
		val = array[i];
		_mm_lfence();
		exit_ = _rdtsc();
		_mm_lfence();

		//
		// Calculating and recording latency data
		//		
		latency = exit_ - entry_;
		fprintf(fp, "%d, %d, %p\n", i + 1, latency, (void *)(array + i));	
	}
	
	//
	// Closing the file
	//
	fclose(fp);
	return 0;
}
