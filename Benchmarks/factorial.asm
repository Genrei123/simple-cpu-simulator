; Factorial of 5 (using only ADD/SUB/LOAD/STORE/CLR)
; Initialize memory[0] = 5 (n=5)
LOAD R1 0       ; R1 = 5 (from memory[0])
LOAD R2 1       ; R2 = 1 (constant)
STORE R1 1      ; Save original n in memory[1] (optional)

; Compute 5! = 5 * 4 * 3 * 2 * 1
; Since no MUL, we use repeated addition

; Step 1: R3 = R1 * R2 (5 * 1 = 5)
CLR R3          ; R3 = 0
ADD R3 R3 R1    ; R3 = 0 + 5 = 5

; Step 2: R4 = R3 * (R1 - 1) = 5 * 4 = 20
CLR R4          ; R4 = 0
SUB R5 R1 R2    ; R5 = R1 - 1 = 4
ADD R4 R4 R3    ; R4 = 0 + 5 = 5
ADD R4 R4 R3    ; R4 = 5 + 5 = 10
ADD R4 R4 R3    ; R4 = 10 + 5 = 15
ADD R4 R4 R3    ; R4 = 15 + 5 = 20

; Step 3: R6 = R4 * (R5 - 1) = 20 * 3 = 60
CLR R6          ; R6 = 0
SUB R7 R5 R2    ; R7 = R5 - 1 = 3
ADD R6 R6 R4    ; R6 = 0 + 20 = 20
ADD R6 R6 R4    ; R6 = 20 + 20 = 40
ADD R6 R6 R4    ; R6 = 40 + 20 = 60

; Step 4: R8 = R6 * (R7 - 1) = 60 * 2 = 120
CLR R8          ; R8 = 0
SUB R9 R7 R2    ; R9 = R7 - 1 = 2
ADD R8 R8 R6    ; R8 = 0 + 60 = 60
ADD R8 R8 R6    ; R8 = 60 + 60 = 120

; Final result: 120 (stored in R8)
STORE R8 2      ; memory[2] = 120 (5!)