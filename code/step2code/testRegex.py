import re
import sys
import os
from typing import List, Tuple

KEYWORDS = [
    r'%let\b', r'%macro\b', r'%mend\b', r'libname\b', r'proc\b', r'data\b',
    r'set\b', r'merge\b', r'%include\b', r'filename\b', r'create\s+table\b', r'connect\s+to\b'
]
KEYWORD_RE = re.compile(r'^\s*(' + '|'.join(KEYWORDS) + r')', re.IGNORECASE)

def split_sas_statements_robust(sas_text: str) -> List[Tuple[str, int]]:
    """
    Robustly splits SAS code into statements.
    Handles:
        - Missing semicolons
        - Nested macros
        - Quoted strings and parentheses
        - Keyword-based recovery
    Returns:
        List of (statement_text, starting_line)
    """
    statements = []
    current = []
    paren_count = 0
    in_single_quote = False
    in_double_quote = False
    line_number = 1
    stmt_start_line = 1
    prev_stmt_keyword = None

    lines = sas_text.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        lowered = stripped.lower()

        # Track quotes and parens across lines
        for char in line:
            current.append(char)
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == '(' and not in_single_quote and not in_double_quote:
                paren_count += 1
            elif char == ')' and not in_single_quote and not in_double_quote:
                paren_count = max(0, paren_count - 1)

        # Handle semicolon-terminated statements
        if ';' in line and not in_single_quote and not in_double_quote and paren_count == 0:
            joined = ''.join(current).strip()
            parts = joined.split(';')
            for part in parts[:-1]:
                stmt = part.strip() + ';'
                if stmt:
                    statements.append((stmt, stmt_start_line))
            # Start building the next statement
            current = [parts[-1]]
            stmt_start_line = i + 1
            continue

        # Fallback: keyword on new line while previous has no semicolon
        if (KEYWORD_RE.match(stripped)
                and current
                and not ''.join(current).strip().endswith(';')):
            # Consider what's already in buffer as one statement
            stmt = ''.join(current).strip()
            if stmt:
                statements.append((stmt, stmt_start_line))
            current = []
            current.append(line)
            stmt_start_line = i + 1
        elif i == len(lines) - 1:
            # End of file
            stmt = ''.join(current).strip()
            if stmt:
                statements.append((stmt, stmt_start_line))

        line_number += 1

    return statements

def process_sas_file(file_path: str) -> None:
    """
    Process a SAS file and print the statements.
    
    Args:
        file_path: Path to the SAS file
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            sas_content = f.read()
            
        statements = split_sas_statements_robust(sas_content)
        
        print(f"\nProcessed {file_path}")
        print(f"Found {len(statements)} statements")
        
        for i, (stmt, line) in enumerate(statements[:10], 1):
            # Print first 50 chars of each statement
            print(f"Statement {i} (line {line}): {stmt[:50]}{'...' if len(stmt) > 50 else ''}")
        
        if len(statements) > 10:
            print(f"... and {len(statements) - 10} more statements")
    
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_sas_file(sys.argv[1])
    else:
        print("Usage: python testRegex.py path/to/sas_file.sas")
        print("Please provide a SAS file path as argument.")