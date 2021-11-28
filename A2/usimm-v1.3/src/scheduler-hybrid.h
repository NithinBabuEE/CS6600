#ifndef __SCHEDULER_H__
#define __SCHEDULER_H__

// Hybrid-Row-Buffer Management Policy
#define THRESHOLD_HIGH_HYBRID 8
#define THRESHOLD_LOW_HYBRID 3
#define INITIAL_VALUE_HYBRID 5
#define OPEN_POLICY 0
#define CLOSE_POLICY 1


// Counter to take care of the Hybrid-Row-Buffer Management Policy
int counter_hybrid[MAX_NUM_CHANNELS];
int current_page_policy[MAX_NUM_CHANNELS];
int previous_row[MAX_NUM_CHANNELS];

void init_scheduler_vars(); //called from main
void scheduler_stats(); //called from main
void schedule(int); // scheduler function called every cycle

#endif //__SCHEDULER_H__

