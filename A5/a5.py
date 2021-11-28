#***********************************************************************
# CS6600 Assignment-5 (Jul-Nov 2021)
#
# File name: a5.py
#
# Team members: Karthikeyan R (EE18B015)
#               Nithin Babu   (EE18B021)
#
# Description: - Dynamic execution core
#                This program simulates a superscalar core by running
#                instructions from the file "Ins.txt". It prints
#                out the total number of CPU clock cycles elapsed to
#                complete the execution of all the instructions.
#
# Instructions to run: python a5.py
#
#***********************************************************************

import copy

#***********************************************************************
#
# Importing the processor parameters from the configuration file
#
#***********************************************************************
param = []
with open("config.txt", "r") as file:
    data = file.read().split("\n")
    for entry in data:
        param.append(int(entry.split(" ")[1]))

#***********************************************************************
#
# Initializing all the necessary variables
#
#***********************************************************************
issue_width    = param[0]
add_latency    = param[1]
mul_latency    = param[2]
div_latency    = param[3]
ls_latency     = param[4]
cache_latency  = param[5]
mem_op_latency = ls_latency + cache_latency
size_add_rs    = param[6]
size_mul_rs    = param[7]
size_div_rs    = param[8]
size_mem_op_rs = param[9]
size_rob = param[10]

#***********************************************************************
#
# Declaring all the processor list and dictionary structures
# 
#***********************************************************************

# Dictionary for all the opcodes
opcode_dict = {'0001':'add', 
               '0010':'add', 
               '0011':'mul',
               '0100':'div',
               '0101':'load', 
               '0110':'store'}

# Opening 'Ins.txt' file containing the instructions to be executed
file = open('Ins.txt', 'r')
cpu_clock = 0; pc = 0

# rob is a list of dicitonary that contains pc, finished, rd.
rob = []; rob_temp = []

# Dispatch buffer is a list of dictionary with elements: opcode, rd, rs1, rs2, pc
dispatch_buffer = []; dispatch_buffer_temp = []

# ARF, RRF dictionary declaration
arf = {'r0' :{'busy': 0, 'tag': 0},
       'r1' :{'busy': 0, 'tag': 0},
       'r2' :{'busy': 0, 'tag': 0},
       'r3' :{'busy': 0, 'tag': 0},
       'r4' :{'busy': 0, 'tag': 0},
       'r5' :{'busy': 0, 'tag': 0},
       'r6' :{'busy': 0, 'tag': 0},
       'r7' :{'busy': 0, 'tag': 0},
       'r8' :{'busy': 0, 'tag': 0},
       'r9' :{'busy': 0, 'tag': 0},
       'r10':{'busy': 0, 'tag': 0},
       'r11':{'busy': 0, 'tag': 0},
       'r12':{'busy': 0, 'tag': 0},
       'r13':{'busy': 0, 'tag': 0},
       'r14':{'busy': 0, 'tag': 0},
       'r15':{'busy': 0, 'tag': 0},
       }

arf_temp = {'r0' :{'busy': 0, 'tag': 0},
            'r1' :{'busy': 0, 'tag': 0},
            'r2' :{'busy': 0, 'tag': 0},
            'r3' :{'busy': 0, 'tag': 0},
            'r4' :{'busy': 0, 'tag': 0},
            'r5' :{'busy': 0, 'tag': 0},
            'r6' :{'busy': 0, 'tag': 0},
            'r7' :{'busy': 0, 'tag': 0},
            'r8' :{'busy': 0, 'tag': 0},
            'r9' :{'busy': 0, 'tag': 0},
            'r10':{'busy': 0, 'tag': 0},
            'r11':{'busy': 0, 'tag': 0},
            'r12':{'busy': 0, 'tag': 0},
            'r13':{'busy': 0, 'tag': 0},
            'r14':{'busy': 0, 'tag': 0},
            'r15':{'busy': 0, 'tag': 0},
            }

rrf = {'r16':{'busy': 0, 'valid': 0},
       'r17':{'busy': 0, 'valid': 0},
       'r18':{'busy': 0, 'valid': 0},
       'r19':{'busy': 0, 'valid': 0},
       'r20':{'busy': 0, 'valid': 0},
       'r21':{'busy': 0, 'valid': 0},
       'r22':{'busy': 0, 'valid': 0},
       'r23':{'busy': 0, 'valid': 0},
       'r24':{'busy': 0, 'valid': 0},
       'r25':{'busy': 0, 'valid': 0},
       'r26':{'busy': 0, 'valid': 0},
       'r27':{'busy': 0, 'valid': 0},
       'r28':{'busy': 0, 'valid': 0},
       'r29':{'busy': 0, 'valid': 0},
       'r30':{'busy': 0, 'valid': 0},
       'r31':{'busy': 0, 'valid': 0},
       }

rrf_temp = {'r16':{'busy': 0, 'valid': 0},
            'r17':{'busy': 0, 'valid': 0},
            'r18':{'busy': 0, 'valid': 0},
            'r19':{'busy': 0, 'valid': 0},
            'r20':{'busy': 0, 'valid': 0},
            'r21':{'busy': 0, 'valid': 0},
            'r22':{'busy': 0, 'valid': 0},
            'r23':{'busy': 0, 'valid': 0},
            'r24':{'busy': 0, 'valid': 0},
            'r25':{'busy': 0, 'valid': 0},
            'r26':{'busy': 0, 'valid': 0},
            'r27':{'busy': 0, 'valid': 0},
            'r28':{'busy': 0, 'valid': 0},
            'r29':{'busy': 0, 'valid': 0},
            'r30':{'busy': 0, 'valid': 0},
            'r31':{'busy': 0, 'valid': 0},
            }

#***********************************************************************
#
# Declaration of reservation stations for all functional units
# 
#***********************************************************************

# Addition/ Subtraction 
add_rs = []; add_rs_temp = []; 
issue_add_rs = {'busy': 0, 'op1': 0, 'op2': 0, 'rd': 0, 'cycles_left': 0, 'pc': 0 }
for i in range(size_add_rs):
    add_rs.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})
    add_rs_temp.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})

# Multiplication
mul_rs = []; mul_rs_temp = []
issue_mul_rs = {'busy': 0, 'op1': 0, 'op2': 0, 'rd': 0, 'cycles_left': 0, 'pc': 0}
for i in range(size_mul_rs):
    mul_rs.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})
    mul_rs_temp.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})

# Division
div_rs = []; div_rs_temp = []
issue_div_rs = {'busy': 0, 'op1': 0, 'op2': 0, 'rd': 0, 'cycles_left': 0, 'pc': 0}
for i in range(size_div_rs):
    div_rs.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})
    div_rs_temp.append({'busy': 0, 'op1': 0, 'valid1': 0, 'op2': 0, 'valid2': 0, 'rd': 0, 'pc': 0})

# Memory Operation
mem_op_rs = []; mem_op_rs_temp = []
issue_mem_op_rs = {'opcode': 0,'busy': 0, 'op1': 0, 'rd': 0, 'cycles_left': 0, 'pc': 0}
for i in range(size_mem_op_rs):
    mem_op_rs.append({'opcode': 0,'busy': 0, 'op1': 0, 'valid1': 0, 'valid2': 0, 'rd': 0, 'pc': 0})
    mem_op_rs_temp.append({'opcode': 0,'busy': 0, 'op1': 0, 'valid1': 0, 'valid2': 0, 'rd': 0, 'pc': 0})

#***********************************************************************
#
# Function: read_file() 
# This will update dispatch_buffer_temp and rob_temp with newly added 
# intructions while keeping track of the program counter.
# 
#***********************************************************************
def read_file():
    global pc
    global dispatch_buffer_temp, rob_temp
    
    while(len(dispatch_buffer_temp) < issue_width):

        instr = file.readline().split(" ")
        
        if(instr[0] == ''):
            break
       
        dispatch_buffer_temp.append({'opcode': opcode_dict[instr[0]], 
                                     'rd': 'r' + str(int(instr[1],2)), 
                                     'rs1': 'r' + str(int(instr[2],2)), 
                                     'rs2': 'r' + str(int(instr[3],2)), 
                                     'pc': pc})
        rob_temp.append({'opcode'  : opcode_dict[instr[0]],
                         'finished': 0, 
                         'rd': 'r' + str(int(instr[1],2)), 
                         'pc': pc })

        pc = pc + 1

#***********************************************************************
#
# Function: source_read(rs) 
# This function returns the source of an operand in reservation station
# Returns (source register, valid bit)
# e.g. rteurns ('r2', 1)
#
#***********************************************************************       
def source_read(rs):

    reg_num = int(rs[1:])
    if(reg_num <= 15):
        if(arf[rs]['busy'] == 0):
            return rs, 1

        else:
            rename_reg = arf[rs]['tag']
            if(rrf[rename_reg]['valid'] == 1):
                return rename_reg, 1 
            else:
                return rename_reg, 0
    else:
        if(rrf[rs]['valid'] == 1):
            return rs, 1 
        else:
            return rs, 0

#***********************************************************************
#
# Function: rotate(l, n) 
# This function is used to left shift a list, to be used in 
# reservation station
#
#***********************************************************************   
def rotate(l, n):
    return l[n:] + l[:n]

#***********************************************************************
#
# Start of the processor execution loop
#
#*********************************************************************** 
while(len(rob) != 0 or cpu_clock == 0):

    # Updation of cpu clock cycle count
    if(len(rob) != 0):
        cpu_clock = cpu_clock + 1

    # Reading the instructions   
    read_file()
          
    # Register Renaming and dispatching into relevant reservation station
    for instr in dispatch_buffer:
        opcode = instr['opcode']
        rd = instr['rd']; rs1 = instr['rs1']; rs2 = instr['rs2']
        for reg in rrf:
            if(rrf[reg]['busy'] == 0 and rrf_temp[reg]['busy'] == 0):
                if(opcode != 'store'):
                    arf_temp[rd]['tag'] = reg
                    arf_temp[rd]['busy'] = 1
                    rrf_temp[reg]['busy'] = 1   

                if(instr['opcode'] == 'add'):
                    for i in range(size_add_rs):
                        if(add_rs[i]['busy'] == 0 and add_rs_temp[i]['busy'] == 0):
                            add_rs_temp[i]['op1'], add_rs_temp[i]['valid1'] = source_read(rs1)
                            add_rs_temp[i]['op2'], add_rs_temp[i]['valid2'] = source_read(rs2)
                            add_rs_temp[i]['busy'] = 1
                            add_rs_temp[i]['rd'] = reg
                            add_rs_temp[i]['pc'] = instr['pc']
                            dispatch_buffer_temp.remove(instr)
                            break

                elif(instr['opcode'] == 'mul'):
                    for i in range(size_mul_rs):
                        if(mul_rs[i]['busy'] == 0 and mul_rs_temp[i]['busy'] == 0):
                            mul_rs_temp[i]['op1'], mul_rs_temp[i]['valid1'] = source_read(rs1)
                            mul_rs_temp[i]['op2'], mul_rs_temp[i]['valid2'] = source_read(rs2)
                            mul_rs_temp[i]['busy'] = 1
                            mul_rs_temp[i]['rd'] = reg
                            mul_rs_temp[i]['pc'] = instr['pc']
                            dispatch_buffer_temp.remove(instr)
                            break

                elif(instr['opcode'] == 'div'):
                    for i in range(size_div_rs):
                        if(div_rs[i]['busy'] == 0 and div_rs_temp[i]['busy'] == 0):
                            div_rs_temp[i]['op1'], div_rs_temp[i]['valid1'] = source_read(rs1)
                            div_rs_temp[i]['op2'], div_rs_temp[i]['valid2'] = source_read(rs2)
                            div_rs_temp[i]['busy'] = 1
                            div_rs_temp[i]['rd'] = reg
                            div_rs_temp[i]['pc'] = instr['pc']
                            dispatch_buffer_temp.remove(instr)
                            break
                
                elif(instr['opcode'] == 'load' or instr['opcode'] == 'store'):
                    for i in range(size_mem_op_rs):
                        if(mem_op_rs[i]['busy'] == 0 and mem_op_rs_temp[i]['busy'] == 0):
                            mem_op_rs_temp[i]['opcode'] = instr['opcode']
                            mem_op_rs_temp[i]['op1'], mem_op_rs_temp[i]['valid1'] = source_read(rs1)
                            mem_op_rs_temp[i]['busy'] = 1
                            if(opcode == 'load'):
                                mem_op_rs_temp[i]['rd'] = reg
                            else:
                                mem_op_rs_temp[i]['rd'] = rd
                            mem_op_rs_temp[i]['pc'] = instr['pc']
                            dispatch_buffer_temp.remove(instr)
                            
                            break                  
                break
                
    # Issuing from the reservation into the issue register present in each functional unit

    # Addition/ Subtraction module
    for i in range(size_add_rs):
        if(add_rs_temp[i]['busy'] == 1):
            if (add_rs_temp[i]['valid1'] != 1):
                add_rs_temp[i]['op1'], add_rs_temp[i]['valid1'] = source_read(add_rs_temp[i]['op1'])   
            if (add_rs_temp[i]['valid2'] != 1):
                add_rs_temp[i]['op2'], add_rs_temp[i]['valid2'] = source_read(add_rs_temp[i]['op2'])

            if(add_rs_temp[i]['valid1'] & add_rs_temp[i]['valid2'] == 1):
                if(issue_add_rs['busy'] == 0):
                    issue_add_rs['busy'] = 1
                    issue_add_rs['op1'] = add_rs_temp[i]['op1']
                    issue_add_rs['op2'] = add_rs_temp[i]['op2']
                    issue_add_rs['rd'] = add_rs_temp[i]['rd']
                    issue_add_rs['pc'] = add_rs_temp[i]['pc']
                    issue_add_rs['cycles_left'] = add_latency
                    add_rs_temp[i]['busy'] = 0
                    add_rs_temp = rotate(add_rs_temp, 1) 
                    break

    # Multiply module
    for i in range(size_mul_rs):
        if(mul_rs_temp[i]['busy'] == 1):
            if (mul_rs_temp[i]['valid1'] != 1):
                mul_rs_temp[i]['op1'], mul_rs_temp[i]['valid1'] = source_read(mul_rs_temp[i]['op1'])   
            if (mul_rs_temp[i]['valid2'] != 1):
                mul_rs_temp[i]['op2'], mul_rs_temp[i]['valid2'] = source_read(mul_rs_temp[i]['op2'])

            if(mul_rs_temp[i]['valid1'] & mul_rs_temp[i]['valid2'] == 1):
                if(issue_mul_rs['busy'] == 0):
                    issue_mul_rs['busy'] = 1
                    issue_mul_rs['op1'] = mul_rs_temp[i]['op1']
                    issue_mul_rs['op2'] = mul_rs_temp[i]['op2']
                    issue_mul_rs['rd'] = mul_rs_temp[i]['rd']
                    issue_mul_rs['pc'] = mul_rs_temp[i]['pc']
                    issue_mul_rs['cycles_left'] = mul_latency
                    mul_rs_temp[i]['busy'] = 0
                    mul_rs_temp = rotate(mul_rs_temp, 1) 
                    break

    # Divide Module        
    for i in range(size_div_rs):
        if(div_rs_temp[i]['busy'] == 1):
            if (div_rs_temp[i]['valid1'] != 1):
                div_rs_temp[i]['op1'], div_rs_temp[i]['valid1'] = source_read(div_rs_temp[i]['op1'])   
            if (div_rs_temp[i]['valid2'] != 1):
                div_rs_temp[i]['op2'], div_rs_temp[i]['valid2'] = source_read(div_rs_temp[i]['op2'])

            if(div_rs_temp[i]['valid1'] & div_rs_temp[i]['valid2'] == 1):
                if(issue_div_rs['busy'] == 0):
                    issue_div_rs['busy'] = 1
                    issue_div_rs['op1'] = div_rs_temp[i]['op1']
                    issue_div_rs['op2'] = div_rs_temp[i]['op2']
                    issue_div_rs['rd'] = div_rs_temp[i]['rd']
                    issue_div_rs['pc'] = div_rs_temp[i]['pc']
                    issue_div_rs['cycles_left'] = div_latency
                    div_rs_temp[i]['busy'] = 0
                    div_rs_temp = rotate(div_rs_temp, 1) 
                    break
                
    # Load/ Store module
    for i in range(size_mem_op_rs):
        if(mem_op_rs_temp[i]['busy'] == 1):
            if (mem_op_rs_temp[i]['valid1'] != 1):
                mem_op_rs_temp[i]['op1'], mem_op_rs_temp[i]['valid1'] = source_read(mem_op_rs_temp[i]['op1'])   
            if(mem_op_rs_temp[i]['opcode'] == 'load'):    
                if(mem_op_rs_temp[i]['valid1'] == 1):     
                    if(issue_mem_op_rs['busy'] == 0):
                        issue_mem_op_rs['opcode'] = 'load'
                        issue_mem_op_rs['busy'] = 1
                        issue_mem_op_rs['op1'] = mem_op_rs_temp[i]['op1']
                        issue_mem_op_rs['rd'] = mem_op_rs_temp[i]['rd']
                        issue_mem_op_rs['pc'] = mem_op_rs_temp[i]['pc']
                        issue_mem_op_rs['cycles_left'] = mem_op_latency
                        mem_op_rs_temp[i]['busy'] = 0
                        mem_op_rs_temp = rotate(mem_op_rs_temp, 1) 
                        break
            else:
                if(rrf[arf[mem_op_rs_temp[i]['rd']]['tag']]['valid'] == 1):
                    if(mem_op_rs_temp[i]['valid1'] == 1):     
                        if(issue_mem_op_rs['busy'] == 0):
                            issue_mem_op_rs['opcode'] = 'store'
                            issue_mem_op_rs['busy'] = 1
                            issue_mem_op_rs['op1'] = mem_op_rs_temp[i]['op1']
                            issue_mem_op_rs['rd'] = mem_op_rs_temp[i]['rd']
                            issue_mem_op_rs['pc'] = mem_op_rs_temp[i]['pc']
                            issue_mem_op_rs['cycles_left'] = mem_op_latency
                            mem_op_rs_temp[i]['busy'] = 0
                            mem_op_rs_temp = rotate(mem_op_rs_temp, 1) 
                            break

                

            

    # Simulating the functional unit

    # Addition/ Subtraction
    if (issue_add_rs['busy'] == 1):
        issue_add_rs['cycles_left'] = issue_add_rs['cycles_left'] - 1

        if (issue_add_rs['cycles_left'] == 0):
            issue_add_rs['busy'] = 0
            rrf_temp[issue_add_rs['rd']]['valid'] = 1
            for i in range(len(rob)):
                if(rob[i]['pc'] == issue_add_rs['pc']):
                    rob_temp[i]['finished'] = 1
    # Multiply
    if (issue_mul_rs['busy'] == 1):
        issue_mul_rs['cycles_left'] = issue_mul_rs['cycles_left'] - 1

        if (issue_mul_rs['cycles_left'] == 0):
            issue_mul_rs['busy'] = 0
            rrf_temp[issue_mul_rs['rd']]['valid'] = 1
            for i in range(len(rob)):
                if(rob[i]['pc'] == issue_mul_rs['pc']):
                    rob_temp[i]['finished'] = 1

    # Divide
    if (issue_div_rs['busy'] == 1):
        issue_div_rs['cycles_left'] = issue_div_rs['cycles_left'] - 1

        if (issue_div_rs['cycles_left'] == 0):
            issue_div_rs['busy'] = 0
            rrf_temp[issue_div_rs['rd']]['valid'] = 1
            for i in range(len(rob)):
                if(rob[i]['pc'] == issue_div_rs['pc']):
                    rob_temp[i]['finished'] = 1

    # Load/ Store
    if (issue_mem_op_rs['busy'] == 1):
        issue_mem_op_rs['cycles_left'] = issue_mem_op_rs['cycles_left'] - 1

        if (issue_mem_op_rs['cycles_left'] == 0):
            issue_mem_op_rs['busy'] = 0
            if(issue_mem_op_rs['opcode'] == 'load'):
                rrf_temp[issue_mem_op_rs['rd']]['valid'] = 1
            for i in range(len(rob)):
                if(rob[i]['pc'] == issue_mem_op_rs['pc']):
                    rob_temp[i]['finished'] = 1
                    

    # Register Updation
    dispatch_buffer = copy.deepcopy(dispatch_buffer_temp)
    arf = copy.deepcopy(arf_temp); rrf = copy.deepcopy(rrf_temp)
    add_rs = copy.deepcopy(add_rs_temp)
    mul_rs = copy.deepcopy(mul_rs_temp)
    div_rs = copy.deepcopy(div_rs_temp)
    mem_op_rs = copy.deepcopy(mem_op_rs_temp)
    rob = copy.deepcopy(rob_temp)

    # Completion of instruction and ARF writeback
    while(len(rob) != 0):
            if(rob[0]['finished'] == 1):
                # Update ARF
                if(rob[0]['opcode'] != 'store'):
                    arf[rob[0]['rd']]['busy'] = 0
                    rrf[arf[rob[0]['rd']]['tag']]['busy'] = 0
                rob.remove(rob[0])
                rob_temp.remove(rob_temp[0])
            else: 
                break   

    
    print(dispatch_buffer)
    print(rob)
    print(issue_add_rs)
    print(issue_mul_rs)
    print(issue_div_rs)
    print(issue_mem_op_rs)
    print()
   

#***********************************************************************
#
# Printing the result
#
#***********************************************************************    
print("Total clock cycles elapsed:", cpu_clock)
file.close()
        
#*********************************************************************** END OF PROGRAM ***********************************************************************
