import sys
from CPU import CPU  # Adjusted import path
from assembler import assemble

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <assembly_file.asm> [debug]")
        sys.exit(1)

    debug = len(sys.argv) > 2 and sys.argv[2] == "debug"

    # Assemble the program
    instructions, _ = assemble(sys.argv[1])

    # Initialize and run the CPU
    cpu = CPU(instructions)
    cpu.run()

    # Print final state if debug mode
    if debug:
        cpu.print_state()

if __name__ == "__main__":
    main()