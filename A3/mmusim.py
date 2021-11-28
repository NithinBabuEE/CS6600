#***********************************************************************
# CS6600 Assignment-3 (Jul-Nov 2021)
#
# File name: mmusim.py
#
# Team members: Karthikeyan R (EE18B015)
#               Nithin Babu   (EE18B021)
#
# Description: - MMU simulator
#
#***********************************************************************


#***********************************************************************
#
# Initializing all the necessary variables
#
#***********************************************************************
cr3_p1 = 1                  # cr3 for Process 1
cr3_p2 = 2                  # cr3 for Process 2

free_page_frame = []        # Free page frame list
dirty_page = []             # Dirty page list
lru_counter = []            # 4-bit saturation LRU counter for pages

p1 = {}                     # Dictionary for paging logic - Process 1
p2 = {}                     # Dictionary for paging logic - Process 2

page_hit  = 0               # Counter for any page hits
page_miss = 0               # Counter for any page misses
read_req  = 0               # Counter for read requests
write_req = 0               # Counter for write requests
p1_req    = 0               # Counter for Process 1 requests
p2_req    = 0               # Counter for Process 2 requests

dirty_page_evictions = 0    # Counter for any dirty page evictions
#***********************************************************************


#
# Function to update the LRU counters
#
def lru_update(page_frame):
    for i in range(768):
        if (i != page_frame) and (i not in free_page_frame):
            if lru_counter[i] < 15:
                lru_counter[i] = lru_counter[i] + 1

#
# Initialize free page frame list with all the pages
#
for i in range(768):
    free_page_frame.append(i)
    dirty_page.append(0)
    lru_counter.append(0)

#
# Loop through all the requests and impelement the pagic logic
# Opening the input file to get the intstructions 
#
with open("input.txt","r") as file:
    for line in file:
        pid, address, mode = line.split()
        
        #
        # Address is first converted to binary, and then page_table and pag_directory are derived from it
        #
        address = address[2:].zfill(8)
        address = bin(int(address, 16))[2:].zfill(32)
        page_directory, page_table = address[0:10], address[10:20]
        virtual_location = hex(int("".join([page_directory,page_table]), 2))

        #
        # Updating the read and write requests counter
        #
        if mode == 'r':
            read_req  = read_req + 1
        elif mode == 'w':
            write_req = write_req + 1

        #
        # Process id - 1
        #
        if pid == '1':
            p1_req += 1

            #
            # If page hit
            #
            if p1.get(virtual_location) != None:
                page_hit = page_hit + 1
                
                #
                # Update the dirty bit if its a write request
                #
                if mode == 'w':
                    dirty_page[p1[virtual_location]] = 1

                #
                # Update the LRU counters
                #
                lru_update(p1[virtual_location])

            #
            # If page miss
            #
            else:
                page_miss = page_miss + 1
                
                #
                # Map a free main memory page frame to the virtual address
                #
                if len(free_page_frame) != 0:
                    p1[virtual_location] = free_page_frame[0]
                    free_page_frame.pop(0)
                    
                    #
                    # Update the dirty bit if its a write request
                    #
                    if mode == 'w':
                        dirty_page[p1[virtual_location]] = 1

                    #
                    # Update the LRU counters
                    #
                    lru_update(p1[virtual_location])

                #
                # LRU eviction policy if no main memory page frame is free
                #
                else:
                    
                    #
                    # Page frame with the maximum LRU counter value is the victim
                    #
                    victim_page_frame = lru_counter.index(max(lru_counter))
                    p1.pop(list(p1.keys())[list(p1.values()).index(victim_page_frame)])

                    #
                    # Increment the dirty page eviction counter if the victim page is dirty
                    #
                    if dirty_page[victim_page_frame] == 1:
                         dirty_page_evictions = dirty_page_evictions + 1

                    dirty_page[victim_page_frame] = 0
                    lru_counter[victim_page_frame] = 0
                    p1[virtual_location] = victim_page_frame

                    if mode == 'w':
                        dirty_page[p1[virtual_location]] = 1

                    #
                    # Update the LRU counters
                    #
                    lru_update(p1[virtual_location])

        #
        # Process id - 2
        #
        elif pid == '2':
            p2_req += 1

            #
            # If page hit
            #
            if p2.get(virtual_location) != None:
                page_hit = page_hit + 1

                #
                # Update the dirty bit if its a write request
                #
                if mode == 'w':
                    dirty_page[p2[virtual_location]] = 1

                #
                # Update the LRU counters
                #
                lru_update(p2[virtual_location])
            
            #
            # If page miss
            #
            else:
                page_miss = page_miss + 1
                
                #
                # Map a free main memory page frame to the virtual address
                #
                if len(free_page_frame) != 0:
                    p2[virtual_location] = free_page_frame[0]
                    free_page_frame.pop(0)

                    #
                    # Update the dirty bit if its a write request
                    #
                    if mode == 'w':
                        dirty_page[p2[virtual_location]] = 1

                    #
                    # Update the LRU counters
                    #
                    lru_update(p2[virtual_location])

                else:

                    #
                    # Page frame with the maximum LRU counter value is the victim
                    #
                    victim_page_frame = lru_counter.index(max(lru_counter))
                    p2.pop(list(p2.keys())[list(p2.values()).index(victim_page_frame)])
                    
                    #
                    # Increment the dirty page eviction counter if the victim page is dirty
                    #
                    if dirty_page[victim_page_frame] == 1:
                         dirty_page_evictions = dirty_page_evictions + 1

                    dirty_page[victim_page_frame] = 0
                    lru_counter[victim_page_frame] = 0
                    p2[virtual_location] = victim_page_frame

                    if mode == 'w':
                        dirty_page[p2[virtual_location]] = 1

                    #
                    # Update the LRU counters
                    #
                    lru_update(p2[virtual_location])

total_req = write_req + read_req


#***********************************************************************
#
# Writing the statistics to output.txt
#
#***********************************************************************
outfile = open("output.txt", "w")
outfile.write("Total requests: " + str(total_req) + "\n")
outfile.write("Page miss rate: " + str(round(100*(page_miss/total_req), 2)) + "%\n")
outfile.write("Page hit rate: " + str(round(100*(page_hit/total_req), 2)) + "%\n")
outfile.write("Read requests: " + str(read_req) + "\n")
outfile.write("Write requests: " + str(write_req) + "\n")
outfile.write("PID: 1: " + str(p1_req) + " requests\n")
outfile.write("PID: 2: " + str(p2_req) + " requests\n")
outfile.write("Dirty page evictions: " + str(dirty_page_evictions) + "\n")
outfile.write("Space for paging logic: " + str(4*len(list(p1.keys()) + list(p2.keys()))) + " bytes\n")
outfile.close()

#*********************************************************************** END OF PROGRAM ***********************************************************************
