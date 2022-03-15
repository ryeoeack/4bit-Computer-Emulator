class Assembler:

    def __init__(self):
        self.ic = 0  # instruction counter
        self.arr1 = []  # stores instructions
        self.result = []

    def start(self):
        x = ""
        while self.ic < 16:
            print(self.ic, end='')
            print(' ', end='')
            x = input()
            self.ic = self.ic + 1
            if x == 'quit':
                break
            else:
                self.arr1.append(x)

        self.assemble()

    def assemble(self):
        self.result = []
        for i in self.arr1:
            tmp = i.split()
            if len(tmp) == 0:
                op = 'NOP'
                addr = 0

            elif len(tmp) == 1:
                op = tmp[0]
                addr = 0

            else:
                op = tmp[0]
                addr = int(tmp[1])

            if op == 'NOP':
                op = hex(0)
                self.result.append(op)

            elif op == 'LDA':
                op = 0b00010000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'ADD':
                op = 0b00100000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'SUB':
                op = 0b00110000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'STA':
                op = 0b01000000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'LDI':
                op = 0b01010000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'JMP':
                op = 0b01100000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'JC':
                op = 0b01110000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'JZ':
                op = 0b10000000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'OUT':
                op = 0b11100000
                op = hex(op | addr)
                self.result.append(op)

            elif op == 'HLT':
                op = 0b11110000
                op = hex(op | addr)
                self.result.append(op)

            else:
                try:
                    op = hex(int(op) % 256)
                    self.result.append(op)
                except Exception as inst:
                    pass

        for idx, val in enumerate(self.result):
            self.result[idx] = int(val, 16)
        #self.out_code()


def out_code(self):
    print("Successfully assembled!")
    for i in self.result:
        print(i)
    print("----------------------")


class Process:
    def __init__(self):
        self.ar = Assembler()
        # self.ar.start()
        self.mem = self.ar.result
        # self.mem=[0]*16
        # for i in range(len(self.mem)):
        #    self.mem[i] = int(self.mem[i], 16)
        self.curadr = 0  # address register, current ram address. I
        self.instreg = 0  # I/O
        self.accum = 0  # I/O
        self.breg = 0  # I
        self.lcd = 0  # I
        self.pc = 0  # I(j)/O
        self.zflag = 0  # C
        self.cflag = 0  # C
        self.sumreg = 0  # O
        self.step = 0  # keeping track of stages for micro-op
        self.inp = [1, 0, 0, 0, 0, 0, 0]  # MI,RI,II,AI,BI,OI,J
        self.out = [0, 0, 0, 0, 1]  # RO,IO,AO,EO,CO
        self.ctrl = [0, 0, 0, 0]  # HLT,Sub,CE,FI
        self.bus = 0
        self.switch = 0  # 1 for 2's complement mode

    def clock(self):  # every data processed during a clock cycle. advance everytime called.
        # ALU
        if self.ctrl[1] == 1:
            di = self.accum - self.breg
            if di < 0:
                self.sumreg = (256 - (self.accum - self.breg) % 129) % 256  # this isn't how it works..
            else:
                self.sumreg = self.accum - self.breg
            if self.ctrl[3] == 1:
                self.cflag = 1
                if self.sumreg == 0:
                    self.zflag = 0
        else:
            su = self.accum + self.breg
            self.sumreg = su % 256
            if self.ctrl[3] == 1:
                if su > 255:
                    self.cflag = 1
                else:
                    self.cflag = 0
                if self.sumreg == 0:
                    self.zflag = 1
                else:
                    self.zflag = 0

        # output to bus sequence
        self.bus = self.mem[self.curadr] * self.out[0] + (self.instreg & 0x0F) * self.out[1] + self.accum * self.out[
            2] + self.sumreg * self.out[3] + self.pc * self.out[4]

        # input from bus sequence
        self.curadr += -(self.curadr * self.inp[0]) + (self.bus & 0x0F) * self.inp[0]
        self.mem[self.curadr] += -(self.mem[self.curadr] * self.inp[1]) + self.bus * self.inp[1]
        self.instreg += -(self.instreg * self.inp[2]) + self.bus * self.inp[2]
        self.accum += -(self.accum * self.inp[3]) + self.bus * self.inp[3]
        self.breg += -(self.breg * self.inp[4]) + self.bus * self.inp[4]
        self.lcd += -(self.lcd * self.inp[5]) + self.bus * self.inp[5]
        self.pc += -(self.pc * self.inp[6]) + (self.bus & 0x0F) * self.inp[6]
        # this will set every component to zero except for one getting input! Better solution needed.....

        # program counter
        self.pc = (self.pc + self.ctrl[2]) % 16

        # step advance
        self.step = (self.step + 1) % 5  # if you want to add instruction with more than 5 steps...

        # print output
        self.lcd_out(self.switch)

    def lcd_out(self, mode):  # switch for 2's complement mode
        if mode == 0:
            print("unsigned mode")
            print(self.lcd)

        else:
            print("signed mode")
            if self.lcd < 128:
                print(self.lcd)
            else:
                print(((256 - self.lcd) * -1) % 256)

    def ctrl(self, opcode):
        # 0HLT 1MI 2RI 3RO 4IO 5II 6AI 7AO 8EO 9SU 10BI 11OI 12CE 13CO 14J 15FI
        cword = [0]*16
        # fetch
        if self.step == 0:
            cword[1], cword[13] = 1, 1
        elif self.step == 1:
            # cword = '0001010000001000'
            cword[3], cword[5], cword[12] = 1, 1, 1
        # op specific
        elif self.step == 2:
            if opcode == 0:  # NOP
                # cword = '0000000000000000'
                self.step = 0
                pass
            elif opcode == 1 or 2 or 3 or 4:  # LDA or ADD or SUB or STA
                # cword = '0100100000000000'  # IO|MI
                cword[1], cword[4] = 1, 1
            elif opcode == 5:  # LDI
                cword[4], cword[6] = 1, 1  # IO|AI
                self.step = 0
            elif opcode == 6:  # JMP
                # cword = '0100000000000010'
                cword[1], cword[14] = 1, 1
                self.step = 0
            elif opcode == 14:  # OUT
                # cword = '0000000100010000'  # AO|OI
                cword[7], cword[11] = 1, 1
            elif opcode == 15:
                cword[0] = 1
                self.step = 0
        elif self.step == 3:
            if opcode == 1:  # LDA
                cword[3], cword[6] = 1, 1  # RO|AI
            elif opcode == 2 or 3:  # ADD or SUB
                cword[3], cword[10] = 1, 1  # RO|BI
            elif opcode == 4:  # STA
                cword[2], cword[7] = 1, 1  # RI|AO
        elif self.step == 4:
            if opcode == 2:  # ADD
                opcode[6], opcode[8], opcode[15] = 1, 1, 1
                self.step = 0
            elif opcode == 3:  # SUB
                opcode[6], opcode[8], opcode[9], opcode[15] = 1, 1, 1, 1
                self.step = 0
        return cword
