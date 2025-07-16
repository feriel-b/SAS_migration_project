import re
import os
import glob
import pandas as pd

# Define regex patterns for SAS constructs (case-insensitive)
PATTERNS = {
    'PROC': re.compile(r'^\s*proc\s+(?P<name>\w+)(?P<params>[^;]*);', re.IGNORECASE),
    'DATA_STEP': re.compile(r'^\s*data\s+(?P<name>[^;\(]+)', re.IGNORECASE),
    'PROC_SQL_START': re.compile(r'^\s*proc\s+sql\b', re.IGNORECASE),
    'PROC_SQL_END': re.compile(r'^\s*quit\s*;', re.IGNORECASE),
    'MACRO_DEF': re.compile(r'^\s*%macro\s+(?P<name>\w+)(?:\s*\((?P<params>[^)]*)\))?;', re.IGNORECASE),
    'MACRO_END': re.compile(r'^\s*%mend\b', re.IGNORECASE),
    'INCLUDE': re.compile(r'^\s*%include\s+["\'](?P<path>[^"\']+)["\']\s*;', re.IGNORECASE),
    'LIBNAME': re.compile(r'^\s*libname\s+(?P<name>\w+)\s+(?P<path>[^;]+);', re.IGNORECASE),
    'FILENAME': re.compile(r'^\s*filename\s+(?P<name>\w+)\s+(?P<path>[^;]+);', re.IGNORECASE),
    'OPTIONS': re.compile(r'^\s*options\s+(?P<opts>[^;]+);', re.IGNORECASE),
    'LET': re.compile(r'^\s*let\s+(?P<assign>[^;]+);', re.IGNORECASE)
}


# Patterns for table references
TABLE_PATTERNS = {
    'PROC': {
        'IN': re.compile(r'\b(?:data=|from\s*)(?P<table>[\w\.]+)', re.IGNORECASE),
        'OUT': re.compile(r'\b(?:out=|create\s+table\s*)(?P<table>[\w\.]+)', re.IGNORECASE),
    },
    'DATA_STEP': {
        'IN': re.compile(r'\b(?:set|merge)\s+(?P<table>[\w\.]+)', re.IGNORECASE),
        'OUT': re.compile(r'^\s*data\s+(?P<table>[\w\.]+)', re.IGNORECASE),
    },
    'SQL': {
        'IN': re.compile(r'\b(?:from|join)\s+(?P<table>[\w\.]+)', re.IGNORECASE),
        'OUT': re.compile(r'\b(?:create\s+table|into)\s+(?P<table>[\w\.]+)', re.IGNORECASE),
    }
}


def extract_tables(code_lines, context):
    """
    Extract input/output tables from a list of code lines given context ('PROC', 'DATA_STEP', 'SQL').
    """
    inputs, outputs = set(), set()
    for line in code_lines:
        pats = TABLE_PATTERNS.get(context, {})
        for direction, pat in pats.items():
            for m in pat.finditer(line):
                if direction == 'IN':
                    inputs.add(m.group('table'))
                else:
                    outputs.add(m.group('table'))
    return list(inputs), list(outputs)


def parse_file(file_path):
    """
    Parse a single .sas file, return list of block dicts.
    """
    blocks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    in_sql = False
    in_macro = False
    current = None

    while i < len(lines):
        line = lines[i]
        # Detect macro definitions
        if not in_macro:
            m = PATTERNS['MACRO_DEF'].match(line)
            if m:
                in_macro = True
                current = {
                    'block_type': 'MACRO',
                    'block_name': m.group('name'),
                    'params': m.group('params') or '',
                    'raw_code': []
                }
        if in_macro and current:
            current['raw_code'].append(line)
            if PATTERNS['MACRO_END'].match(line):
                blocks.append(current)
                in_macro = False
                current = None
            i += 1
            continue

        # Detect PROC SQL
        if not in_sql and PATTERNS['PROC_SQL_START'].match(line):
            in_sql = True
            current = {'block_type': 'PROC SQL', 'block_name': '', 'raw_code': []}
        if in_sql and current:
            current['raw_code'].append(line)
            if PATTERNS['PROC_SQL_END'].match(line):
                # Extract tables
                inputs, outputs = extract_tables(current['raw_code'], 'SQL')
                current.update({'input_tables': inputs, 'output_tables': outputs})
                blocks.append(current)
                in_sql = False
                current = None
            i += 1
            continue

        # PROC steps
        m = PATTERNS['PROC'].match(line)
        if m:
            current = {
                'block_type': f"PROC {m.group('name').upper()}",
                'block_name': m.group('name'),
                'raw_code': [line]
            }
            # consume until semicolon ending the step (simple assumption)
            while i+1 < len(lines) and not lines[i].strip().endswith(';'):
                i += 1
                current['raw_code'].append(lines[i])
            # extract tables
            inputs, outputs = extract_tables(current['raw_code'], 'PROC')
            current.update({'input_tables': inputs, 'output_tables': outputs})
            blocks.append(current)
            i += 1
            continue

        # DATA step
        m = PATTERNS['DATA_STEP'].match(line)
        if m:
            current = {
                'block_type': 'DATA_STEP',
                'block_name': m.group('name').strip(),
                'raw_code': [line]
            }
            # find end via run; or semicolon on submit
            while i+1 < len(lines) and not re.match(r'^\s*run\s*;', lines[i+1], re.IGNORECASE):
                i += 1
                current['raw_code'].append(lines[i])
            # append the run; if present
            if i+1 < len(lines):
                i += 1
                current['raw_code'].append(lines[i])
            inputs, outputs = extract_tables(current['raw_code'], 'DATA_STEP')
            current.update({'input_tables': inputs, 'output_tables': outputs})
            blocks.append(current)
            i += 1
            continue

        # Other single-line constructs
        for key in ['INCLUDE', 'LIBNAME', 'FILENAME', 'OPTIONS', 'LET']:
            m = PATTERNS[key].match(line)
            if m:
                blocks.append({
                    'block_type': key,
                    'block_name': m.groupdict().get('name') or m.groupdict().get('path') or m.groupdict().get('opts') or m.groupdict().get('assign'),
                    'input_tables': [],
                    'output_tables': [],
                    'raw_code': [line]
                })
                break
        i += 1

    # Add file name to each
    for b in blocks:
        b['file_name'] = os.path.basename(file_path)
    return blocks


def parse_folder(folder_path):
    """
    Walk through folder, parse all .sas files, return DataFrame.
    """
    all_blocks = []
    for sas_file in glob.glob(os.path.join(folder_path, '*.sas')):
        all_blocks.extend(parse_file(sas_file))
    df = pd.DataFrame(all_blocks, columns=['file_name', 'block_type', 'block_name', 'input_tables', 'output_tables', 'raw_code'])
    return df


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse SAS scripts for metadata.')
    parser.add_argument('sas_folder', help='Path to folder containing .sas files')
    parser.add_argument('-o', '--output', default='sas_blocks.xlsx', help='Excel output file')
    args = parser.parse_args()

    df = parse_folder(args.sas_folder)
    # Convert raw_code lists to single strings
    df['raw_code'] = df['raw_code'].apply(lambda lines: ''.join(lines))

    df.to_excel(args.output, index=False)
    print(f"Parsed {len(df)} blocks. Output written to {args.output}")


if __name__ == '__main__':
    main()
