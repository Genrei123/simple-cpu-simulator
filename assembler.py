def assemble(file):
    SUPPORTED_OPS = ["ADD", "SUB", "LOAD", "STORE", "CLR"]
    # Read lines, strip whitespace, and remove comments
    instructions = []
    with open(file, 'r') as f:
        for line in f:
            # Remove inline comments and strip
            line = line.split(';', 1)[0].strip()
            if line:  # Only process non-empty lines
                instructions.append(line)
    
    # Process each instruction
    processed = []
    for instr in instructions:
        parts = instr.split()
        op = parts[0]
        if op not in SUPPORTED_OPS:
            raise ValueError(f"Unsupported instruction: {op}")
        
        # Convert register names to indices (R1 → 1) and keep as a single string
        args = [x[1:] if x.startswith('R') else x for x in parts[1:]]
        processed.append(" ".join([op] + args))  # e.g., "LOAD 1 0"
    
    return processed, []