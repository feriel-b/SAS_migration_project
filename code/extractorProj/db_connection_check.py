import os
import re

# List of built-in or always-available SAS libraries to ignore
BUILTIN_LIBNAMES = {"work", "sashelp", "sasuser", "maps"}

def read_sas_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove single-line comments
    content = re.sub(r'^\s*\*.*?;', '', content, flags=re.MULTILINE)
    return content

def extract_libnames(code):
    """
    Extracts libnames defined in the code.
    Returns a set of librefs (library names).
    """
    return set(match.group(1).lower() for match in re.finditer(r'libname\s+(\w+)\b', code, re.IGNORECASE))

def extract_librefs_used(code):
    """
    Extracts all librefs used as part of libref.table patterns.
    Returns a set of librefs.
    """
    return set(match.group(1).lower() for match in re.finditer(r'\b(\w+)\.\w+\b', code))

def main():
    base_dir = "SAS Files"
    if not os.path.isdir(base_dir):
        print("❌ 'SAS Files' folder not found.")
        return

    libnames_defined = set()
    librefs_used = set()
    libref_usage_map = {}  # For reporting where they were used

    for filename in os.listdir(base_dir):
        if filename.endswith(".sas"):
            path = os.path.join(base_dir, filename)
            code = read_sas_file(path)
            found_libnames = extract_libnames(code)
            libnames_defined.update(found_libnames)

            used_librefs = extract_librefs_used(code)
            librefs_used.update(used_librefs)
            # Map each usage to filename for reporting
            for ref in used_librefs:
                ref = ref.lower()
                if ref not in libref_usage_map:
                    libref_usage_map[ref] = set()
                libref_usage_map[ref].add(filename)

    # Remove built-in libnames from the check
    librefs_used_to_check = librefs_used - BUILTIN_LIBNAMES

    missing_libnames = sorted(librefs_used_to_check - libnames_defined)
    if missing_libnames:
        print("🚨 Missing LIBNAME statements for the following librefs (potential DB connection issues):")
        for libref in missing_libnames:
            files = ', '.join(libref_usage_map[libref])
            print(f"  - {libref} (used in: {files})")
    else:
        print("✅ All used librefs have corresponding LIBNAME statements.")

if __name__ == "__main__":
    main()