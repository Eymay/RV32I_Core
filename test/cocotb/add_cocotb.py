import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, Timer

from as2hex import *

def debug_instr(dut, addr):
    for i in range(4):
        print(hex(dut.instr_mem.imem[addr+i].value))
    print("PC:", hex(dut.o_PC.value))
    print("Instr mem:", hex(dut.o_instruction_mem.value))

def debug_signals(dut, addr):
    for i in range(4):
        print(hex(dut.instr_mem.imem[addr+i].value))
    print("PC:", hex(dut.o_PC.value))
    print("Instr mem:", hex(dut.o_instruction_mem.value))
    print("Reg1:", dut.dp.regfile.regs[2].value)
    print("Reg2:", dut.dp.regfile.regs[4].value)
    print("ALU A:", dut.dp.ALU.A.value)
    print("ALU B:", dut.dp.ALU.B.value)
    print("Regfile out 2:", dut.dp.o_regfile_rreg2.value)
    print("CW", dut.cu.ctrl_wrd.value)
    print("CW4_2", dut.dp.CW4_2.value)
    print("Imm out:", dut.dp.o_imm.value)
    print("ALU out:", dut.o_ALU.value)


class r_encoding:
    def __init__(self, rd, rs1, rs2):
        self.rd_idx = rd
        self.rs1_idx = rs1
        self.rs2_idx = rs2

class instruction():
    def __init__(self, op, place1, place2, place3): 
        #place1, place2, place3 are the places where the operands are in the instruction
        self.op = op
        self.place1 = place1
        self.place2 = place2
        self.place3 = place3
        self.assembly = op +" "+ place1 +", "+ place2 +", "+ place3
        self.instr_byte = as2hex(self.assembly , op)

    def get_instr_byte(self):
        return self.instr_byte
    def get_assembly(self):
        return self.assembly

class r_type(r_encoding):
    def __init__(self, dut, rd, rs1, rs2, op, opstring):
        super().__init__(rd, rs1, rs2)
        self.rd = dut.dp.regfile.regs[rd]
        self.rs1 = dut.dp.regfile.regs[rs1]
        self.rs2 = dut.dp.regfile.regs[rs2]
        self.op = op
        self.ideal_result = 0
        self.ideal_rs1 = 0
        self.ideal_rs2 = 0
        self.instr = instruction(
                opstring, 
                "x{}".format(rd),
                "x{}".format(rs1),
                "x{}".format(rs2))
        self.dut = dut

    def check_x0(self, reg, value):
        #x0 register is hardwired to 0 in RISC-V
        return 0 if reg == 0 else value

    def set_rs1(self, value):
        self.rs1.value = self.check_x0(self.rs1_idx, value)
        self.ideal_rs1 = value

    def set_rs2(self, value):
        self.rs2.value = self.check_x0(self.rs2_idx, value)
        self.ideal_rs2 = value

    def set_ideal_result(self):
        self.ideal_result = self.check_x0(self.rd_idx, self.gold())

    def set_instruction(self,addr):
        instr = self.instr.get_instr_byte()
        print("Instr emmitted is", instr[0], instr[1], instr[2], instr[3])
        for i in range(4):
            self.dut.instr_mem.imem[addr+i].value = int(instr[i], 16)

    def gold(self):
        return self.op(self.ideal_rs1,self.ideal_rs2)

    def check_ALU(self):
        assert self.dut.dp.o_ALU.value == self.ideal_result, "ALU output not correct {} != {}".format(self.dut.dp.o_ALU.value, self.ideal_result)

    def check_rd(self):
        assert self.rd.value == self.ideal_result, "Destination register has wrong result {} != {}".format(self.rd.value, self.ideal_result)


async def generic_rtype_test(dut, op, opstring):
    """Try accessing the design."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst.value = 0
    await Timer(5, units="ns")
    dut.rst.value = 1
    await Timer(5, units="ns")
    rd = 1
    rs1 = 2
    rs2 = 4
    addr = 4

    instr_obj = r_type(dut, rd, rs1, rs2, op, opstring)
    instr_obj.set_rs1(5)
    instr_obj.set_rs2(3)
    instr_obj.set_ideal_result()
    instr_obj.set_instruction(addr)

    debug_instr(dut, addr)

    await FallingEdge(dut.clk)
    debug_signals(dut, addr)
    instr_obj.check_ALU()

    await FallingEdge(dut.clk)
    instr_obj.check_rd()
    debug_instr(dut, addr)

    dut.PC.Q.value = 4


@cocotb.test()
async def add_test(dut):
    await generic_rtype_test(dut, lambda x,y: x+y, "add")

@cocotb.test()
async def sub_test(dut):
    await generic_rtype_test(dut, lambda x,y: x-y, "sub")

@cocotb.test()
async def sll_test(dut):
    await generic_rtype_test(dut, lambda x,y: x<<y, "sll")

@cocotb.test()
async def slt_test(dut):
    await generic_rtype_test(dut, lambda x,y: 1 if x<y else 0, "slt")

@cocotb.test()
async def sltu_test(dut):
    await generic_rtype_test(dut, lambda x,y: 1 if (x+2**32)<(y+2**32) else 0, "sltu")

@cocotb.test()
async def xor_test(dut):
    await generic_rtype_test(dut, lambda x,y: x^y, "xor")

@cocotb.test()
async def srl_test(dut):
    await generic_rtype_test(dut, lambda x,y: (x % 0x100000000) >> y, "srl")

@cocotb.test()
async def sra_test(dut):
    await generic_rtype_test(dut, lambda x,y: x>>y, "sra")

@cocotb.test()
async def or_test(dut):
    await generic_rtype_test(dut, lambda x,y: x|y, "or")

@cocotb.test()
async def and_test(dut):
    await generic_rtype_test(dut, lambda x,y: x&y, "and")
