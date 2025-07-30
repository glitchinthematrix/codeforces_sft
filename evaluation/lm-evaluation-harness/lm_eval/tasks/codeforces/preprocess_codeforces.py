instruction_prefix = """You are a Python expert tasked with solving a coding problem. When solving the problem:
1. Think step‑by‑step but output the final Python code wrapped in one block of ```python …```.
2. The final code should be fully executable by a main() function that reads from stdin and writes to stdout in the specified formats.
3. Use only the Python Standard Library and list any imports at top.
4. Name functions/variables clearly; do not hard‑code or memorize answers.
5. Do not write test cases for the code outside the code block.
6. Include the standard entry‑point guard:
   ```python
   if __name__ == "__main__":
       main()
   ```
The question is as follows:
"""
instruction_suffix = """
Let's think step by step:
"""

def doc_to_text(doc) -> str:
    
    title = doc['title']
    description = doc['description']
    input_format = doc['input_format']
    output_format = doc['output_format']
    if 'examples' in doc:
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
        
    return f"{instruction_prefix}\n{title}: {description}\nInput Format: {input_format}\nOutput Format: {output_format}\nExample Inputs:\n{example_inputs}\nExample Outputs:\n{example_outputs}\n{instruction_suffix}"

def doc_to_target(doc) -> int:
    
    return 0
