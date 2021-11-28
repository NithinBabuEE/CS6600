#***********************************************************************
# CS6600 Assignment-6 (Jul-Nov 2021)
#
# File name: cache_sim.py
#
# Team members: Karthikeyan R (EE18B015)
#               Nithin Babu   (EE18B021)
#
# Description: - Cache simulator
#                This program simulates a cache.
#
# Instructions to run: python cache_sim.py
#
#***********************************************************************

import math as m
import random as r
from os import read, write 

#***********************************************************************
#
# Importing the cache parameters from 'input.txt'
#
#***********************************************************************
input_file = open('input.txt', 'r')
cache_size = int(input_file.readline().split()[0])
block_size = int(input_file.readline().split()[0])
associativity = int(input_file.readline().split()[0])
replacement_policy = int(input_file.readline().split()[0])
filename = input_file.readline().split()[0]

#***********************************************************************
#
# Compute cache dimensions using the input paramters
#
#***********************************************************************
no_of_blocks = int(cache_size / block_size)
if(associativity == 0):  # Fully associative
    no_of_sets = 1
    blocks_per_set = no_of_blocks
else:
    no_of_sets = int(no_of_blocks/ associativity)
    blocks_per_set = associativity
block_width = int(m.log(block_size, 2))
set_width = int(m.log(no_of_sets, 2))

#***********************************************************************
#
# Data structure for cache block
#
#***********************************************************************
class cache_block:
    tag   = 0
    valid = 0
    dirty = 0

#***********************************************************************
#
# Functions required for block replacement policy
#
#***********************************************************************

#
# Function to update the replacement policy paramters
# on every cache access
#
def rp_update(set_index, block_index):
    global cache, lru_list, plru_list, blocks_per_set, replacement_policy
    if(replacement_policy == 1):
        lru_value = lru_list[set_index][block_index]
        for i in range(blocks_per_set):
            if(lru_list[set_index][i] < lru_value):
                lru_list[set_index][i] = lru_list[set_index][i] + 1
        lru_list[set_index][block_index] = 0

    elif(replacement_policy == 2):
        plru_list[set_index][block_index] = 1
        if(sum(plru_list[set_index]) == blocks_per_set):
            for i in range(blocks_per_set):
                if(i != block_index):
                    plru_list[set_index][i] = 0

#
# Function to evict and replace a cache block
#
def block_replace(set_index, tag, instr_type):
    global dirty_evict, cache, lru_list, plru_list, blocks_per_set, replacement_policy
    temp_lru_value = -1; temp_lru_index = -1;
    eviction_done = 0

    #
    # LRU replacement policy
    #
    if(replacement_policy == 1):

        #
        # Prioritizing dirty blocks first for LRU replacement
        #
        for i in range(blocks_per_set):
            if(cache[set_index][i].dirty == 1):
                if(temp_lru_value < lru_list[set_index][i]):
                    temp_lru_value = lru_list[set_index][i]
                    temp_lru_index = i

        if(temp_lru_value != -1):
            eviction_done = 1
            dirty_evict = dirty_evict + 1
            cache[set_index][temp_lru_index].tag = tag
            if(instr_type == 'w'):
                cache[set_index][temp_lru_index].dirty = 1
            elif(instr_type == 'r'):
                cache[set_index][temp_lru_index].dirty = 0
            rp_update(set_index, temp_lru_index)
        
        #
        # If there are no dirty blocks
        #
        if(eviction_done == 0):
            for i in range(blocks_per_set):
                if(lru_list[set_index][i] == blocks_per_set-1):
                    cache[set_index][i].tag = tag
                    if(instr_type == 'w'):
                        cache[set_index][i].dirty = 1
                    elif(instr_type == 'r'):
                        cache[set_index][i].dirty = 0
                    rp_update(set_index, i)
                    break
    
    #
    # Pseudo-LRU replacement policy
    #
    elif(replacement_policy == 2):

        #
        # Prioritizing dirty blocks first for Pseudo-LRU replacement
        #
        for i in range(blocks_per_set):
            if(plru_list[set_index][i] == 0):
                if(cache[set_index][i].dirty == 1):
                    dirty_evict = dirty_evict + 1
                    cache[set_index][i].tag = tag
                    if(instr_type == 'w'):
                        cache[set_index][i].dirty = 1
                    elif(instr_type == 'r'):
                        cache[set_index][i].dirty = 0
                    rp_update(set_index, i)
                    eviction_done = 1
                    break
        
        #
        # If there are no dirty blocks
        #
        if(eviction_done == 0):
            for i in range(blocks_per_set):
                if(plru_list[set_index][i] == 0):
                    cache[set_index][i].tag = tag
                    if(instr_type == 'w'):
                        cache[set_index][i].dirty = 1
                    elif(instr_type == 'r'):
                        cache[set_index][i].dirty = 0
                    rp_update(set_index, i)
                    break

    #
    # Random replacement policy
    #
    elif(replacement_policy == 0):

        #
        # Prioritizing dirty blocks first for random replacement
        #
        for i in range(blocks_per_set):
            if(cache[set_index][i].dirty == 1):
                dirty_evict = dirty_evict + 1
                cache[set_index][i].tag = tag
                if(instr_type == 'w'):
                    cache[set_index][i].dirty = 1
                elif(instr_type == 'r'):
                    cache[set_index][i].dirty = 0
                eviction_done = 1
                break

        #
        # If there are no dirty blocks
        #
        if(eviction_done == 0):
            eviction_index = r.randrange(0, blocks_per_set, 1)
            if(cache[set_index][eviction_index].dirty == 1):
                dirty_evict = dirty_evict + 1
            cache[set_index][eviction_index].tag = tag
            if(instr_type == 'w'):
                cache[set_index][eviction_index].dirty = 1
            elif(instr_type == 'r'):
                cache[set_index][eviction_index].dirty = 0                      

#***********************************************************************
#
# Initialize the cache
#
#***********************************************************************
cache = []
lru_list = []; plru_list = []
comp_miss_set = {}

for i in range(no_of_sets):
    cache_set = []; rp_set = []
    for j in range(blocks_per_set):
        cache_set.append(cache_block())
        if(replacement_policy == 1):
            rp_set.append(j)
        elif(replacement_policy == 2):
            rp_set.append(0)
    cache.append(cache_set)
    if(replacement_policy == 1):
        lru_list.append(rp_set)
    elif(replacement_policy == 2):
        plru_list.append(rp_set)

#***********************************************************************
#
# Declare variables to keep track of output data
#
#***********************************************************************
cache_access = 0; read_access = 0; write_access = 0
cache_miss = 0; compulsory_miss = 0; capacity_miss = 0; conflict_miss = 0
read_miss = 0; write_miss = 0; dirty_evict = 0

#***********************************************************************
#
# Open the trace file and loop through it line by line
#
#***********************************************************************
file = open(filename, 'r')
while(1):
    flag_hit = 0; flag_comp_miss = 0; flag_conflict_miss = 0; flag_empty_set = 0

    #
    # Read an instruction and bread down the address into tag & index
    #
    instr = file.readline()
    if(instr == ''):
        print('Cache simulation complete!')
        print('Please find the results in output.txt')
        break
    address, instr_type = instr.split()
    address = address[2:].zfill(8)
    address = bin(int(address, 16))[2:].zfill(32)
    address = "".join(reversed(address))
    tag, set_index = int(address[block_width + set_width:], 2), int(address[block_width:block_width + set_width], 2)
    address_entry = str(tag) + str(set_index)
    
    cache_access = cache_access + 1
    if instr_type == 'r':
        read_access = read_access + 1
    elif instr_type == 'w':
        write_access = write_access + 1 

    #
    # Cache hit
    #
    for i in range(blocks_per_set):
        if(cache[set_index][i].tag == tag):
            flag_hit = 1
            rp_update(set_index, i)
            if instr_type == 'w':
                cache[set_index][i].dirty = 1
            elif instr_type == 'r':
                cache[set_index][i].dirty = 0 
            break
    
    #
    # Cache miss
    #
    if(flag_hit == 0):
        if instr_type == 'w':
            write_miss = write_miss + 1
        elif instr_type == 'r': 
            read_miss = read_miss + 1

        #
        # Check for compulsory cache miss
        #
        initial_len = len(comp_miss_set)
        comp_miss_list = list(comp_miss_set)
        comp_miss_list.append(address_entry)
        comp_miss_set = set(comp_miss_list)
        final_len = len(comp_miss_set)
        if(initial_len != final_len):
            flag_comp_miss = 1
            compulsory_miss = compulsory_miss + 1

        for i in range(blocks_per_set):
            if(cache[set_index][i].valid == 0):
                flag_empty_set = 1
                cache[set_index][i].tag = tag
                cache[set_index][i].valid = 1
                rp_update(set_index, i)
                if instr_type == 'w':
                    cache[set_index][i].dirty = 1
                elif instr_type == 'r':
                    cache[set_index][i].dirty = 0 
                break
        
        if(flag_comp_miss == 1):
            if(flag_empty_set == 0):
                block_replace(set_index, tag, instr_type)

        else:

            #
            # Check for conflict cache miss
            #
            for set in cache:
                for block in set:
                    if(block.valid == 0):
                        flag_conflict_miss = 1
                        conflict_miss = conflict_miss + 1
                        break
                break

            #
            # Capacity miss
            #
            if(flag_conflict_miss == 0):
                capacity_miss = capacity_miss + 1
            
            #
            # Block replacement policy incase of conflict miss
            # and capacity miss
            #
            block_replace(set_index, tag, instr_type)
            
cache_miss = read_miss + write_miss
file.close()

#***********************************************************************
#
# Writing the statistics to output.txt
#
#***********************************************************************
rp_name_list = ['Random Replacement','LRU Replacement','Pseudo LRU Replacement']
cache_type_name_list = ['Fully associative cache','Direct-mapped cache','Set-associative cache']

outfile = open("output.txt", "w")
outfile.write("Cache Size          : " + str(cache_size) + "\n")
outfile.write("Block Size          : " + str(block_size) + "\n")
if(associativity <=1):
    outfile.write("Type of Cache       : " + cache_type_name_list[associativity] + "\n")
else:
    outfile.write("Type of Cache       : " + cache_type_name_list[2] + "\n")
outfile.write("Replacement Policy  : " + rp_name_list[replacement_policy] + "\n")
outfile.write("Cache accesses      : " + str(cache_access) + "\n")
outfile.write("Read accesses       : " + str(read_access) + "\n")
outfile.write("Write accesses      : " + str(write_access) + "\n")
outfile.write("Cache misses        : " + str(cache_miss) + "\n")
outfile.write("Compulsory misses   : " + str(compulsory_miss) + "\n")
outfile.write("Capacity misses     : " + str(capacity_miss) + "\n")
outfile.write("Conflict misses     : " + str(conflict_miss) + "\n")
outfile.write("Read misses         : " + str(read_miss) + "\n")
outfile.write("Write misses        : " + str(write_miss) + "\n")
outfile.write("Dirty Blocks Evicted: " + str(dirty_evict) + "\n")
outfile.close()

#*********************************************************************** END OF PROGRAM ***********************************************************************

                





          
    





