import re
import pandas as pd
import glob
import os
from typing import List, Dict, Any, Optional, Tuple
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SASAnalyzer:
    """
    Enhanced SAS code analyzer with improved regex patterns and error handling.
    """
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns with improvements from the review."""
        
        # 1. LIBNAME statement - handles quoted paths, engines, options
        self.libname_pattern = re.compile(
            r'\blibname\s+(\w+)\s+(?:'
            r'(\([^)]+\))|'  # Temporary library reference
            r'(["\'][^"\']*["\'])|'  # Quoted path
            r'(\w+)'  # Engine or unquoted identifier
            r')\s*([^;]*)?;',
            re.IGNORECASE | re.DOTALL
        )
        
        # 2. Macro definition - handles parameters, nested parens, options
        self.macro_def_pattern = re.compile(
            r'%macro\s+(\w+)\s*'
            r'(?:\(([^)]*(?:\([^)]*\)[^)]*)*)\))?'  # Parameters with nested parens
            r'\s*(?:/\s*([^;]+))?'  # Macro options
            r'\s*;',
            re.IGNORECASE | re.DOTALL
        )
        
        # 3. Macro end - requires semicolon
        self.macro_end_pattern = re.compile(
            r'%mend\s*(\w*)\s*;',
            re.IGNORECASE
        )
        
        # 4. Macro calls - function-style (no semicolon)
        self.macro_func_call_pattern = re.compile(
            r'%(\w+)\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)',
            re.IGNORECASE
        )
        
        # 5. Macro calls - statement-style (with semicolon)
        self.macro_stmt_call_pattern = re.compile(
            r'%(\w+)(?:\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\))?\s*;',
            re.IGNORECASE
        )
        
        # 6. PROC statement - captures name and options
        self.proc_pattern = re.compile(
            r'\bproc\s+(\w+)\s*([^;]*)?;',
            re.IGNORECASE | re.DOTALL
        )
        
        # 7. %LET variable assignment
        self.let_pattern = re.compile(
            r'%let\s+(\w+)\s*=\s*(.*?);',
            re.IGNORECASE | re.DOTALL
        )
        
        # 8. Database connections - multiple patterns
        self.libname_db_pattern = re.compile(
            r'\blibname\s+(\w+)\s+(oracle|teradata|mysql|postgres|sqlserver|odbc|oledb)\s+([^;]+);',
            re.IGNORECASE | re.DOTALL
        )
        
        self.sql_connect_pattern = re.compile(
            r'\bconnect\s+to\s+(\w+)\s*(?:\([^)]*\))?\s*;',
            re.IGNORECASE | re.DOTALL
        )
        
        # 9. SET/MERGE statements
        self.set_merge_pattern = re.compile(
            r'\b(set|merge)\s+(.*?)(?=\s+(?:by|if|where|end)\b|;)',
            re.IGNORECASE | re.DOTALL
        )
        # 10. SQL FROM clause
        self.from_pattern = re.compile(
            r'\bfrom\s+(.*?)(?=\s+(?:where|group|having|order)\b|;|\s*$)',
            re.IGNORECASE | re.DOTALL
        )
        
        # 11. DATA statement
        self.data_pattern = re.compile(
            r'\bdata\s+(.*?)(?=;)',
            re.IGNORECASE
        )
        
        # 12. CREATE TABLE statement
        self.create_table_pattern = re.compile(
            r'\bcreate\s+table\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)?)',
            re.IGNORECASE
        )
        
        # 13. PROC EXPORT
        self.proc_export_pattern = re.compile(
            r'\bproc\s+export\b[^;]*\bdata\s*=\s*([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)?)(?:\([^)]*\))?',
            re.IGNORECASE
        )
        
        # 14. Additional patterns
        self.include_pattern = re.compile(
            r'%include\s+(["\'][^"\']*["\']|\w+)\s*;',
            re.IGNORECASE
        )
        
        self.filename_pattern = re.compile(
            r'\bfilename\s+(\w+)\s+(["\'][^"\']*["\']|[^;]+);',
            re.IGNORECASE | re.DOTALL
        )

    def load_sas_file(self, filepath: str) -> Tuple[str, List[str]]:
        """
        Load a SAS file with robust encoding handling and comment removal.
        """
        
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()
         
        # Remove block comments more carefully
        text_no_comments = self._remove_comments(raw_text)
        return text_no_comments, raw_text.splitlines()
    
    def _remove_comments(self, text: str) -> str:
        """
        Remove SAS comments while preserving strings.
        """
        result = []
        i = 0
        in_single_quote = False
        in_double_quote = False
        
        while i < len(text):
            char = text[i]
            
            # Handle quotes
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                result.append(char)
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                result.append(char)
            # Handle block comments
            elif char == '/' and i + 1 < len(text) and text[i + 1] == '*' and not in_single_quote and not in_double_quote:
                # Skip until */
                i += 2
                while i < len(text) - 1:
                    if text[i] == '*' and text[i + 1] == '/':
                        i += 2
                        break
                    i += 1
                result.append(' ')  # Replace comment with space
                continue
            # Handle line comments
            elif char == '*' and (i == 0 or text[i-1] in '\n\r;') and not in_single_quote and not in_double_quote:
                # Skip to end of line
                while i < len(text) and text[i] not in '\n\r':
                    i += 1
                if i < len(text):
                    result.append(text[i])  # Keep the newline
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    KEYWORDS = [
    r'%let\b', r'%macro\b', r'%mend\b', r'libname\b', r'proc\b', r'data\b',
    r'set\b', r'merge\b', r'%include\b', r'filename\b', r'create\s+table\b', r'connect\s+to\b'
    ]
    KEYWORD_RE = re.compile(r'^\s*(' + '|'.join(KEYWORDS) + r')', re.IGNORECASE)


    def split_sas_statements(self, sas_text: str) -> List[Tuple[str, int]]:
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
            if (self.KEYWORD_RE.match(stripped)
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

    def extract_datasets(self, stmt: str, pattern: re.Pattern, table_type: str) -> List[Dict]:
        """
        Enhanced dataset extraction with better cleaning and validation.
        Properly handles SAS dataset options with lists of variables.

        """
        SAS_DATASET_OPTIONS = {
        'keep', 'drop', 'rename','out', 'where', 'in', 'firstobs', 'obs', 'index', 'compress', 'label'
        }
        tables = []

        # Process the statement to handle dataset options more intelligently
        # First, remove parenthesized options in a preprocessing step
        # This removes (keep=...) and other dataset options before splitting
        stmt_cleaned = re.sub(r'\([^)]*\)', '', stmt)

        for match in pattern.finditer(stmt_cleaned):
            if table_type in ['SET', 'MERGE']:
                raw_datasets = match.group(2)
            else:
                raw_datasets = match.group(1)
            
            if not raw_datasets:
                continue
            
            # Handle different separators based on context
            if table_type == 'FROM':
                parts = [p.strip() for p in raw_datasets.split(',')]
            else:
                # For DATA/SET/MERGE, split by actual separators, not inside option lists
                parts = []
                current_word = ""
                i = 0
                
                # Use a simple word extraction - looking for valid dataset names
                for word in re.finditer(r'\b([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)?)\b', raw_datasets):
                    word_text = word.group(1)
                    
                    # Skip if it's a SAS option
                    if word_text.lower() in SAS_DATASET_OPTIONS:
                        continue
                        
                    # Ensure it's a valid dataset name
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$|^_null_$', word_text, re.IGNORECASE):
                        parts.append(word_text)
            
            # Process each table reference
            for ds_clean in parts:
                # Already cleaned and validated dataset name
                # Skip '=' which might indicate an option assignment
                if '=' in ds_clean:
                    continue

                # Skip SAS keywords
                if ds_clean.lower() in SAS_DATASET_OPTIONS:
                    continue

                # Remove table aliases for FROM clauses
                if table_type == 'FROM':
                    alias_match = re.search(r'\s+(?:as\s+)?(\w+)$', ds_clean, re.IGNORECASE)
                    if alias_match:
                        ds_clean = ds_clean[:alias_match.start()].strip()

                tables.append({
                    'type': table_type,
                    'table': ds_clean,
                    'line_number': None
                })

        return tables

    def extract_macro_calls(self, stmt: str) -> List[Dict]:
        """
        Extract both function-style and statement-style macro calls.
        """
        calls = []
        
        # Function-style calls
        for match in self.macro_func_call_pattern.finditer(stmt):
            calls.append({
                'macro_name': match.group(1),
                'macro_args': match.group(2) if match.group(2) else '',
                'call_type': 'function'
            })
        
        # Statement-style calls
        for match in self.macro_stmt_call_pattern.finditer(stmt):
            calls.append({
                'macro_name': match.group(1),
                'macro_args': match.group(2) if match.group(2) else '',
                'call_type': 'statement'
            })
        
        return calls

    def extract_sas_info(self, filepath: str) -> Dict[str, pd.DataFrame]:
        """
        Main extraction function with comprehensive error handling.
        """
        try:
            text_no_comments, original_lines = self.load_sas_file(filepath)
            if not text_no_comments.strip():
                logger.warning(f"Empty or unreadable file: {filepath}")
                return self._empty_results()
            
            statements = self.split_sas_statements(text_no_comments)
            
            # Initialize result collections
            results = {
                'libname_matches': [],
                'macro_defs': [],
                'macro_calls': [],
                'proc_defs': [],
                'let_defs': [],
                'db_conns': [],
                'input_tables': [],
                'output_tables': [],
                '%include': [],
                'filenames': []
            }
            
            macro_stack = []  # Track nested macros
            
            for stmt, stmt_line in statements:
                self._process_statement(stmt, stmt_line, results, macro_stack)
            
            # Convert to DataFrames with error handling
            return self._create_dataframes(results)
            
        except Exception as e:
            logger.error(f"Error processing {filepath}: {str(e)}")
            return self._empty_results()

    def _process_statement(self, stmt: str, stmt_line: int, results: Dict, macro_stack: List):
        """Process a single SAS statement."""
        stmt_lower = stmt.lower().strip()
        
        # Skip empty statements
        if not stmt_lower:
            return
        
        # 1. LIBNAME statements
        for match in self.libname_pattern.finditer(stmt):
            libref = match.group(1)
            temp_ref = match.group(2)
            quoted_path = match.group(3)
            engine_or_path = match.group(4)
            options = match.group(5) if match.group(5) else ''
            
            if temp_ref:
                # Temporary library reference
                results['libname_matches'].append({
                    'libref': libref,
                    'libref_type': 'temporary',
                    'libref_path': temp_ref,
                    'db_engine': None,
                    'options': options,
                    'line_number': stmt_line
                })
            elif quoted_path:
                # File path
                results['libname_matches'].append({
                    'libref': libref,
                    'libref_type': 'path',
                    'libref_path': quoted_path,
                    'db_engine': None,
                    'options': options,
                    'line_number': stmt_line
                })
            elif engine_or_path:
                # Could be engine or unquoted path
                db_engines = ['oracle', 'teradata', 'mysql', 'postgres', 'sqlserver', 'odbc', 'oledb']
                if engine_or_path.lower() in db_engines:
                    results['libname_matches'].append({
                        'libref': libref,
                        'libref_type': 'database',
                        'libref_path': None,
                        'db_engine': engine_or_path,
                        'options': options,
                        'line_number': stmt_line
                    })
                else:
                    results['libname_matches'].append({
                        'libref': libref,
                        'libref_type': 'path',
                        'libref_path': engine_or_path,
                        'db_engine': None,
                        'options': options,
                        'line_number': stmt_line
                    })
        
        # 2. Macro definitions
        for match in self.macro_def_pattern.finditer(stmt):
            macro_info = {
                'macro_name': match.group(1),
                'macro_args': match.group(2) if match.group(2) else '',
                'macro_options': match.group(3) if match.group(3) else '',
                'start_line': stmt_line,
                'end_line': None
            }
            macro_stack.append(macro_info)
            results['macro_defs'].append(macro_info)
        
        # 3. Macro ends
        for match in self.macro_end_pattern.finditer(stmt):
            if macro_stack:
                macro_info = macro_stack.pop()
                macro_info['end_line'] = stmt_line
        
        # 4. Macro calls
        macro_calls = self.extract_macro_calls(stmt)
        for call in macro_calls:
            call['line_number'] = stmt_line
            results['macro_calls'].append(call)
        
        # 5. PROC statements
        for match in self.proc_pattern.finditer(stmt):
            results['proc_defs'].append({
                'proc': match.group(1),
                'proc_options': match.group(2) if match.group(2) else '',
                'proc_line_number': stmt_line
            })
        
        # 6. %LET statements
        for match in self.let_pattern.finditer(stmt):
            results['let_defs'].append({
                'let_variable': match.group(1),
                'let_value': match.group(2).strip(),
                'let_line_number': stmt_line
            })
        
        # 7. Database connections
        for match in self.libname_db_pattern.finditer(stmt):
            results['db_conns'].append({
                'db_connection_type': 'libname_db',
                'db_engine': match.group(2),
                'db_connection_string': match.group(3),
                'db_line_number': stmt_line
            })
        
        for match in self.sql_connect_pattern.finditer(stmt):
            results['db_conns'].append({
                'db_connection_type': 'sql_connect',
                'db_engine': match.group(1),
                'db_connection_string': match.group(0),
                'db_line_number': stmt_line
            })
        
        # 8. Input tables
        input_tables = []
        input_tables.extend(self.extract_datasets(stmt, self.set_merge_pattern, 'SET'))
        input_tables.extend(self.extract_datasets(stmt, self.set_merge_pattern, 'MERGE'))
        input_tables.extend(self.extract_datasets(stmt, self.from_pattern, 'FROM'))
        
        for table in input_tables:
            table['line_number'] = stmt_line
            results['input_tables'].append(table)
        
        # 9. Output tables
        output_tables = []
        output_tables.extend(self.extract_datasets(stmt, self.data_pattern, 'DATA'))
        output_tables.extend(self.extract_datasets(stmt, self.create_table_pattern, 'CREATE_TABLE'))
        output_tables.extend(self.extract_datasets(stmt, self.proc_export_pattern, 'PROC_EXPORT'))
        
        for table in output_tables:
            table['line_number'] = stmt_line
            results['output_tables'].append(table)
        
        # 10. %INCLUDE statements
        for match in self.include_pattern.finditer(stmt):
            results['%include'].append({
                'include_file': match.group(1),
                'include_line_number': stmt_line
            })
        
        # 11. FILENAME statements
        for match in self.filename_pattern.finditer(stmt):
            results['filenames'].append({
                'fileref': match.group(1),
                'filename': match.group(2),
                'line_number': stmt_line
            })

    def _create_dataframes(self, results: Dict) -> Dict[str, pd.DataFrame]:
        """Create DataFrames from extraction results with error handling."""
        dataframes = {}
        
        try:
            dataframes['libname'] = pd.DataFrame(results['libname_matches'])
            dataframes['macro'] = pd.DataFrame(results['macro_defs'])
            dataframes['macro_calls'] = pd.DataFrame(results['macro_calls'])
            dataframes['proc'] = pd.DataFrame(results['proc_defs'])
            dataframes['let'] = pd.DataFrame(results['let_defs'])
            dataframes['db_conn'] = pd.DataFrame(results['db_conns'])
            dataframes['input_tables'] = pd.DataFrame(results['input_tables']).drop_duplicates()
            dataframes['output_tables'] = pd.DataFrame(results['output_tables']).drop_duplicates()
            dataframes['%include'] = pd.DataFrame(results['%include'])
            dataframes['filenames'] = pd.DataFrame(results['filenames'])
        except Exception as e:
            logger.error(f"Error creating DataFrames: {str(e)}")
            return self._empty_results()
        
        return dataframes

    def _empty_results(self) -> Dict[str, pd.DataFrame]:
        """Return empty DataFrames for all result types."""
        return {
            'libname': pd.DataFrame(),
            'macro': pd.DataFrame(),
            'macro_calls': pd.DataFrame(),
            'proc': pd.DataFrame(),
            'let': pd.DataFrame(),
            'db_conn': pd.DataFrame(),
            'input_tables': pd.DataFrame(),
            'output_tables': pd.DataFrame(),
            '%include': pd.DataFrame(),
            'filenames': pd.DataFrame()
        }

    def combine_results(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Combine all result DataFrames into a single DataFrame.
        """
        frames = []
        
        for key, df in results.items():
            if not df.empty:
                df_copy = df.copy()
                df_copy['extracted_type'] = key
                frames.append(df_copy)
        
        if frames:
            try:
                combined_df = pd.concat(frames, ignore_index=True, sort=False)
                return combined_df
            except Exception as e:
                logger.error(f"Error combining results: {str(e)}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def analyze_files(self, pattern: str = "../data/**/*.sas", output_file: str = "sas_analysis_results.xlsx") -> pd.DataFrame:
        """
        Analyze multiple SAS files and return combined results.
        """
        sas_files = glob.glob(pattern, recursive=True)
        logger.info(f"Found {len(sas_files)} SAS files to process.")
        
        if not sas_files:
            logger.warning(f"No SAS files found matching pattern: {pattern}")
            return pd.DataFrame()
        
        all_results = []
        successful_files = 0
        
        for sas_file in sas_files:
            logger.info(f"Processing: {os.path.basename(sas_file)}")
            
            try:
                # Extract info from one file  
                file_results = self.extract_sas_info(sas_file)
                
                # Combine results for this file
                combined_results = self.combine_results(file_results)
                
                if not combined_results.empty:
                    combined_results['source_file'] = os.path.basename(sas_file)
                    combined_results['source_path'] = sas_file
                    all_results.append(combined_results)
                    successful_files += 1
                else:
                    logger.warning(f"No data extracted from {sas_file}")
                    
            except Exception as e:
                logger.error(f"Failed to process {sas_file}: {str(e)}")
        
        # Combine all results
        if all_results:
            try:
                final_df = pd.concat(all_results, ignore_index=True, sort=False)
                logger.info(f"Successfully processed {successful_files}/{len(sas_files)} files")
                logger.info(f"Total records extracted: {len(final_df)}")
                
                # Export results
                try:
                    final_df.to_excel(output_file, index=False)
                    logger.info(f"Results exported to {output_file}")
                except Exception as e:
                    logger.error(f"Failed to export to Excel: {str(e)}")
                    # Try CSV as fallback
                    csv_file = output_file.replace('.xlsx', '.csv')
                    final_df.to_csv(csv_file, index=False)
                    logger.info(f"Results exported to {csv_file} (CSV fallback)")
                
                return final_df
                
            except Exception as e:
                logger.error(f"Failed to combine final results: {str(e)}")
                return pd.DataFrame()
        else:
            logger.warning("No data was extracted from any files")
            return pd.DataFrame()


def main():
    """
    Main function to run the SAS analyzer.
    """
    analyzer = SASAnalyzer()
    
    # Analyze files - adjust the pattern as needed
    results_df = analyzer.analyze_files(
        pattern="../data2/*.sas",  
        output_file="sas_analysis_results3.xlsx"
    )
    
    if not results_df.empty:
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"Total records: {len(results_df)}")
        print("\nRecords by type:")
        print(results_df['extracted_type'].value_counts())
        print("\nFiles processed:")
        print(results_df['source_file'].nunique(), "unique files")
    else:
        print("No results to display")
    
    return results_df

if __name__ == "__main__":
    main()