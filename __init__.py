import builtins
import sys
import threading
import ast
import importlib
import inline
import colorama
from colorama import Fore

class create_thread(threading.Thread): #Thread with .kill() method
  def __init__(self, *args, **keywords): 
    threading.Thread.__init__(self, *args, **keywords) 
    self.killed = False
  def start(self): 
    self.__run_backup = self.run 
    self.run = self.__run       
    threading.Thread.start(self) 

  def __run(self): 
    sys.settrace(self.globaltrace) 
    self.__run_backup() 
    self.run = self.__run_backup 
  def globaltrace(self, frame, event, arg): 
    if event == 'call': 
      return self.localtrace 
    else: 
      return None

  def localtrace(self, frame, event, arg): 
    if self.killed: 
      if event == 'line': 
        raise SystemExit() 
    return self.localtrace 
  def kill(self): 
    self.killed = True


# Initialize colorama
colorama.init()

input = inline.input
input.autoCompleteOnEnter = True #maybe False?

VERSION = '1.0.0'

class CodeExecutor:
    def __init__(self):
        self.ALLOWED_LIBRARIES = []
        self.environment = {}
        # Create a dictionary to store the threads
        self.threads = {}
        self.counter = 0

    def close_all_threads(self, thread_number: int = None):
        """Close all threads"""
        # Cancel all threads
        if thread_number is None:
            # Interrupt all threads
            for thread in self.threads.values():
                thread.kill()
            self.threads.clear()
        else:
            # Interrupt the specific thread
            thread = self.threads.get(thread_number)
            print(thread)
            if thread:
                thread.kill()
                del self.threads[thread_number]
            else:
                print(f"Thread {thread_number} not found")

    def list_threads(self):
        """List all active threads"""
        print("Active threads:")
        for key, thread in self.threads.items():
            print(f" - Thread {key}: {thread.name}")

    def import_library(self, name: str, alias: str) -> object:
        """Import a library with a given alias"""
        # Import the library using importlib
        lib = importlib.import_module(name)

        # Return the library with the specified alias
        return {alias: lib}

    def _import_allowed_libraries(self):
        """Import the allowed libraries or functions into the environment"""
        for library in self.ALLOWED_LIBRARIES:
            # Split the library name and function name
            parts = library.split('.')

            # Check if the library name has an alias
            if 'as' in parts[0]:
                # Split the library name and alias
                lib_parts = parts[0].split()
                # Import the library using the import_library function
                self.environment.update(self.import_library(lib_parts[0], lib_parts[-1]))
            else:
                try:
                    if len(parts) == 1:
                        # Import the entire library
                        self.environment[library] = __import__(library)
                    else:
                        # Import the specific function
                        lib = __import__(parts[0])
                        self.environment[parts[1]] = getattr(lib, parts[1])
                except ImportError:
                    print(f"Could not import library '{library}'")

    def restricted_import(name: str, *args, **kwargs):
        raise ImportError(f"Importing external library '{name}' is not allowed")

    def add_allowed_library(self, *libraries: str):
        """Add allowed libraries or functions to the list and import them into the environment"""
        self.ALLOWED_LIBRARIES.extend(libraries)
        self._import_allowed_libraries()

    def execute_code(self, code: str) -> dict:
        if self.restricted_import != builtins.__import__:
            builtins.__import__ = self.restricted_import
        try:
            code_obj = compile(code, '<string>', 'exec')
        except SyntaxError as e:
            print("Invalid syntax:\n -", e)
            return self.environment
        try:
            exec(code_obj, self.environment)
        except ImportError:
            print("Importing external libraries is not allowed")
        except NameError as e:
            if e.name in sys.modules:
                print(f"Library '{e.name}' is not imported")
            else:
                print(f"Unknown variable: '{e.name}'")
        except ZeroDivisionError:
            print("Division by zero")
        except Exception as e:
            print(f"An error occurred:\n - {e}")
        else:
            print("\n- The code was executed successfully.")
        
        return self.environment

    def execute_code_thread(self, code: str, thread_number: int = None) -> dict:
        """Execute the code in a separate thread"""
        # Create a new thread
        thread = create_thread(target=self.execute_code, args=(code,))
        if thread_number is None:
            # Generate a new thread number
            thread_number = len(self.threads) + 1
        # Add the thread to the dictionary
        self.threads[thread_number] = thread
        # Start the thread
        thread.start()

        return self.environment

    def get_code(self):
        name = input("Path to file: ")
        try:
            with open(name, 'r') as f:
                return f.read()
        except:
            print("Couldn't find the file, try again:")
            return self.get_code()

    def analyze(self, code: str) -> dict:
        """Count the number of functions and variables and calls used in the code"""
        # Parse the code into an AST tree
        tree = ast.parse(code)

        # Initialize counters
        function_count = 0
        variable_count = 0
        call_count = 0

        # Iterate over the AST nodes
        for node in ast.walk(tree):
            # Increment the function count for FunctionDef nodes
            if isinstance(node, ast.FunctionDef):
                function_count += 1
            # Increment the variable count for Assign nodes
            elif isinstance(node, ast.Assign):
                variable_count += 1
            # Increment the call count for Call nodes
            elif isinstance(node, ast.Call):
                call_count += 1

        # Return the counts as a dictionary
        return {'functions': function_count, 'variables': variable_count, 'calls': call_count}



code = '''
#a = np.array([1, 2, 3])
#print(a)
while True:
    #print(1)
    sleep(1)
'''

# Now you can use the CodeExecutor class like this:
executor = CodeExecutor()
executor.add_allowed_library('math', 'time.sleep', 'numpy as np', 'cv2')
print("Info about code:", executor.analyze(code=code))
#executor.execute_code(executor.get_code())
#executor.execute_code(code)
# Run the code in a separate thread
#executor.execute_code_thread(executor.get_code())
executor.execute_code_thread(code)


COMMANDS_HELP = {
        "Close": "Close all threads or a specific thread by its number",
        "Exit": "Exit the program",
        "Libraries": "List all available libraries and functions",
        "Threads": "List all active threads",
        "Version": "Show the version of the CodeExecutor library"
    }



inline.commands = ["Help", "Close", "Version", "Exit", "Threads", "Libraries"] # All .lower() / Autocomplete to path #presstabforac if autocomplete != textinput
for command in COMMANDS_HELP:
    inline.commands.append(command + " /?")

print(inline.commands)

def help(command: str):
    """Print the help message for a specific command"""
    description = COMMANDS_HELP.get(command)
    if description:
        print(f"{command}: {description}")
    elif command == "":
        for command in COMMANDS_HELP:
            print(f"{Fore.CYAN}{command}{Fore.RESET} -", COMMANDS_HELP[command])
    else:
        print(f"Command '{command}' not found")

while True:
    # Get user input
    command = input('Enter a command: ', free=False)

    # Check if the user entered the 'help' command
    if 'Help' in command:
        # Print a list of available commands
        command = command[4:].strip()
        help(command)
    elif "/?" in command:
        command = command[:-3].strip()
        help(command)

    # Check if the user entered the 'run' command
    elif command == 'Run':
        # Get the code to be executed
        code = input('Enter the code to be executed: ')
        # Execute the code
        executor.execute_code_thread(code)

    # Check if the user entered the 'exit' command
    elif command == 'Exit':
        # Exit the program
        break

    elif command == 'Close':
        if not executor.threads:
            print("There are no running threads to close.")
            continue
        # Print the list of threads
        for thread_number, thread in executor.threads.items():
            print(f"{thread_number}: {thread.name}")
        # Get the thread number from the user
        cmds = ['All']
        for i in range(len(executor.threads)):
            cmds.append(str(i+1))
        thread_number = input("Enter the number of the thread to close (or 'all' to close all threads): ", command=cmds, free=False)
        if thread_number.lower() == 'all':
            # Close all threads
            executor.close_all_threads()
        else:
            try:
                # Convert the input to an integer
                thread_number = int(thread_number)
                # Close the specific thread
                executor.close_all_threads(thread_number=thread_number)
            except (ValueError, IndexError):
                print("Invalid thread number")

    elif command == 'version':
        # Print the version of the CodeExecutor library
        print(f"CodeExecutor version: {VERSION}")

    elif command == 'Threads':
        # Print the list of active threads
        for thread_number, thread in executor.threads.items():
            status = "Running" if thread.is_alive() else "Stopped"
            print(f"Thread {thread_number}: {status}")

    elif command == 'Libraries':
        # Get the list of allowed libraries
        libraries = [l for l in executor.ALLOWED_LIBRARIES if '.' not in l]
        # Get the list of allowed functions
        functions = [f.split('.')[-1] for f in executor.ALLOWED_LIBRARIES if '.' in f]

        # Print the list of allowed libraries in green
        print(f"{Fore.GREEN}Allowed libraries: {', '.join(libraries)}")
        # Print the list of allowed functions in red
        print(f"{Fore.CYAN}Allowed functions: {', '.join(functions)}")