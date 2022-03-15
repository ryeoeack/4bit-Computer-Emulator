from tkinter import *
import tkinter.messagebox as msg
from emulator import *

root = Tk()
root.title("Ben Eater's 8 bit computer emulator developed by Mulmit")
machine = Process()


# Definitions #
def submit():
    txt = asm.get("1.0", END)
    machine.mem = []
    machine.ar.arr1 = txt.split("\n")
    machine.ar.arr1.remove('')
    machine.ar.assemble()
    machine.mem = machine.ar.result
    print(machine.ar.arr1, " ", machine.mem)
    for i in range(inspector.size()):
        inspector.delete(END)
    for i in machine.mem:
        inspector.insert(END, i)


def run():
    try:
        for i in range(inspector.size()):
            inspector.delete(END)
        machine.clock()
        for i in machine.mem:
            inspector.insert(END, i)
        print(bin(machine.step))
        buspector.delete(0, END)
        buspector.insert(0, machine.bus)
        step_counter.delete(0, END)
        step_counter.insert(0, bin(machine.step))
    except Exception as inst:
        msg.showwarning("Error", inst)


# Option
menu = Menu(root)
menu_file = Menu(menu, tearoff=0)
menu_file.add_command(label="New File")
menu.add_cascade(label="File", menu=menu_file)
# layout

# programming
frame_asm = LabelFrame(root, text="Assembler")
frame_asm.pack(side="left")

asm = Text(frame_asm, width=50, height=16)
asm.pack(pady=5)
btn_submit = Button(frame_asm, text="submit", width=10, command=submit)
btn_submit.pack(padx=5, pady=5)
# RAM inspector
frame_RAM = LabelFrame(root, text="RAM inspector")
frame_RAM.pack(side="right")

inspector = Listbox(frame_RAM, height=16)
inspector.pack(fill="y")
buspector = Entry(frame_RAM)
buspector.pack()
step_counter = Entry(frame_RAM)
step_counter.pack()
# Ctrl words
# HLT MI RI RO IO II AI AO EO SU BI OI CE CO J FI

# Output
frame_output = LabelFrame(root, text="Output monitor")
frame_output.pack(side="bottom", padx=10)
LCD = Label(frame_output, text=str(machine.lcd))
LCD.pack(ipady=10)
switch = Checkbutton(frame_output, text="signed", variable=machine.switch)
switch.pack()
btn_run = Button(root, text="RUN!", width=10, command=run)
btn_run.pack(padx=5, pady=5)
root.config(menu=menu)

mainloop()
