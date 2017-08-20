#PyForth.py is only compatible with version 3!

from sys import argv# Get command line arguements, for file running purposes.
stack = []
executing = True

#These are any functions needed for primitives that can't be lambdas.
def stackshow():
  print("<{}> {}".format(len(stack), stack)) # Just print the entire stack, with some formatting.
def forthcomp(operator):
    exec('''
if stack.pop() {} stack.pop():
    stack.append(1)
else:
    stack.append(0)'''.format(operator))
def end(exitMsg = "Bye."):
  global executing # Need to have executing global. There's no way to avoid it, best practices or not.
  print(exitMsg) # Print the exit message.
  executing = False # Turn executing off, so that way we don't evaluate any more FORTH calls.
# The collection of primitives. Mostly lambdas, but there is some calls to the functions above.
primitives = {
  '.s': stackshow, # Show the stack.
  '.': lambda: print(stack.pop()), # Print the top off the stack.
  '+': lambda: stack.append(stack.pop() + stack.pop()),
  '-': lambda: stack.append(stack.pop() - stack.pop()),
  '*': lambda: stack.append(stack.pop() * stack.pop()),
  '/': lambda: stack.append(stack.pop() / stack.pop()),
  '^': lambda: stack.append(stack.pop() ** stack.pop()),
  '=': lambda: forthcomp("=="),
  '>': lambda: forthcomp(">"),
  '<': lambda: forthcomp("<"),
  '>=': lambda: forthcomp('>='),
  '<=': lambda: forthcomp('<='),
  'bye': end,
  'emit': lambda: print(chr(stack.pop())),
}
variables = {
  
}
# The collection of user defined words and bootstrapped words. It's actually executed in the same way as REPL code.
word_dict = {
  'swap': '! swap-top ! swap-bottom @ swap-top @ swap-bottom', # swap. It works without variable definiton because of a quirk of !
  'dup': '! dup-value @ dup-value @ dup-value', # dup works on similar logic to above.
}

def parse(string):
  return string.lower().split()

def forth_eval(parsed_array):
  line_ptr = 0
  while line_ptr < len(parsed_array):
    word = parsed_array[line_ptr] # Create "word" as equal to the current word pointed to. 
    try: int(word) # Check if the word is an integer.
    except ValueError: # If the word isn't an integer, then move onto the next part of compilation
      try: word_dict[word] # Check if it's a user defined word.
      except KeyError:
          try: primitives[word] # Check if it's a primitive, since users can redefine primitves.
          except KeyError:
            if word == ":": # Check and see if it's the start of a function definition.
              line_ptr += 1
              function_name = parsed_array[line_ptr]
              code_str = ""
              line_ptr += 1
              while parsed_array[line_ptr] != ";":
                code_str += parsed_array[line_ptr]
                code_str += " "
                line_ptr += 1
              word_dict[function_name] = code_str
              line_ptr += 1
            elif word == "variable":
              line_ptr += 1 # Force the pointer ahead so the pointer isn't tread as code.
              variables[parsed_array[line_ptr]] = 0; # Create a variable.
            elif word == "@":
              line_ptr += 1 # Force the pointer ahead so the variable isn't treated as code.
              stack.append(variables[parsed_array[line_ptr]]) # Append the value of the variable.
            elif word == "!": # This is the "setter" command for the variable.
              line_ptr += 1
              variables[parsed_array[line_ptr]] = stack.pop() # It sets a given variable to the top of the stack.
            elif word == "if": # The "if" statement. Quite possibly the most important command.
              line_ptr += 1 # Make sure the IF isn't interpreted.
              code_str = "" # Create the later evaluated code_str.
              boolean = stack.pop()
              if boolean == 0:
                while parsed_array[line_ptr] != "else":
                  line_ptr += 1
                line_ptr += 1
                while parsed_array[line_ptr] != "then":
                  code_str += parsed_array[line_ptr]
                  code_str += " "
                  line_ptr += 1
              else:
                while parsed_array[line_ptr] != "else":
                  code_str += parsed_array[line_ptr]
                  code_str += " "
                  line_ptr += 1
                while parsed_array[line_ptr] != "then":
                  line_ptr += 1
              forth_eval(parse(code_str))
            elif word == '."':
              line_ptr += 1
              string = ""
              while parsed_array[line_ptr] != '"':
                string += parsed_array[line_ptr] + " "
                line_ptr += 1
              print(string)
            elif word == 's"':
              line_ptr += 1
              string = ""
              while parsed_array[line_ptr] != '"':
                string += parsed_array[line_ptr] + " "
                line_ptr += 1
              stack.append(string)
            else:
              print("Undefined Word at {}".format(word)) # This is the undef'd error message.
          else:
            forth_eval(parse(word_dict[word])) # If it is a user defined word, execute it as code.
      else:
        primitives[word]() # If it is a primitive, run it.
    else: # if it IS a number, add it to the stack.
      stack.append(int(word))
    line_ptr += 1 # Continue the loop!
def main_loop():
  while executing:
    try: forth_eval(parse(input("pyforth>")))
    except IndexError:
      print("Stack Error!")
      stack.append(-127)

if __name__ == "__main__":
  if len(argv) == 1:
    main_loop()
  else:
    file = open(argv[1], 'r')
    forth_eval(parse(file.read()))
    main_loop()

