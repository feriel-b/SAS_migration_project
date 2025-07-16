import re
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

# 1) Utility: Read & Pre-clean

def _remove_comments(text: str) -> str:
    """
    A more robust function to remove SAS comments while respecting strings.
    """
    # Pattern for SAS comments (block and line) and strings
    pattern = re.compile(
        r'/\*.*?\*/'  # Block comments
        r'|\'(?:[^\']|\'\')*?\''  # Single-quoted strings
        r'|\"(?:[^\"]|\"\")*?\"'  # Double-quoted strings
        r'|^\s*\*[^;]*;',  # Star-style line comments
        re.DOTALL | re.MULTILINE
    )
    
    def replacer(match):
        # If the match is a comment, replace it with a space. Otherwise, keep the string.
        s = match.group(0)
        if s.startswith('/'):
            return ' '
        if s.startswith('*'):
            return ''
        else:
            return s

    return re.sub(pattern, replacer, text)

def load_sas_file(filepath: str) -> Tuple[str, List[str]]:
    """
    Load a SAS file, remove block comments, and return cleaned text and original lines.
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()
    
    text_no_comments = _remove_comments(raw_text)
    return text_no_comments, raw_text.splitlines()



#### split more specific for each sas keyword : let, proc, libname, macro, include, etc.
def split_sas_statements(sas_text: str) -> List[Tuple[str, int]]:
    """
    Split text into approximate statements by semicolon.
    Returns a list of (statement, start_line_number).
    Handles quotes and parentheses.
    """
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    paren_count = 0
    line_number = 1
    stmt_start_line = 1

    for idx, char in enumerate(sas_text):
        current.append(char)
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == '(' and not in_single_quote and not in_double_quote:
            paren_count += 1
        elif char == ')' and not in_single_quote and not in_double_quote and paren_count > 0:
            paren_count -= 1

        if char == '\n':
            line_number += 1

        if char == ';' and not in_single_quote and not in_double_quote and paren_count == 0:
            stmt_str = ''.join(current).strip()
            statements.append((stmt_str, stmt_start_line))
            current = []
            stmt_start_line = line_number

    # Catch anything leftover, that doesn't end with a semicolon
    if current:
        leftover = ''.join(current).strip()
        if leftover:
            statements.append((leftover, stmt_start_line))
    return statements

# 2) Regex Patterns


# Each pattern is documented with an example

# LIBNAME statement
libname_pattern = re.compile(
    r'\blibname\s+(\w+)\s+["\']([^"\']+)["\'](?:\s+(\w+))?', re.IGNORECASE
)  # Example: libname mylib 'C:/data';

# Macro definition start
macro_def_pattern = re.compile(
    r'\s*%macro\s+(\w+)\s*(?:\(([^)]*)\))?', re.IGNORECASE
)  # Example: %macro test(arg1, arg2);

# Macro end
macro_end_pattern = re.compile(
    r'\s*%mend\s*(\w*)', re.IGNORECASE
)  # Example: %mend test;

# Macro invocation/call
macro_call_pattern = re.compile(
    r'%(\w+)\s*\(([^;)]*)\)?', re.IGNORECASE
)  # Example: %my_macro(arg1, arg2);

# PROC statement
proc_pattern = re.compile(
    r'\bproc\s+(\w+)', re.IGNORECASE
)  # Example: proc sql;

# %LET variable assignment
let_pattern = re.compile(
    r'%let\s+(\w+)\s*=\s*([^;]+)', re.IGNORECASE
)  # Example: %let var = value;

# DB connection (libname with engine or proc sql connect)
db_conn_pattern = re.compile(
    r'libname\s+\w+\s+["\'][^"\']+["\']\s+\w+|proc\s+sql.*?connect\s+to\s+\w+.*?',
    re.IGNORECASE | re.DOTALL
)

# SET/MERGE in DATA step (multi-table input)
input_set_merge_pattern = re.compile(
    r'\b(set|merge)\s+([^;]+?)(?=\s*(?:by|if|where|;))', re.IGNORECASE
)

# FROM in SQL
input_from_pattern = re.compile(
    r'\bfrom\s+((?:(?!\b(?:where|group|order|having|;)\b).)+)', re.IGNORECASE | re.DOTALL
)

# DATA statement (output table)
data_pattern = re.compile(
    r'\bdata\s+([^;]+?)(?=;)', re.IGNORECASE
)

# CREATE TABLE in PROC SQL
create_table_pattern = re.compile(
    r'\bcreate\s+table\s+([a-zA-Z0-9_.]+)', re.IGNORECASE
)

# PROC EXPORT output
proc_export_pattern = re.compile(
    r'\bproc\s+export.*?\bdata\s*=\s*([a-zA-Z0-9_.]+)', re.IGNORECASE | re.DOTALL
)

# 3) Extraction Logic


def extract_datasets(stmt: str, pattern: re.Pattern, table_type: str) -> List[Dict]:
    """
    Extract dataset names using provided pattern.
    Handles multiple tables per statement, skips options in parentheses.
    """
    tables = []
    match = pattern.search(stmt)
    while match:
        if table_type in ['SET', 'MERGE']:
            raw_list = match.group(2).split()
        else:
            raw_list = [match.group(1)]
        for ds in raw_list:
            ds_clean = ds.strip().split('(')[0]  # Remove anything after (
            if ds_clean and re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', ds_clean):
                tables.append({'type': table_type, 'table': ds_clean})
        match = pattern.search(stmt, match.end())
    return tables

def extract_macro_calls(stmt: str, line_number: int) -> List[Dict]:
    """
    Extract macro invocations (calls) from statement.
    """
    calls = []
    for match in macro_call_pattern.finditer(stmt):
        calls.append({
            'macro_name': match.group(1),
            'args': match.group(2),
            'line_number': line_number
        })
    return calls

def extract_sas_info(filepath: str) -> Dict[str, pd.DataFrame]:
    text_no_comments, original_lines = load_sas_file(filepath)
    statements = split_sas_statements(text_no_comments)

    libname_matches = []
    macro_stack = []
    macro_defs = []
    macro_calls = []
    proc_defs = []
    let_defs = []
    db_conns = []
    input_tables = []
    output_tables = []

    for stmt, stmt_line in statements:
        stmt_lower = stmt.lower()

        # 1) LIBNAME
        lib_m = libname_pattern.search(stmt)
        if lib_m:
            libname_matches.append({
                'libref': lib_m.group(1),
                'path': lib_m.group(2),
                'engine': lib_m.group(3),
            })

        # 2) Macro Start
        start_m = macro_def_pattern.search(stmt)
        if start_m:
            macro_stack.append({
                'name': start_m.group(1),
                'args': start_m.group(2),
            })

        # 3) Macro End
        end_m = macro_end_pattern.search(stmt)
        if end_m and macro_stack:
            macro = macro_stack.pop()
            macro['end_line'] = stmt_line
            macro_defs.append(macro)

        # 4) Macro Calls
        macro_calls.extend(extract_macro_calls(stmt, stmt_line))

        # 5) PROC
        proc_m = proc_pattern.search(stmt)
        if proc_m:
            proc_defs.append({'proc': proc_m.group(1), 'line_number': stmt_line})

        # 6) %LET
        for let_m in let_pattern.finditer(stmt):
            let_defs.append({
                'let_variable': let_m.group(1),
                'let_value': let_m.group(2).strip(),
                'line_number': stmt_line
            })

        # 7) DB connections
        db_m = db_conn_pattern.search(stmt)
        if db_m:
            db_conns.append({'connection_statement': db_m.group(0), 'line_number': stmt_line})

        # 8) Input tables: SET, MERGE, FROM
        input_tables.extend(extract_datasets(stmt, input_set_merge_pattern, 'SET'))
        input_tables.extend(extract_datasets(stmt, input_set_merge_pattern, 'MERGE'))
        input_tables.extend(extract_datasets(stmt, input_from_pattern, 'FROM'))

        # 9) Output tables: DATA, CREATE TABLE, PROC EXPORT
        output_tables.extend(extract_datasets(stmt, data_pattern, 'DATA'))
        output_tables.extend(extract_datasets(stmt, create_table_pattern, 'CREATE TABLE'))
        output_tables.extend(extract_datasets(stmt, proc_export_pattern, 'PROC EXPORT'))

    # Convert to DataFrames
    libname_df = pd.DataFrame(libname_matches)
    macro_df = pd.DataFrame(macro_defs)
    macro_call_df = pd.DataFrame(macro_calls)
    proc_df = pd.DataFrame(proc_defs)
    let_df = pd.DataFrame(let_defs)
    db_conn_df = pd.DataFrame(db_conns)
    input_tables_df = pd.DataFrame(input_tables).drop_duplicates()
    output_tables_df = pd.DataFrame(output_tables).drop_duplicates()

    return {
        "libname": libname_df,
        "macro": macro_df,
        "macro_calls": macro_call_df,
        "proc": proc_df,
        "let": let_df,
        "db_conn": db_conn_df,
        "input_tables": input_tables_df,
        "output_tables": output_tables_df
    }

def combine_results(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combine all result DataFrames into a single DataFrame with extracted_type column.
    Only keeps columns present in each DataFrame.
    """
    desired_order = [
        'extracted_type', 'libref', 'path', 'engine', 'name', 'args', 'start_line', 'end_line',
        'macro_name', 'proc', 'line_number', 'variable', 'value', 'connection_statement',
        'type', 'table'
    ]
    frames = []
    for key, df in results.items():
        if not df.empty:
            df = df.copy()
            df['extracted_type'] = key
            # Reorder columns
            cols = [col for col in desired_order if col in df.columns]
            df = df[cols + [c for c in df.columns if c not in cols]]
            frames.append(df)
    if frames:
        df_all = pd.concat(frames, ignore_index=True)
    else:
        df_all = pd.DataFrame()
    return df_all

# Example usage

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract keywords/macros/statements from a SAS program.")
    parser.add_argument("sas_file", help="Path to the SAS program file.")
    args = parser.parse_args()

    # Extract info
    results = extract_sas_info(args.sas_file)

    # Print each section
    for section, df in results.items():
        print(f"\n--- {section.upper()} ---")
        print(df)

    # Combine all for Excel export
    df_all = combine_results(results)

    print("\n--- Combined Results ---")
    print(df_all)

    # Export to Excel
    df_all.to_excel("combined_results.xlsx", index=False)
    with pd.ExcelWriter("multiple_sheets.xlsx") as writer:
        for sheet_name, df_sheet in results.items():
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)