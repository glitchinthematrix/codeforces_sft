

def doc_to_text(doc) -> str:
    
    title = doc['title']
    description = doc['description']
    input_format = doc['input_format']
    output_format = doc['output_format']

    instruction_prefix = """You are a competitive programming tutor tasked with solving a coding problem in C++. When solving the problem:
    1. Think step‑by‑step but output the final C++ code wrapped in one block of ```cpp <code here>```.
    2. The final code should be fully executable by a main() function that reads from stdin and writes to stdout in the specified formats.
    3. Use only the C++ Standard Library and list any imports at top.
    4. Name functions/variables clearly; do not hard‑code or memorize answers.
    5. Do not write test cases for the code outside the code block. Do not repeat instructions.
    The question is as follows:
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
    instruction_suffix = """
    Let's think step by step:
    """
    return f"{instruction_prefix}\n{title}: {description}\n## Input Format: {input_format}\n## Output Format: {output_format}\n## Example Inputs:\n```inp\n{example_inputs}\n```\n## Example Outputs:\n```op\n{example_outputs}\n```\n ## Time limit per test case: {doc['time_limit']} seconds\n## Memory limit per test case: {doc['memory_limit']} MB\n{instruction_suffix}"

def doc_to_target(doc) -> int:
    
    return 0
