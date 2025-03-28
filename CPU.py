class CPU:
    def __init__(self, instructions):
        self.pc = 0
        self.instructions = instructions
        self.registers = [0] * 32
        self.memory = [0] * 128
        self.memory[0] = 5  # Input n
        self.memory[1] = 1  # Constant 1
        # memory[2] stays 0 until STORE
        self.cycle_count = 0

    def fetch(self):
        """Fetch the next instruction."""
        if self.pc >= len(self.instructions):
            return None  # Halt if no more instructions
        instr = self.instructions[self.pc]
        self.pc += 1
        return instr

    def decode(self, instr):
        """Split instruction into opcode and operands."""
        return instr.split()  # e.g., ["LOAD", "1", "0"]

    def execute(self, op, args):
        args = [int(arg) for arg in args]
        if op == "ADD":
            self.registers[args[0]] = self.registers[args[1]] + self.registers[args[2]]
        elif op == "SUB":
            self.registers[args[0]] = self.registers[args[1]] - self.registers[args[2]]
        elif op == "LOAD":
            self.registers[args[0]] = self.memory[args[1]]
        elif op == "STORE":
            self.memory[args[1]] = self.registers[args[0]]
        elif op == "CLR":
            self.registers[args[0]] = 0

    def run(self):
        """Run the CPU until all instructions are done."""
        while True:
            instr = self.fetch()
            if instr is None:
                break
            op, *args = self.decode(instr)
            self.execute(op, args)
            self.cycle_count += 1
            self.print_state()  # Show progress each cycle
        print("\nExecution finished.")
        self.print_final_state()

    def print_state(self):
        """Clean output for registers/memory."""
        print(f"Cycle {self.cycle_count}:")
        print(f"Registers: " + ", ".join(f"r{i}={self.registers[i]}" for i in range(1, 10)))
        print(f"Memory[0:4]: {self.memory[0:4]}")

    def print_final_state(self):
        """Show final result."""
        print(f"Final Result (5!): R8 = {self.registers[8]}, Memory[2] = {self.memory[2]}")