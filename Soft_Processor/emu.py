# -*- coding: utf-8 -*-
import os
import struct
import sys
from time import sleep
from time import time
import platform

# create a GUI variable called app

os.system('make clean')
os.system('make all')
os.system('python comp.py')
os.system('python conv.py xx')

if( platform.system()=='Windows'):
    import msvcrt
else:
    import getch

reg_array = []

memory = []
fifo_addr = 'e0001030'
mem_size = 24
PC = int('00000000', 16) / 4

opcode = {
    '0110111': 'lui',
    '0010111': 'auipc',
    '1101111': 'jump',
    '1100111': 'jumpr',
    '1100011': 'cjump',
    '0000011': 'load',
    '0100011': 'store',
    '0010011': 'iops',
    '0110011': 'rops',
    '1110011': 'system',
    '0001111': 'fenc',
    '0101111': 'rops',
    '0000000': 'uimp',
    }


def convert(i):
    return int(bin(i + 2 ** 32)[-32:])


for i in range(32):
    if i == 2:
        reg_array.append(int('400',16))
    elif i == 3:
        reg_array.append(0)
    else:
        reg_array.append(0)


for i in xrange(1 << mem_size):
    memory.append(0)
filed = open('data_hex.txt', 'r')

data = filed.readlines()


def rem(num1, num2):
    if num2 == 0:
        return num1
    elif num1 < 0 and num2 > 0:
        return -(-num1 % num2)
    elif num1 > 0 and num2 > 0:
        return num1 % num2
    elif num1 < 0 and num2 < 0:
        return -(-num1 % -num2)
    elif num1 > 0 and num2 < 0:
        return num1 % -num2
    elif num1 == 0:
        return 0


def div(num1, num2):
    if num2 == 0:
        if num1 < 0:
            return 1
        else:
            return -1
    elif num1 < 0 and num2 > 0:
        return -(-num1 / num2)
    elif num1 > 0 and num2 < 0:
        return -(num1 / -num2)
    elif num1 < 0 and num2 < 0:
        return -num1 / -num2
    elif num1 > 0 and num2 > 0:
        return num1 / num2
    elif num1 == 0:
        return 0


def twoscomp32(num):
    if num < 0:
        num = pow(2, 32) + num
    else:
        num = num
    return num


def twoscomp64(num):
    if num < 0:
        num = pow(2, 64) + num
    else:
        num = num
    return num


def usigned(num):
    if num < 0:
        num = num + 1 << 32
    else:
        return num


def signed(num):
    if bin(num)[2] == '1' and len(bin(num)) == 34:
        return num - (1 << 32)
    else:
        return num


for i in range(len(data)):
    memory[i] = int(data[i], 16)


def conv(imm):
    num = int('0b' + imm, 2)
    return num


def byte_extend(num, typ):
    if bin(num)[2] == '1' and len(bin(num)) == 10 and typ == 1:
        return conv('1' * 24 + bin(num)[2:])
    else:
        return conv(bin(num)[2:])


def hword_extend(num, typ):
    if bin(num)[2] == '1' and len(bin(num)) == 18 and typ == 1:
        return conv('1' * 16 + bin(num)[2:])
    else:
        return conv(bin(num)[2:])


def rashift(num, n):

    if bin(num)[2] == '1' and len(bin(num)) == 34:

        return int('1' * n + bin(num)[2:34 - n], 2)
    else:
        return num >> n


x = 0
n = 0
pre = 0
cycle = 0
pr = ''
try:
    mile = \
        open('/home/riscv_group/Desktop/New/Wingle.sim/sim_1/behav/mem_reads.txt'
             , 'r')
    cile = \
        open('/home/riscv_group/Desktop/New/Wingle.sim/sim_1/behav/clocks.txt'
             , 'r')
    nile = mile.readlines()
    clocks = cile.readlines()

except:
###    print "error"
###    sys.exit(0)
    pass
flag=0

while PC < 1 << 20:
##    print hex(PC*4)
    sub = []
    imm = 32 * '0'
    wb_data = 0
    instruction = memory[PC]

    binary = bin(instruction)[2:]
    binary = (32 - len(binary)) * '0' + binary
    rs1_sel = conv(binary[12:17])
    rs2_sel = conv(binary[7:12])
    rd = conv(binary[20:25])
    function = binary[17:20]
    start_fu = binary[0:7]
    lpc = PC
    PC = PC + 1

 # ##########################################lui##################################################

    if opcode[binary[25:32]] == 'lui':
        imm = binary[0:20] + 12 * '0'
        wb_data = conv(imm)
        reg_array[rd] = wb_data
    elif opcode[binary[25:32]] == 'auipc':

 # ###########################################auipc######################################################

        imm = binary[0:20] + 12 * '0'
        wb_data = ((PC - 1) * 4 + conv(imm)) % (1 << 32)
        reg_array[rd] = wb_data
    elif opcode[binary[25:32]] == 'jump':

#######################################jump and link ####################################################

        imm = 12 * binary[0] + binary[12:20] + binary[11] + binary[1:7] \
            + binary[7:11] + '0'
        wb_data = PC * 4
        reg_array[rd] = wb_data
        PC = ((PC - 1) * 4 + conv(imm)) % (1 << 32) / 4
    elif opcode[binary[25:32]] == 'jumpr':

###############################################jump and link register####################################

        imm = 21 * binary[0] + binary[1:12]
        wb_data = PC * 4
        PC = (reg_array[rs1_sel] + conv(imm)) % (1 << 32) / 4
        reg_array[rd] = wb_data
    elif opcode[binary[25:32]] == 'cjump':

#####################################conditional jump####################################################

        branch = 0
        imm = 20 * binary[0] + binary[24] + binary[1:7] + binary[20:24] \
            + '0'

        if function == '000':  # #BEQ
            branch = reg_array[rs1_sel] == reg_array[rs2_sel]
        elif function == '001':

                                   # #BNE

            branch = reg_array[rs1_sel] != reg_array[rs2_sel]
        elif function == '100':

                                   # #BLT

            branch = signed(reg_array[rs1_sel]) \
                < signed(reg_array[rs2_sel])
        elif function == '101':

                                   # #BGE

            branch = signed(reg_array[rs1_sel]) \
                >= signed(reg_array[rs2_sel])
        elif function == '110':

                                   # #BLTU

            branch = reg_array[rs1_sel] < reg_array[rs2_sel]
        elif function == '111':

                                   # #BGEU

            branch = reg_array[rs1_sel] >= reg_array[rs2_sel]
        if branch == 1:
            PC = ((PC - 1) * 4 + conv(imm)) % (1 << 32) / 4
    elif opcode[binary[25:32]] == 'load':

####################################load####################################################################

        imm = 21 * binary[0] + binary[1:12]
        wb_data = (((reg_array[rs1_sel] + conv(imm))) % (1<<mem_size)) 
        wb_prev=(((reg_array[rs1_sel] + conv(imm))) % (1<<32)) 
        if wb_data >= 1 << mem_size:
            print 'out_of_range_memory', hex(lpc * 4), hex(wb_data)
            break
        read_data = memory[wb_data / 4]
        if ((wb_prev!=int('e000102c',16)) and (wb_prev!=int('e0001030',16))):
            if function == '000':
                reg_array[rd] = byte_extend((read_data >> wb_data % 4 * 8)
                        % 256, 1)
            elif function == '001':
                reg_array[rd] = hword_extend((read_data >> wb_data % 4 * 8)
                        % (256 * 256), 1)
            elif function == '010':
                reg_array[rd] = read_data
            elif function == '100':
                reg_array[rd] = byte_extend((read_data >> wb_data % 4 * 8)
                        % 256, 0)
            elif function == '101':

                reg_array[rd] = hword_extend((read_data >> wb_data % 4 * 8)
                        % (256 * 256), 0)
            
        elif (wb_prev==int('e000102c',16)):
##            print 'here1'
            reg_array[rd]=0
        elif  (wb_prev==int('e0001030',16)):
           #  print 'here'
            if( platform.system()=='Windows'):
                reg_array[rd]=ord(msvcrt.getch())
            else:
                reg_array[rd]=ord(getch.getch())
            

        wb_data = wb_prev
    elif opcode[binary[25:32]] == 'store':

  # ######################### store############################################################################

        imm = 21 * binary[0] + binary[1:7] + binary[20:25]
        wb_data = (reg_array[rs1_sel] + conv(imm)) % (1 << mem_size)
        wb_prev =  (reg_array[rs1_sel] + conv(imm)) % (1 << 32)
        sub = []
        if wb_data >= 1 << mem_size:
            print 'out_of_range_memory', hex(lpc * 4), hex(wb_data / 4)
            break
        if (((reg_array[rs1_sel] + conv(imm))%(1<<32))) != int(fifo_addr,16):  # #FIFO ADDRESSS for printf (65872)
            if function == '000':  # #STORE_BYTE
                sub.extend((32 - len(bin(memory[wb_data / 4])[2:]))
                           * '0' + bin(memory[wb_data / 4])[2:])
                sub[8 * (3 - wb_data % 4):8 * (3 - wb_data % 4) + 8] = \
                    (8 - len(bin(reg_array[rs2_sel] % 256)[2:])) * '0' \
                    + bin(reg_array[rs2_sel] % 256)[2:]
                memory[wb_data / 4] = int(''.join(sub), 2)
            elif function == '001':

                                      # #STORE_HALF_WORD

                sub.extend((32 - len(bin(memory[wb_data / 4])[2:]))
                           * '0' + bin(memory[wb_data / 4])[2:])
                if wb_data % 4 == 3:
                    print 'data_missaligned at PC =', hex(lpc * 4)
                    break
                sub[8 * (2 - wb_data % 4):8 * (2 - wb_data % 4) + 16] = \
                    (16 - len(bin(reg_array[rs2_sel] % (256
                     * 256))[2:])) * '0' + bin(reg_array[rs2_sel]
                        % (256 * 256))[2:]
                memory[wb_data / 4] = int(''.join(sub), 2)
            else:
                memory[wb_data / 4] = reg_array[rs2_sel]  # #STORE_WORD
        else:

            sys.stdout.write(chr(reg_array[rs2_sel]))
        wb_data =wb_prev
        
    elif opcode[binary[25:32]] == 'iops':

  # ######################## register-imediate operations##########################################################

        imm = 21 * binary[0] + binary[1:12]
        if function == '000':  # #ADDI
            wb_data = (reg_array[rs1_sel] + conv(imm)) % (1 << 32)
        elif function == '001':

                                # #SLLI

            wb_data = (reg_array[rs1_sel] << conv(imm[27:32])) % (1
                    << 32)
        elif function == '010':

                                # #SLTI

            wb_data = signed(reg_array[rs1_sel]) < signed(conv(imm))
        elif function == '011':

                                # #SLTUI

            wb_data = reg_array[rs1_sel] < conv(imm)
        elif function == '100':

                                # #XORI

            wb_data = reg_array[rs1_sel] ^ conv(imm)
        elif function == '101':
            if start_fu == '0000000':  # #SLLI
                wb_data = reg_array[rs1_sel] >> conv(imm[27:32])
            elif start_fu == '0100000':

                                         # #SLAI

                wb_data = rashift(reg_array[rs1_sel], conv(imm[27:32]))
        elif function == '110':

                                # #ORI

            wb_data = reg_array[rs1_sel] | conv(imm)
        elif function == '111':

                                # #ANDI

            wb_data = reg_array[rs1_sel] & conv(imm)
        reg_array[rd] = wb_data
    elif opcode[binary[25:32]] == 'rops':

   # #########################################register-register operation ##################################################

        if start_fu == '0000001':
            if function == '000':  # #MUL
                wb_data = twoscomp64(signed(reg_array[rs1_sel])
                        * signed(reg_array[rs2_sel])) % (1 << 32)
            elif function == '001':

                # wb_data= (usigned((reg_array[rs1_sel] * reg_array[rs2_sel]))%(1<<32))
                                        # #MULH

                wb_data = twoscomp64(signed(reg_array[rs1_sel])
                        * signed(reg_array[rs2_sel])) / (1 << 32)
            elif function == '010':

                                        # #MULHSU

                wb_data = twoscomp64(signed(reg_array[rs1_sel])
                        * reg_array[rs2_sel]) / (1 << 32)
            elif function == '011':

                                        # #MULHU

                wb_data = twoscomp64(reg_array[rs1_sel]
                        * reg_array[rs2_sel]) / (1 << 32)
            elif function == '100':

                                       # #DIV

                wb_data = twoscomp32(div(signed(reg_array[rs1_sel]),
                        signed(reg_array[rs2_sel])))
            elif function == '110':

                                       # #REM

                wb_data = twoscomp32(rem(signed(reg_array[rs1_sel]),
                        signed(reg_array[rs2_sel])))
            elif function == '101':

                                       # #DIVU

                wb_data = twoscomp32(div(reg_array[rs1_sel],
                        reg_array[rs2_sel]))
            elif function == '111':

                                       # #REMU

                wb_data = twoscomp32(rem(reg_array[rs1_sel],
                        reg_array[rs2_sel]))
        else:

            if function == '000':
                if start_fu == '0000000':  # ADD
                    wb_data = (reg_array[rs1_sel] + reg_array[rs2_sel]) \
                        % (1 << 32)
                if start_fu == '0100000':  # #SUB
                    wb_data = (reg_array[rs1_sel] + (1 << 32)
                               - reg_array[rs2_sel]) % (1 << 32)
            elif function == '001':

                                    # #SLL

                wb_data = (reg_array[rs1_sel] << reg_array[rs2_sel]
                           % 32) % (1 << 32)
            elif function == '010':

                                    # #SLT

                wb_data = signed(reg_array[rs1_sel]) \
                    < signed(reg_array[rs2_sel])
            elif function == '011':

                                    # #SLTU

                wb_data = reg_array[rs1_sel] < reg_array[rs2_sel]
            elif function == '100':

                                    # #XOR

                wb_data = reg_array[rs1_sel] ^ reg_array[rs2_sel]
            elif function == '101':
                if start_fu == '0000000':  # # SRL
                    wb_data = reg_array[rs1_sel] >> reg_array[rs2_sel] \
                        % 32
                elif start_fu == '0100000':

                                             # #SRA

                    wb_data = rashift(reg_array[rs1_sel],
                            reg_array[rs2_sel] % 32)
            elif function == '110':

                                    # #OR

                wb_data = reg_array[rs1_sel] | reg_array[rs2_sel]
            elif function == '111':

                                    # #AND

                wb_data = reg_array[rs1_sel] & reg_array[rs2_sel]
        reg_array[rd] = wb_data
    elif opcode[binary[25:32]] == 'system':

##################################################previledge instructions#####################################################

        if binary[0:12] == bin(int('c00', 16))[2:]:
            reg_array[rd] = n#int(clocks[n])  # rd_CYCLE
        if binary[0:12] == bin(int('c02', 16))[2:]:
            reg_array[rd] = n  # INSRET
        wb_data = reg_array[rd]
    val = (10 - len(hex(lpc * 4).strip('L'))) * '0' + hex(lpc
            * 4).strip('L')[2:] + ' ' + (10 - len(hex(wb_data).strip('L'
            ))) * '0' + hex(wb_data).strip('L')[2:]

    try:
        if val != (nile[n])[:-1]:
            print prev
            print 'from python', val, 'from logic ', (nile[n])[:-1], \
                '\t'
            print 'last', prevs
            print 'now', int(clocks[n]), 'rs1', \
                hex(reg_array[rs1_sel]), 'rs2', \
                hex(reg_array[rs2_sel]), opcode[binary[25:32]], 'imm', \
                hex(conv(imm)), 'rs1', rs1_sel, 'rs2s', rs2_sel, rd, \
                function
            break
    except:

##        print "\nstill execting",n
##        break

        pass
    try:
        prev = val + ' ' + (nile[n])[:-1]
    except:
        pass

##        print n

##    if (instruction == int('00008067',16)):
##        x+=1
##        if (ins_memory[lpc]!=reg_array[1]):
##            ins_memory[lpc]=reg_array[1]
##            print hex(lpc*4),reg_array[1]
##
##        if(x==10000):break
##
##    if (reg_array[2] > (1<<20)):
##        print "outofboundry", reg_array[2]

    prevs = (
        hex(reg_array[rs1_sel]),
        hex(reg_array[rs2_sel]),
        opcode[binary[25:32]],
        conv(imm),
        start_fu,
        rs1_sel,
        rs2_sel,
        function,
        rd,
        hex(wb_data),
        )

    n = n + 1
    cycle += 1
    reg_array[0] = 0

    if lpc == PC:  # #BREAKS AT INFINITE LOOP
        break

			
