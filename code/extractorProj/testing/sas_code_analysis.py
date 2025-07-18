#!/usr/bin/env python3
"""
SAS Code Analysis Script
Analyzes the provided SAS code and extracts information for specified columns
"""

import re
import pandas as pd
from typing import List, Dict, Any

def analyze_sas_code():
    """
    Analyze the SAS code from testfile3.sas and extract information for specified columns
    """
    
    # Read the SAS file content
    with open(r'c:\Users\ferie\Documents\ferielWork\Summer_Intership\EY_25\Projets\Migration to Viya\code\extractorProj\testing\SAS Files\testfile3.sas', 'r') as f:
        sas_content = f.read()
    
    # Initialize results list
    results = []
    
    # Split content into lines for line-by-line analysis
    lines = sas_content.split('\n')
    
    # Analysis patterns
    patterns = {
        'proc_sql': r'proc\s+sql',
        'data_step': r'data\s+([^;]+)',
        'proc_step': r'proc\s+(\w+)',
        'macro_def': r'%macro\s+(\w+)',
        'macro_call': r'%(\w+)\s*\(',
        'let_statement': r'%let\s+(\w+)',
        'libname': r'libname\s+(\w+)',
        'filename': r'filename\s+(\w+)',
        'set_statement': r'set\s+([^;]+)',
        'merge_statement': r'merge\s+([^;]+)',
        'output_statement': r'output\s+([^;]*)',
        'create_table': r'create\s+table\s+(\w+)',
        'select_from': r'select\s+.*from\s+([^;\s]+)',
        'connect_to': r'connect\s+to\s+(\w+)',
        'execute_statement': r'execute\s*\(',
        'file_statement': r'file\s+(\w+)',
        'put_statement': r'put\s+',
        'include_statement': r'%include\s+',
        'where_clause': r'where\s+',
        'options_statement': r'options\s+',
        'quit_statement': r'quit\s*;',
        'run_statement': r'run\s*;'
    }
    
    # Process each line
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('/*'):
            continue
            
        # Initialize row data
        row_data = {
            'statement': line,
            'output_table': '',
            'WRITE_BACK': 'FALSE',
            'write_back_type': '',
            'file_path': '',
            'INCLUDE_PATH': '',
            'DEPENDENCY_EXISTS': 'FALSE',
            'LET_STATEMENT': 'FALSE',
            'MACRO_CALL': 'FALSE',
            'tables_sourcejoin': '',
            'referenced_table': '',
            'libref': '',
            'MISSING_CONNECTION': 'FALSE',
            'connection_issue': '',
            'Input tables': '',
            'import proc': '',
            'PROC_SQL': 'FALSE',
            'export proc': '',
            'DB_CONNECTION': 'FALSE',
            'connection_type': '',
            'engine': '',
            'connection_name': '',
            'libname_connections': '',
            'sql_connections': ''
        }
        
        # Analyze each pattern
        
        # PROC SQL detection
        if re.search(patterns['proc_sql'], line, re.IGNORECASE):
            row_data['PROC_SQL'] = 'TRUE'
            row_data['import proc'] = 'PROC SQL'
        
        # DATA step detection
        data_match = re.search(patterns['data_step'], line, re.IGNORECASE)
        if data_match:
            output_datasets = data_match.group(1).strip()
            if output_datasets != '_null_':
                row_data['output_table'] = output_datasets
                row_data['WRITE_BACK'] = 'TRUE'
                row_data['write_back_type'] = 'DATA_STEP'
        
        # PROC step detection
        proc_match = re.search(patterns['proc_step'], line, re.IGNORECASE)
        if proc_match:
            proc_name = proc_match.group(1).upper()
            if proc_name in ['EXPORT', 'PRINT', 'REPORT']:
                row_data['export proc'] = proc_name
                row_data['WRITE_BACK'] = 'TRUE'
                row_data['write_back_type'] = 'PROC_EXPORT'
            elif proc_name in ['IMPORT', 'MEANS', 'FREQ', 'CONTENTS']:
                row_data['import proc'] = proc_name
        
        # Macro definition
        macro_def_match = re.search(patterns['macro_def'], line, re.IGNORECASE)
        if macro_def_match:
            row_data['MACRO_CALL'] = 'TRUE'
        
        # Macro call
        macro_call_match = re.search(patterns['macro_call'], line, re.IGNORECASE)
        if macro_call_match:
            row_data['MACRO_CALL'] = 'TRUE'
        
        # Let statement
        if re.search(patterns['let_statement'], line, re.IGNORECASE):
            row_data['LET_STATEMENT'] = 'TRUE'
        
        # LIBNAME statement
        libname_match = re.search(patterns['libname'], line, re.IGNORECASE)
        if libname_match:
            libref = libname_match.group(1)
            row_data['libref'] = libref
            row_data['DB_CONNECTION'] = 'TRUE'
            row_data['libname_connections'] = libref
            
            # Check for connection type/engine
            if 'odbc' in line.lower():
                row_data['connection_type'] = 'ODBC'
                row_data['engine'] = 'ODBC'
            elif 'oracle' in line.lower():
                row_data['connection_type'] = 'Oracle'
                row_data['engine'] = 'Oracle'
            elif 'teradata' in line.lower():
                row_data['connection_type'] = 'Teradata'
                row_data['engine'] = 'Teradata'
        
        # FILENAME statement
        filename_match = re.search(patterns['filename'], line, re.IGNORECASE)
        if filename_match:
            # Extract file path
            path_match = re.search(r'"([^"]+)"', line)
            if path_match:
                row_data['file_path'] = path_match.group(1)
        
        # SET statement
        set_match = re.search(patterns['set_statement'], line, re.IGNORECASE)
        if set_match:
            input_tables = set_match.group(1).strip()
            row_data['Input tables'] = input_tables
            row_data['referenced_table'] = input_tables.split()[0]  # First table
            row_data['DEPENDENCY_EXISTS'] = 'TRUE'
        
        # MERGE statement
        merge_match = re.search(patterns['merge_statement'], line, re.IGNORECASE)
        if merge_match:
            merge_tables = merge_match.group(1).strip()
            row_data['Input tables'] = merge_tables
            row_data['tables_sourcejoin'] = merge_tables
            row_data['DEPENDENCY_EXISTS'] = 'TRUE'
        
        # CREATE TABLE statement
        create_match = re.search(patterns['create_table'], line, re.IGNORECASE)
        if create_match:
            table_name = create_match.group(1)
            row_data['output_table'] = table_name
            row_data['WRITE_BACK'] = 'TRUE'
            row_data['write_back_type'] = 'CREATE_TABLE'
        
        # SELECT FROM statement
        select_match = re.search(patterns['select_from'], line, re.IGNORECASE)
        if select_match:
            from_table = select_match.group(1).strip()
            row_data['Input tables'] = from_table
            row_data['referenced_table'] = from_table
            row_data['DEPENDENCY_EXISTS'] = 'TRUE'
        
        # CONNECT TO statement
        connect_match = re.search(patterns['connect_to'], line, re.IGNORECASE)
        if connect_match:
            db_type = connect_match.group(1)
            row_data['DB_CONNECTION'] = 'TRUE'
            row_data['connection_type'] = db_type.upper()
            row_data['engine'] = db_type.upper()
            row_data['sql_connections'] = db_type
        
        # File output detection
        if re.search(patterns['file_statement'], line, re.IGNORECASE):
            row_data['WRITE_BACK'] = 'TRUE'
            row_data['write_back_type'] = 'FILE_OUTPUT'
        
        # PUT statement (indicates file write)
        if re.search(patterns['put_statement'], line, re.IGNORECASE):
            row_data['WRITE_BACK'] = 'TRUE'
            row_data['write_back_type'] = 'FILE_WRITE'
        
        # Include statement
        if re.search(patterns['include_statement'], line, re.IGNORECASE):
            row_data['INCLUDE_PATH'] = 'TRUE'
        
        # Check for missing connection issues
        if 'oracle.customers' in line.lower() and 'connect' not in line.lower():
            row_data['MISSING_CONNECTION'] = 'TRUE'
            row_data['connection_issue'] = 'Implicit connection without explicit CONNECT'
        
        # Check for missing disconnect
        if 'disconnect' not in sas_content.lower() and 'connect to teradata' in sas_content.lower():
            if 'teradata' in line.lower():
                row_data['connection_issue'] = 'Missing DISCONNECT statement'
        
        # Only add non-empty rows
        if any(value not in ['', 'FALSE'] for value in row_data.values() if value != line):
            results.append(row_data)
    
    return results

def main():
    """Main function to run the analysis and create output"""
    
    print("Analyzing SAS code from testfile3.sas...")
    
    # Run analysis
    analysis_results = analyze_sas_code()
    
    # Create DataFrame
    df = pd.DataFrame(analysis_results)
    
    # Save to Excel
    output_file = r'c:\Users\ferie\Documents\ferielWork\Summer_Intership\EY_25\Projets\Migration to Viya\code\extractorProj\testing\sas_analysis_results.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"Analysis complete! Results saved to: {output_file}")
    print(f"Total rows analyzed: {len(analysis_results)}")
    
    # Print summary
    print("\n=== ANALYSIS SUMMARY ===")
    print(f"PROC SQL statements: {sum(1 for r in analysis_results if r['PROC_SQL'] == 'TRUE')}")
    print(f"Data steps with output: {sum(1 for r in analysis_results if r['WRITE_BACK'] == 'TRUE')}")
    print(f"Macro calls: {sum(1 for r in analysis_results if r['MACRO_CALL'] == 'TRUE')}")
    print(f"LET statements: {sum(1 for r in analysis_results if r['LET_STATEMENT'] == 'TRUE')}")
    print(f"Database connections: {sum(1 for r in analysis_results if r['DB_CONNECTION'] == 'TRUE')}")
    print(f"Dependencies found: {sum(1 for r in analysis_results if r['DEPENDENCY_EXISTS'] == 'TRUE')}")
    print(f"Missing connections: {sum(1 for r in analysis_results if r['MISSING_CONNECTION'] == 'TRUE')}")
    
    return df

if __name__ == "__main__":
    df = main()
