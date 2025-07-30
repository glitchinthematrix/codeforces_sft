import re
import sys
import io
import subprocess
import tempfile
import os
import time
import resource
from contextlib import redirect_stdout

def run_tests(code, official_tests, checker_fn, time_limit: float, memory_limit: int):
    # Extract Python code from markdown format
    code_match = re.search(r"```python(.*?)(```|$)", code, re.DOTALL)
    if code_match:
        code = code_match.group(1).strip()
    else:
        code = code.strip()
    # Check for compilation errors
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return {'status': 'CE', 'message': f'Compilation Error: {str(e)}'}
    except Exception as e:
        return {'status': 'CE', 'message': f'Compilation Error: {str(e)}'}
    
    # Run each test dict individually and collect all results
    test_results = []
    
    for test_idx, test in enumerate(official_tests):
        test_input = test['input'].strip()
        test_output = test['output'].strip()
        # Parse the input - first line should be number of test cases
        input_lines = test_input.split('\n')
        
        # Calculate memory limit for this test dict
        try:
            num_cases = int(input_lines[0])
            scaled_memory_limit = memory_limit * num_cases
            scaled_time_limit = time_limit * num_cases
        except (ValueError, IndexError):
            # If first line isn't a number, treat as single test case
            scaled_memory_limit = memory_limit
            scaled_time_limit = time_limit
        
        # Execute this test dict with constraints
        result = execute_with_constraints(code, test_input, scaled_time_limit, scaled_memory_limit)
        
        test_result = {'test_idx': test_idx + 1, 'input': test_input, 'expected': test_output}
        
        if result['timeout']:
            test_result.update({'status': 'TLE', 'message': f'Time Limit Exceeded on test {test_idx + 1}', 'actual': ''})
            
        elif result['memory_exceeded']:
            test_result.update({'status': 'MLE', 'message': f'Memory Limit Exceeded on test {test_idx + 1}', 'actual': ''})
               
        elif result['error']:
            test_result.update({'status': 'RE', 'message': f'Runtime Error on test {test_idx + 1}: {result["error"]}', 'actual': ''})
           
        else:
            actual_output = result['output'].strip()
            test_result['actual'] = actual_output
            
            # Check the result for this test dict
            if checker_fn is not None:
                check_result = run_checker(checker_fn, test_input, test_output, actual_output)
                if check_result['status'] != 'AC':
                    test_result.update({'status': check_result['status'], 'message': f'{check_result["message"]} (test {test_idx + 1})'})
                
                else:
                    test_result.update({'status': 'AC', 'message': f'Accepted (test {test_idx + 1})'})
            else:
                # Direct string comparison
                if actual_output != test_output.strip():
                    test_result.update({'status': 'WA', 'message': f'Wrong Answer on test {test_idx + 1}', 'actual': actual_output})
                
                else:
                    test_result.update({'status': 'AC', 'message': f'Accepted (test {test_idx + 1})', 'actual': actual_output})
        
        test_results.append(test_result)
    
    return test_results

def execute_with_constraints(code, input_data, time_limit, memory_limit):
    # Create temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        code_file = f.name
    
    try:
        # Prepare the command with memory limit using ulimit
        memory_kb = memory_limit * 1024  # Convert MB to KB
        cmd = [
            'bash', '-c', 
            f'ulimit -v {memory_kb}; python3 {code_file}'
        ]
        
        # Execute with timeout
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Create new process group for clean termination
        )
        
        try:
            stdout, stderr = process.communicate(input=input_data, timeout=time_limit)
            
            if process.returncode != 0:
                # Check if it's a memory error
                if 'MemoryError' in stderr or 'memory' in stderr.lower():
                    return {'output': '', 'error': None, 'timeout': False, 'memory_exceeded': True}
                return {'output': '', 'error': stderr, 'timeout': False, 'memory_exceeded': False}
            
            return {'output': stdout, 'error': None, 'timeout': False, 'memory_exceeded': False}
            
        except subprocess.TimeoutExpired:
            # Kill the entire process group
            os.killpg(os.getpgid(process.pid), 9)
            process.wait()
            return {'output': '', 'error': None, 'timeout': True, 'memory_exceeded': False}
            
    except Exception as e:
        return {'output': '', 'error': str(e), 'timeout': False, 'memory_exceeded': False}
    finally:
        if os.path.exists(code_file):
            os.unlink(code_file)

def run_checker(checker_fn, input_data, expected_output, actual_output):
    # Create temporary file for the checker function
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(checker_fn)
        checker_file = f.name
    
    try:
        # Run checker with the three arguments as specified
        cmd = ['python3', checker_file, input_data, expected_output, actual_output]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return {'status': 'AC', 'message': 'Accepted'}
        else:
            return {
                'status': 'WA', 
                'message': f'Wrong Answer (checker): {result.stderr.strip() or result.stdout.strip()}'
            }
            
    except subprocess.TimeoutExpired:
        return {'status': 'RE', 'message': 'Checker timeout'}
    except Exception as e:
        return {'status': 'RE', 'message': f'Checker error: {str(e)}'}
    finally:
        if os.path.exists(checker_file):
            os.unlink(checker_file)