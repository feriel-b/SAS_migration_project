import re
import os
import glob
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SASCodeParser:
    """
    Production-grade SAS code parser for auditing and migration analysis.
    Extracts structured metadata from SAS scripts including blocks, tables, and dependencies.
    """
    
    def __init__(self):
        self.results = []
        self.current_file = ""
        
        # Compiled regex patterns for performance
        self.patterns = {
            'proc_start': re.compile(r'^\s*proc\s+(\w+)', re.IGNORECASE),
            'data_start': re.compile(r'^\s*data\s+([^;]+)', re.IGNORECASE),
            'macro_def': re.compile(r'^\s*%macro\s+(\w+)\s*(\([^)]*\))?', re.IGNORECASE),
            'macro_call': re.compile(r'^\s*%(\w+)(\s*\([^)]*\))?', re.IGNORECASE),
            'include': re.compile(r'^\s*%include\s+([^;]+)', re.IGNORECASE),
            'libname': re.compile(r'^\s*libname\s+(\w+)\s+([^;]+)', re.IGNORECASE),
            'filename': re.compile(r'^\s*filename\s+(\w+)\s+([^;]+)', re.IGNORECASE),
            'options': re.compile(r'^\s*options\s+([^;]+)', re.IGNORECASE),
            'run_quit': re.compile(r'^\s*(run|quit)\s*;', re.IGNORECASE),
            'mend': re.compile(r'^\s*%mend', re.IGNORECASE),
            'comment_line': re.compile(r'^\s*(\*|/\*)', re.IGNORECASE),
            'comment_block_end': re.compile(r'\*/', re.IGNORECASE)
        }
        
        # Table extraction patterns
        self.table_patterns = {
            'data_equals': re.compile(r'data\s*=\s*([^)\s,;]+)', re.IGNORECASE),
            'out_equals': re.compile(r'out\s*=\s*([^)\s,;]+)', re.IGNORECASE),
            'set_statement': re.compile(r'set\s+([^;]+)', re.IGNORECASE),
            'merge_statement': re.compile(r'merge\s+([^;]+)', re.IGNORECASE),
            'sql_from': re.compile(r'from\s+([^;,\s]+)', re.IGNORECASE),
            'sql_join': re.compile(r'(?:inner|left|right|full)?\s*join\s+([^;,\s]+)', re.IGNORECASE),
            'sql_into': re.compile(r'into\s+([^;,\s]+)', re.IGNORECASE),
            'sql_create': re.compile(r'create\s+table\s+([^;,\s(]+)', re.IGNORECASE),
            'output_statement': re.compile(r'output\s+([^;]+)', re.IGNORECASE)
        }
    
    def clean_line(self, line: str) -> str:
        """Clean and normalize a line of SAS code."""
        return line.strip().rstrip(';')
    
    def extract_table_names(self, text: str) -> List[str]:
        """Extract table names from a text string, handling various SAS formats."""
        tables = []
        # Remove common SAS options and keywords that aren't table names
        text = re.sub(r'\s+(where|if|keep|drop|rename|firstobs|obs)\s*=.*?(?=\s|$)', '', text, flags=re.IGNORECASE)
        
        # Split by common delimiters and clean
        parts = re.split(r'[,\s]+', text)
        for part in parts:
            part = part.strip().rstrip(';')
            if part and not re.match(r'^(where|if|keep|drop|rename|firstobs|obs)$', part, re.IGNORECASE):
                # Handle parentheses (dataset options)
                if '(' in part:
                    part = part.split('(')[0]
                tables.append(part)
        
        return [t for t in tables if t]
    
    def parse_proc_block(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """Parse a PROC block and extract relevant information."""
        proc_line = lines[start_idx]
        match = self.patterns['proc_start'].match(proc_line)
        if not match:
            return None
        
        proc_type = match.group(1).upper()
        block_name = f"PROC {proc_type}"
        
        # Collect the full block
        block_lines = [proc_line]
        current_idx = start_idx + 1
        in_comment_block = False
        
        while current_idx < len(lines):
            line = lines[current_idx]
            
            # Handle comment blocks
            if '/*' in line and '*/' not in line:
                in_comment_block = True
            elif '*/' in line:
                in_comment_block = False
            
            block_lines.append(line)
            
            # Check for block end
            if not in_comment_block and self.patterns['run_quit'].match(line):
                break
            
            current_idx += 1
        
        # Extract tables
        full_block = ' '.join(block_lines)
        input_tables = set()
        output_tables = set()
        
        # PROC-specific parsing
        if proc_type == 'SQL':
            input_tables.update(self._extract_sql_inputs(full_block))
            output_tables.update(self._extract_sql_outputs(full_block))
        else:
            # Generic PROC parsing
            for pattern_name, pattern in self.table_patterns.items():
                matches = pattern.findall(full_block)
                for match in matches:
                    tables = self.extract_table_names(match)
                    if pattern_name in ['data_equals']:
                        input_tables.update(tables)
                    elif pattern_name in ['out_equals']:
                        output_tables.update(tables)
        
        return {
            'block_type': 'PROC',
            'block_name': block_name,
            'input_tables': list(input_tables),
            'output_tables': list(output_tables),
            'raw_code': '\n'.join(block_lines),
            'end_line': current_idx
        }
    
    def _extract_sql_inputs(self, sql_text: str) -> Set[str]:
        """Extract input tables from SQL text."""
        inputs = set()
        
        # FROM clauses
        from_matches = self.table_patterns['sql_from'].findall(sql_text)
        for match in from_matches:
            inputs.update(self.extract_table_names(match))
        
        # JOIN clauses
        join_matches = self.table_patterns['sql_join'].findall(sql_text)
        for match in join_matches:
            inputs.update(self.extract_table_names(match))
        
        return inputs
    
    def _extract_sql_outputs(self, sql_text: str) -> Set[str]:
        """Extract output tables from SQL text."""
        outputs = set()
        
        # CREATE TABLE
        create_matches = self.table_patterns['sql_create'].findall(sql_text)
        for match in create_matches:
            outputs.update(self.extract_table_names(match))
        
        # INTO clauses
        into_matches = self.table_patterns['sql_into'].findall(sql_text)
        for match in into_matches:
            outputs.update(self.extract_table_names(match))
        
        return outputs
    
    def parse_data_step(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """Parse a DATA step and extract relevant information."""
        data_line = lines[start_idx]
        match = self.patterns['data_start'].match(data_line)
        if not match:
            return None
        
        # Extract output datasets from DATA statement
        data_statement = match.group(1)
        output_tables = self.extract_table_names(data_statement)
        
        # Collect the full block
        block_lines = [data_line]
        current_idx = start_idx + 1
        in_comment_block = False
        input_tables = set()
        
        while current_idx < len(lines):
            line = lines[current_idx]
            
            # Handle comment blocks
            if '/*' in line and '*/' not in line:
                in_comment_block = True
            elif '*/' in line:
                in_comment_block = False
            
            block_lines.append(line)
            
            # Extract input tables from SET, MERGE statements
            if not in_comment_block and not self.patterns['comment_line'].match(line):
                set_match = self.table_patterns['set_statement'].search(line)
                if set_match:
                    input_tables.update(self.extract_table_names(set_match.group(1)))
                
                merge_match = self.table_patterns['merge_statement'].search(line)
                if merge_match:
                    input_tables.update(self.extract_table_names(merge_match.group(1)))
            
            # Check for block end
            if not in_comment_block and self.patterns['run_quit'].match(line):
                break
            
            current_idx += 1
        
        return {
            'block_type': 'DATA',
            'block_name': 'DATA STEP',
            'input_tables': list(input_tables),
            'output_tables': output_tables,
            'raw_code': '\n'.join(block_lines),
            'end_line': current_idx
        }
    
    def parse_macro_definition(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """Parse a macro definition."""
        macro_line = lines[start_idx]
        match = self.patterns['macro_def'].match(macro_line)
        if not match:
            return None
        
        macro_name = match.group(1)
        parameters = match.group(2) if match.group(2) else ""
        
        # Collect the full macro
        block_lines = [macro_line]
        current_idx = start_idx + 1
        
        while current_idx < len(lines):
            line = lines[current_idx]
            block_lines.append(line)
            
            if self.patterns['mend'].match(line):
                break
            
            current_idx += 1
        
        return {
            'block_type': 'MACRO_DEF',
            'block_name': f"%{macro_name}",
            'input_tables': [],
            'output_tables': [],
            'raw_code': '\n'.join(block_lines),
            'parameters': parameters,
            'end_line': current_idx
        }
    
    def parse_macro_call(self, line: str) -> Optional[Dict]:
        """Parse a macro call."""
        match = self.patterns['macro_call'].match(line)
        if not match:
            return None
        
        macro_name = match.group(1)
        parameters = match.group(2) if match.group(2) else ""
        
        return {
            'block_type': 'MACRO_CALL',
            'block_name': f"%{macro_name}",
            'input_tables': [],
            'output_tables': [],
            'raw_code': line.strip(),
            'parameters': parameters,
            'end_line': None
        }
    
    def parse_include_statement(self, line: str) -> Optional[Dict]:
        """Parse an %INCLUDE statement."""
        match = self.patterns['include'].match(line)
        if not match:
            return None
        
        include_path = match.group(1).strip().strip('"\'')
        
        return {
            'block_type': 'INCLUDE',
            'block_name': f"%INCLUDE {include_path}",
            'input_tables': [],
            'output_tables': [],
            'raw_code': line.strip(),
            'end_line': None
        }
    
    def parse_libname_statement(self, line: str) -> Optional[Dict]:
        """Parse a LIBNAME statement."""
        match = self.patterns['libname'].match(line)
        if not match:
            return None
        
        libref = match.group(1)
        path = match.group(2).strip().strip('"\'')
        
        return {
            'block_type': 'LIBNAME',
            'block_name': f"LIBNAME {libref}",
            'input_tables': [],
            'output_tables': [],
            'raw_code': line.strip(),
            'end_line': None
        }
    
    def parse_filename_statement(self, line: str) -> Optional[Dict]:
        """Parse a FILENAME statement."""
        match = self.patterns['filename'].match(line)
        if not match:
            return None
        
        fileref = match.group(1)
        path = match.group(2).strip().strip('"\'')
        
        return {
            'block_type': 'FILENAME',
            'block_name': f"FILENAME {fileref}",
            'input_tables': [],
            'output_tables': [],
            'raw_code': line.strip(),
            'end_line': None
        }
    
    def parse_options_statement(self, line: str) -> Optional[Dict]:
        """Parse an OPTIONS statement."""
        match = self.patterns['options'].match(line)
        if not match:
            return None
        
        options = match.group(1).strip()
        
        return {
            'block_type': 'OPTIONS',
            'block_name': f"OPTIONS",
            'input_tables': [],
            'output_tables': [],
            'raw_code': line.strip(),
            'end_line': None
        }
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse a single SAS file and return all blocks found."""
        self.current_file = os.path.basename(file_path)
        file_results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Clean lines
            lines = [self.clean_line(line) for line in lines]
            
            i = 0
            in_comment_block = False
            
            while i < len(lines):
                line = lines[i]
                
                # Handle multi-line comments
                if '/*' in line and '*/' not in line:
                    in_comment_block = True
                    i += 1
                    continue
                elif '*/' in line:
                    in_comment_block = False
                    i += 1
                    continue
                elif in_comment_block:
                    i += 1
                    continue
                
                # Skip empty lines and single-line comments
                if not line or self.patterns['comment_line'].match(line):
                    i += 1
                    continue
                
                # Parse different constructs
                block_result = None
                
                # PROC blocks
                if self.patterns['proc_start'].match(line):
                    block_result = self.parse_proc_block(lines, i)
                
                # DATA steps
                elif self.patterns['data_start'].match(line):
                    block_result = self.parse_data_step(lines, i)
                
                # Macro definitions
                elif self.patterns['macro_def'].match(line):
                    block_result = self.parse_macro_definition(lines, i)
                
                # Macro calls
                elif self.patterns['macro_call'].match(line):
                    block_result = self.parse_macro_call(line)
                
                # Include statements
                elif self.patterns['include'].match(line):
                    block_result = self.parse_include_statement(line)
                
                # Libname statements
                elif self.patterns['libname'].match(line):
                    block_result = self.parse_libname_statement(line)
                
                # Filename statements
                elif self.patterns['filename'].match(line):
                    block_result = self.parse_filename_statement(line)
                
                # Options statements
                elif self.patterns['options'].match(line):
                    block_result = self.parse_options_statement(line)
                
                if block_result:
                    block_result['file_name'] = self.current_file
                    file_results.append(block_result)
                    
                    # Skip to end of block if applicable
                    if block_result.get('end_line') is not None:
                        i = block_result['end_line'] + 1
                    else:
                        i += 1
                else:
                    i += 1
            
            logger.info(f"Parsed {self.current_file}: {len(file_results)} blocks found")
            return file_results
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            return []
    
    def parse_directory(self, directory_path: str) -> pd.DataFrame:
        """Parse all SAS files in a directory and return consolidated results."""
        sas_files = glob.glob(os.path.join(directory_path, "*.sas"))
        
        if not sas_files:
            logger.warning(f"No .sas files found in {directory_path}")
            return pd.DataFrame()
        
        logger.info(f"Found {len(sas_files)} SAS files to parse")
        
        all_results = []
        for file_path in sas_files:
            file_results = self.parse_file(file_path)
            all_results.extend(file_results)
        
        # Convert to DataFrame
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Ensure all required columns exist
            required_columns = ['file_name', 'block_type', 'block_name', 'input_tables', 'output_tables', 'raw_code']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Reorder columns
            df = df[required_columns + [col for col in df.columns if col not in required_columns]]
            
            logger.info(f"Parsing complete: {len(df)} total blocks found")
            return df
        else:
            logger.warning("No blocks found in any files")
            return pd.DataFrame(columns=['file_name', 'block_type', 'block_name', 'input_tables', 'output_tables', 'raw_code'])


def main():
    """Main function to run the SAS parser."""
    # Configuration
    SAS_DIRECTORY = "../data"
    OUTPUT_FILE = "excel/claude_sas_analysis_results.xlsx"
    
    # Initialize parser
    parser = SASCodeParser()
    
    # Parse all files
    results_df = parser.parse_directory(SAS_DIRECTORY)
    
    if not results_df.empty:
        # Export to Excel
        results_df.to_excel(OUTPUT_FILE, index=False)
        logger.info(f"Results exported to {OUTPUT_FILE}")
        
        # Print summary statistics
        print("\n" + "="*60)
        print("SAS CODE ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total files processed: {results_df['file_name'].nunique()}")
        print(f"Total blocks found: {len(results_df)}")
        print("\nBlock type distribution:")
        print(results_df['block_type'].value_counts())
        
        # Show files with most blocks
        print("\nFiles with most blocks:")
        file_counts = results_df['file_name'].value_counts().head(10)
        for file, count in file_counts.items():
            print(f"  {file}: {count} blocks")
        
        # Show most common input/output tables
        all_inputs = []
        all_outputs = []
        for _, row in results_df.iterrows():
            if isinstance(row['input_tables'], list):
                all_inputs.extend(row['input_tables'])
            if isinstance(row['output_tables'], list):
                all_outputs.extend(row['output_tables'])
        
        if all_inputs:
            print("\nMost referenced input tables:")
            input_counts = pd.Series(all_inputs).value_counts().head(10)
            for table, count in input_counts.items():
                print(f"  {table}: {count} references")
        
        if all_outputs:
            print("\nMost created output tables:")
            output_counts = pd.Series(all_outputs).value_counts().head(10)
            for table, count in output_counts.items():
                print(f"  {table}: {count} creations")
    else:
        logger.warning("No results to export")


if __name__ == "__main__":
    main()