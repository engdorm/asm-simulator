from instruction import Instruction
from utils import num_lower, num_upper


def clean(program_lines):
  return [line.strip() for line in program_lines if line.strip()]


def preprocess(program_lines, mode):
  """ Goes through our instruction list and replaces any
  pseudo-instructions with actual instructions. Differs
  from the standard MIPS assembler in that we keep register
  keywords ($zero instead of converting to $0) and that we
  don't change all numbers to decimal (we assume all hex). """
  processed = []
  for line in program_lines:
    instr = Instruction(line)

    if mode == "MIPS":
      if instr.operation == "noop":
        instr.update("sll", "$zero", "$zero", "0x0")
      elif instr.operation == "mov":
        instr.update("add", instr.operand0, instr.operand1, "$zero")
      elif instr.operation == "clear":
        instr.update("add", instr.operand0, "$zero", "$zero")
      elif instr.operation == "not":
        instr.update("nor", instr.operand0, instr.operand1, "$zero")
      elif instr.operation == "la" or instr.operation == "li":
        val = int(instr.operand1, 16)
        if val < 65536:
          instr.update("addiu", instr.operand0, "$zero", instr.operand1)
        else:
          instr.update("lui", instr.operand0, num_upper(val), instr.operand2)
          processed.append(str(instr))
          instr.update("ori", instr.operand0, instr.operand0, num_lower(val))
      elif instr.operation == "bge":
        label = instr.operand2
        instr.update("slt", "$at", instr.operand0, instr.operand1)
        processed.append(str(instr))
        instr.update("beq", instr.operand0, "$zero", label)
      elif instr.operation == "bgt":
        label = instr.operand2
        instr.update("slt", "$at", instr.operand1, instr.operand0)
        processed.append(str(instr))
        instr.update("bne", instr.operand0, "$zero", label)
      elif instr.operation == "ble":
        label = instr.operand2
        instr.update("slt", "$at", instr.operand1, instr.operand0)
        processed.append(str(instr))
        instr.update("beq", instr.operand0, "$zero", label)
      elif instr.operation == "blt":
        label = instr.operand2
        instr.update("slt", "$at", instr.operand0, instr.operand1)
        processed.append(str(instr))
        instr.update("bne", instr.operand0, "$zero", label)
      elif instr.operation == "b":
        instr.update("beq", "$zero", "$zero", instr.operand0)
      elif instr.operation == "bal":
        instr.update("bgezal", "$zero", instr.operand0, instr.operand2)
      elif instr.operation == "blez":
        label = instr.operand1
        instr.update("slt", "$at", "$zero", instr.operand0)
        processed.append(str(instr))
        instr.update("beq", instr.operand0, instr.operand1, label)
      elif instr.operation == "bgtu":
        label = instr.operand2
        instr.update("sltu", "$at", instr.operand1, instr.operand0)
        processed.append(str(instr))
        instr.update("bne", instr.operand0, "$zero", label)
      elif instr.operation == "bgtz":
        label = instr.operand1
        instr.update("slt", "$at", "$zero", instr.operand0)
        processed.append(str(instr))
        instr.update("bne", instr.operand0, instr.operand1, label)
      elif instr.operation == "beqz":
        instr.update("beq", instr.operand0, "$zero", instr.operand1)
      elif instr.operation == "mul":
        output = instr.operand0
        instr.update("mult", instr.operand1, instr.operand2, None)
        processed.append(str(instr))
        instr.update("mflo", output, None, None)
      elif instr.operation == "div" or instr.operation == "rem": # add bne and break, like MARS, to check for no div by 0?
        output = instr.operand0
        isrem = instr.operation == "rem"
        instr.update("div", instr.operand1, instr.operand2, None)
        processed.append(str(instr))
        instr.update(["mflo", "mfhi"][int(isrem)], output, None, None)
      processed.append(str(instr))

    elif mode == "ARM":
      # TODO
      pass

  return processed


def label_positions(program_lines):
  """ Creates a dict of label positions for use in jumping and branching. """
  labels = {}
  cur_line = 0
  for line in program_lines:
    word = line.split(" ")[0]
    if word[-1] == ":":
      labels[word[:-1]] = cur_line
    cur_line += 1
  return labels


if __name__ == "__main__":
  example = ".text\n\nmain:\n  li $t1, 5\n  li $t2, 0x3BF20\n".split("\n")
  print(example)
  print(clean(example))
  print(preprocess(clean(example), "MIPS"))
