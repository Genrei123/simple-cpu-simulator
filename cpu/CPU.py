from .Memory import REGISTERS, MEMORY, SCOREBOARD, RAT
from .reorder_buffer import reorder_buffer
from .memory_order_buffer import memory_order_buffer
import pprint
import matplotlib.pyplot as plt
from collections import defaultdict

class CPU():
    def __init__(self, instructions, labels, fetch_unit, decode_unit, execute_units, writeback_unit):
        self.program_counter = 0
        self.instruction_cache = instructions
        self.labels = labels
        
        self.fetch_unit = fetch_unit
        self.decode_unit = decode_unit
        self.execute_units = execute_units
        self.writeback_unit = writeback_unit

        self.reorder_buffer = reorder_buffer()
        self.memory_order_buffer = memory_order_buffer()

        self.all_components = [self.fetch_unit, self.decode_unit] + self.execute_units + [self.writeback_unit]

        self.cycle_count = 0
        self.instructions_executed = 0
        self.flushed_count = 0
        
        # For visualization
        self.cycle_history = []
        self.pc_history = []
        self.instructions_executed_history = []
        self.register_history = defaultdict(list)
        self.memory_history = defaultdict(list)
        self.pipeline_stats = {
            'fetch': [],
            'decode': [],
            'execute': [],
            'writeback': []
        }

    def increment_pc(self, num=1):
        self.program_counter += num

    def increment_cycle(self):
        self.cycle_count += 1   
        # Record history for visualization
        self.cycle_history.append(self.cycle_count)
        self.pc_history.append(self.program_counter)
        self.instructions_executed_history.append(self.instructions_executed)
        
        # Record pipeline activity
        self.pipeline_stats['fetch'].append(0 if self.fetch_unit.halt else 1)
        self.pipeline_stats['decode'].append(0 if self.decode_unit.halt else 1)
        self.pipeline_stats['execute'].append(0 if all(unit.halt for unit in self.execute_units) else 1)
        self.pipeline_stats['writeback'].append(0 if self.writeback_unit.halt else 1)
        
        # Record register and memory state periodically
        if self.cycle_count % 5 == 0 or self.cycle_count == 1:  # Record every 5 cycles and first cycle
            for reg, val in REGISTERS.items():
                self.register_history[reg].append((self.cycle_count, val))
            for addr, val in enumerate(MEMORY[:256]):  # Only track first 256 memory locations
                if val != 0:  # Only track non-zero memory locations
                    self.memory_history[addr].append((self.cycle_count, val))

    def increment_ie(self):
        self.instructions_executed += 1

    def check_start(self):
        if not self.fetch_unit.halt and self.decode_unit.halt:
            self.decode_unit.start_unit()
            return

        if not self.decode_unit.halt and any(unit.halt == True for unit in self.execute_units):
            for unit in self.execute_units:
                unit.start_unit()
            return

        if any(unit.halt == False for unit in self.execute_units) and self.writeback_unit.halt:
            self.writeback_unit.start_unit()
            return

        for unit in self.execute_units:
            if not unit.reservation_station.is_empty():
                unit.start_unit()
        
        return False

    def shutdown(self):
        for comp in self.all_components:
            comp.halt_unit()

    def check_done(self):
        return all(component.halt == True for component in self.all_components)

    def iterate(self, debug=False):
        self.writeback_unit.run(self)
        
        for unit in self.execute_units:
            unit.run(self)

        self.decode_unit.run(self)
            
        self.fetch_unit.run(self)

        self.check_start()
        self.increment_cycle()
        
        if debug:
            self.print_state()
            input("Press ENTER to continue... ")

    def flush_pipeline(self, instruction):
        self.reorder_buffer.flush(instruction)
        self.memory_order_buffer.flush(self)

        for comp in self.all_components:
            comp.flush(self, instruction)
    
    def update_reservation(self):
        for unit in self.execute_units:
            unit.update_reservation(self)
    
    def set_new_destination(self, reg, index):
        RAT[reg] = "rob" + str(index)
        return "rob" + str(index)
    
    def plot_pipeline_activity(self):
        plt.figure(figsize=(12, 6))
        for stage, activity in self.pipeline_stats.items():
            plt.plot(self.cycle_history, activity, label=stage)
        plt.title('Pipeline Stage Activity Over Time')
        plt.xlabel('Cycle Count')
        plt.ylabel('Activity (1 = active, 0 = halted)')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_register_values(self, register_names):
        plt.figure(figsize=(12, 6))
        for reg in register_names:
            if reg in self.register_history and len(self.register_history[reg]) > 0:
                cycles, values = zip(*self.register_history[reg])
                plt.plot(cycles, values, label=reg)
        plt.title('Register Values Over Time')
        plt.xlabel('Cycle Count')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_memory_values(self, addresses):
        plt.figure(figsize=(12, 6))
        for addr in addresses:
            if addr in self.memory_history and len(self.memory_history[addr]) > 0:
                cycles, values = zip(*self.memory_history[addr])
                plt.plot(cycles, values, label=f'Memory[{addr}]')
        plt.title('Memory Values Over Time')
        plt.xlabel('Cycle Count')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_program_counter(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.cycle_history, self.pc_history)
        plt.title('Program Counter Over Time')
        plt.xlabel('Cycle Count')
        plt.ylabel('PC Value')
        plt.grid(True)
        plt.show()
    
    def plot_instructions_executed(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.cycle_history, self.instructions_executed_history)
        plt.title('Instructions Executed Over Time')
        plt.xlabel('Cycle Count')
        plt.ylabel('Total Instructions Executed')
        plt.grid(True)
        plt.show()
    
    def plot_all_stats(self):
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        for stage, activity in self.pipeline_stats.items():
            plt.plot(self.cycle_history, activity, label=stage)
        plt.title('Pipeline Activity')
        plt.xlabel('Cycle')
        plt.ylabel('Activity')
        plt.legend()
        
        plt.subplot(2, 2, 2)
        plt.plot(self.cycle_history, self.pc_history)
        plt.title('Program Counter')
        plt.xlabel('Cycle')
        plt.ylabel('PC Value')
        
        plt.subplot(2, 2, 3)
        plt.plot(self.cycle_history, self.instructions_executed_history)
        plt.title('Instructions Executed')
        plt.xlabel('Cycle')
        plt.ylabel('Count')
        
        plt.subplot(2, 2, 4)
        for reg in list(self.register_history.keys())[:5]:  # Show first 5 registers
            plt.plot(range(0, self.cycle_count, 5), self.register_history[reg], label=reg)
        plt.title('Register Values')
        plt.xlabel('Cycle')
        plt.ylabel('Value')
        plt.legend()
        
        plt.tight_layout()
        plt.show()

    def print_state(self, final=False):
            if final:    
                stats = ("CYCLE COUNT: " + str(self.cycle_count) + "  |  "
                        "FLUSHED COUNT: " + str(self.flushed_count) + "  |  "
                        "INSTRUCTIONS EXECUTED: " + str(self.instructions_executed) + "  |  "
                        "INSTRUCTIONS PER CYCLE: " + str(self.instructions_executed / self.cycle_count))
                
                # Automatically show visualizations when simulation ends
                self.show_visualizations()
            else:
                stats = ("CURRENT CYCLE: " + str(self.cycle_count) + "  |  "
                        "PC: " + str(self.program_counter) + "  |  ")
                
                for comp in self.all_components[0:2]:
                    print(comp.__class__.__name__ + "  |  " + str(comp.halt))
                    pprint.pprint(comp.pipeline_register, compact=True)
                
                for unit in self.execute_units:
                    print(unit.__class__.__name__ + "  |  " + str(unit.halt))
                    pprint.pprint(unit.pipeline_register, compact=True)
                    pprint.pprint(unit.reservation_station.reservation, compact=True)
                
                print(self.writeback_unit.__class__.__name__ + "  |  " + str(self.writeback_unit.halt))
                pprint.pprint(self.writeback_unit.pipeline_register, compact=True)
                        
            print("\n" + stats)
            
            print("\nINSTRUCTION BUFFER:")
            pprint.pprint(self.decode_unit.instruction_buffer, compact=True)

            print("\nREORDER BUFFER:")
            print(f"TAIL:{self.reorder_buffer.tail} HEAD:{self.reorder_buffer.head}")
            pprint.pprint(self.reorder_buffer.buffer, compact=True)

            print("\n|  REGISTER  |  VALUE  |  SCOREBOARD  |")
            for state in REGISTERS:
                if len(str(state)) > 2:
                    print(f"|     {state}    |    {REGISTERS[str(state)]}    |      {SCOREBOARD[str(state)]}       |    {RAT[str(state)]}")
                else:
                    print(f"|     {state}     |    {REGISTERS[str(state)]}    |      {SCOREBOARD[str(state)]}       |    {RAT[str(state)]}")

            print("\nMEMORY:")
            pprint.pprint(MEMORY[:256], compact=True)
            print("...")

    def show_visualizations(self):
        """Display all visualizations automatically at the end of simulation"""
        try:
            # Show pipeline activity
            if len(self.cycle_history) == len(self.pipeline_stats['fetch']):
                self.plot_pipeline_activity()
            
            # Show PC progression
            if len(self.cycle_history) == len(self.pc_history):
                self.plot_program_counter()
            
            # Show instructions executed
            if len(self.cycle_history) == len(self.instructions_executed_history):
                self.plot_instructions_executed()
            
            # Show register values for the first 3 registers that changed
            if self.register_history:
                active_registers = [reg for reg in self.register_history if len(self.register_history[reg]) > 0]
                if active_registers:
                    self.plot_register_values(active_registers[:3])  # Plot first 3 active registers
            
            # Show memory values for addresses that changed
            if self.memory_history:
                active_mem = [addr for addr in self.memory_history if len(self.memory_history[addr]) > 0]
                if active_mem:
                    self.plot_memory_values(active_mem[:3])  # Plot first 3 active memory locations
                
            # Also show the combined dashboard if we have enough data
            if len(self.cycle_history) > 1:
                self.plot_all_stats()
            
        except Exception as e:
            print(f"Visualization error: {str(e)}. Continuing with text output...")