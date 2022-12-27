# CodeExecutor utility!

## Introduction
The CodeExecutor is a utility for executing arbitrary Python code in a restricted environment. It allows you to specify a list of allowed libraries or functions that can be imported and used in the code being executed, and provides an easy way to execute code snippets or files in a controlled and isolated environment.

Installation
To install the CodeExecutor utility, you can clone this repository and use pip to install the package:

```
pip install CodeExecutor
```
## Usage
Here's an example of how you might use the CodeExecutor class:
```
from code_executor import CodeExecutor

# First, create an instance of the CodeExecutor class
executor = CodeExecutor()

# Optionally, add any allowed libraries or functions that you want to make available
# For example, to allow the use of the math and time.sleep functions:
executor.add_allowed_library('math', 'time.sleep')

# To execute some code, you can pass it as a string to the execute_code() method:
code = '''
import math

result = math.sqrt(16)
print(result)
'''
executor.execute_code(code)
# Output: 4.0

# You can also execute code in a separate thread by calling the execute_code_thread() method:
executor.execute_code_thread(code)

# To read code from a file, you can use the get_code() method:
code = executor.get_code()
executor.execute_code(code)
```
The `execute_code()` and `execute_code_thread()` methods both return a dictionary containing the environment in which the code was executed. This can be useful for inspecting the values of variables or functions defined in the code.
Note that the CodeExecutor includes a method that raises an ImportError if an attempt is made to import a library or module that is not in the list of allowed libraries. This helps to prevent malicious code from importing external libraries or accessing sensitive information.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
We welcome contributions to the CodeExecutor utility! If you have an idea for a new feature or bug fix, please open an issue or pull request on GitHub.
