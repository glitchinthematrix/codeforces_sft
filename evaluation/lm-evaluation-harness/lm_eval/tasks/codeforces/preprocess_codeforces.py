

def doc_to_text(doc) -> str:
    
    title = doc['title']
    description = doc['description']
    input_format = doc['input_format']
    output_format = doc['output_format']

    instruction_prefix = """You are a competitive programming tutor tasked with solving a competitive programming problem.
(1) Please reason step by step about your solution approach, then provide a optimal algorithmic implementation in C++17 that is thoroughly optimized for both speed and memory usage.
(2) Your approach must use the data structures needed to process the largest possible test cases within the time and memory limits.
(3) Cleanly name functions and variables and specify all imports at top.
(4) Your solution must read input from standard input (cin), write output to standard output (cout) following the input and output format provided.
(5) Do not include any debug prints or additional output and do not memorize answers.
(6) Put your final solution within a single code block:
```cpp
<your code here>
```
## Problem
    """
    if doc['examples'] is not None:
        if 'input' in doc['examples'][0]:
            example_inputs = doc['examples'][0]['input']
        else:
            example_inputs = ""
        if 'output' in doc['examples'][0]:
            example_outputs = doc['examples'][0]['output']
        else:
            example_outputs = ""
    else:
        example_inputs = ""
        example_outputs = ""
    note = doc['note'] if doc['note'] else "None"
    return f"{instruction_prefix}\n{title}: {description}\n## Input Format\n {input_format}\n## Output Format\n {output_format}\n## Examples\n```input\n{example_inputs}\n```\n```output\n{example_outputs}\n```\n## Constraints\nTime limit per test case: {doc['time_limit']} seconds\nMemory limit per test case: {doc['memory_limit']} MB\n## Note\n{note}"

def doc_to_target(doc) -> int:
    
    return 0
