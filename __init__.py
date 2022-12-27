import builtins
import sys
import threading

class CodeExecutor:
    def __init__(self):
        self.ALLOWED_LIBRARIES = []
        self.environment = {}
        for library in self.ALLOWED_LIBRARIES:
            try:
                # Split the library name and function name
                parts = library.split('.')
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

    
    def execute_code_thread(self, code: str) -> dict:
        thread = threading.Thread(target=self.execute_code, args=(code,))
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

# Now you can use the CodeExecutor class like this:
#executor = CodeExecutor()
#executor.add_allowed_library('lib.func', 'lib', 'math', 'time.sleep')
#executor.execute_code(executor.get_code())
# Run the code in a separate thread
#executor.execute_code_thread(executor.get_code())