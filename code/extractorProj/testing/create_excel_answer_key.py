import pandas as pd

# Define the expected output data that matches extractor2.py output
data = [
    # Test File 1 - %include statements
    {
        "statement": '%include "common_macros.sas";',
        "INCLUDE_PATH": "common_macros.sas",
        "DEPENDENCY_EXISTS": "No",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": '%include "nonexistent_file.sas";',
        "INCLUDE_PATH": "nonexistent_file.sas", 
        "DEPENDENCY_EXISTS": "No",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # %let statements
    {
        "statement": "%let dataset_name=test_data;",
        "LET_STATEMENT": "dataset_name",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "%let output_dir=/data/output;",
        "LET_STATEMENT": "output_dir",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "%let file_path=&output_dir./results.csv;",
        "LET_STATEMENT": "file_path", 
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "%let proc_name=means;",
        "LET_STATEMENT": "proc_name",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Database connections
    {
        "statement": "libname oralib oracle",
        "DB_CONNECTION": "Yes",
        "connection_type": "LIBNAME_ORACLE",
        "libref": "oralib",
        "engine": "oracle",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # DATA steps
    {
        "statement": "data work.dataset_a;",
        "output_table": "work.dataset_a",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "data work.array_test;",
        "output_table": "work.array_test", 
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # MERGE statement
    {
        "statement": "merge work.dataset_a(in=a) work.dataset_b(in=b);",
        "tables_sourcejoin": "work.dataset_a, work.dataset_b",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    {
        "statement": "data work.merged_data;",
        "output_table": "work.merged_data",
        "WRITE_BACK": "Yes", 
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "data work.error_test;",
        "output_table": "work.error_test",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP", 
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Missing connection
    {
        "statement": "set badlib.nonexistent_table",
        "referenced_table": "badlib.nonexistent_table",
        "libref": "badlib",
        "MISSING_CONNECTION": "Yes",
        "connection_issue": "Library referenced but no connection found",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # PROC SQL
    {
        "statement": "proc sql;",
        "PROC_SQL": "Yes",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "connect to oracle",
        "DB_CONNECTION": "Yes",
        "connection_type": "PROC_SQL_CONNECT_ORACLE",
        "engine": "oracle",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "create table work.sql_output",
        "output_table": "work.sql_output",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SQL_CREATE",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "insert into work.sql_output",
        "output_table": "work.sql_output",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SQL_INSERT",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "from sashelp.cars",
        "Input tables": "sashelp.cars",
        "tables_sourcejoin": "cars",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Missing connection SQL
    {
        "statement": "proc sql;",
        "PROC_SQL": "Yes",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "select * from connection to missing_conn",
        "connection_name": "missing_conn",
        "MISSING_CONNECTION": "Yes",
        "connection_issue": "Pass-through query without connection",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # PROC steps
    {
        "statement": "proc sort out=work.sorted_data",
        "output_table": "work.sorted_data",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SORT",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "proc means out=&dataset_name._summary",
        "output_table": "&dataset_name._summary", 
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_MEANS",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "proc freq out=work.freq_output",
        "output_table": "work.freq_output",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_FREQ",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Embedded macro call in DATA
    {
        "statement": "data embedded_macro_test;",
        "output_table": "embedded_macro_test",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Macro calls
    {
        "statement": "%create_summary(input_ds=work.sorted_data,output_ds=work.macro_summary,var_list=age height weight);",
        "MACRO_CALL": "create_summary",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # More PROC steps
    {
        "statement": "proc transpose out=work.transposed_data",
        "output_table": "work.transposed_data",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_TRANSPOSE",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "proc append base=work.sql_output",
        "output_table": "work.sql_output",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_APPEND",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "proc datasets modify sql_output",
        "output_table": "sql_output",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_DATASETS_MODIFY",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # PROC IMPORT/EXPORT
    {
        "statement": "proc import out=work.imported_data",
        "Input tables": "&file_path",
        "output_table": "work.imported_data",
        "import proc": "Yes",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    {
        "statement": "proc export data=work.final_results",
        "output_table": "/data/export/results.xlsx",
        "export proc": "Yes",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Statistical PROC
    {
        "statement": "proc univariate out=work.univariate_stats",
        "output_table": "work.univariate_stats",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_UNIVARIATE",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # More DATA steps
    {
        "statement": "data work.inline_comments;",
        "output_table": "work.inline_comments",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Simple macro call
    {
        "statement": "%simple_print(msg=Processing complete);",
        "MACRO_CALL": "simple_print",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # Connection summary
    {
        "statement": "Connection Summary",
        "DB_CONNECTION": "Yes",
        "connection_type": "SUMMARY",
        "libname_connections": "oralib",
        "sql_connections": "oracle",
        "file_path": "testing/SAS Files/test_file_1.sas"
    },
    
    # TEST FILE 2 entries
    {
        "statement": '%include "shared_utilities.sas";',
        "INCLUDE_PATH": "shared_utilities.sas",
        "DEPENDENCY_EXISTS": "No",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "%let analysis_year=2024;",
        "LET_STATEMENT": "analysis_year",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "%let threshold_value=1000;",
        "LET_STATEMENT": "threshold_value",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "%let export_format=xlsx;",
        "LET_STATEMENT": "export_format",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Additional database connections
    {
        "statement": "libname myteradata teradata",
        "DB_CONNECTION": "Yes",
        "connection_type": "LIBNAME_TERADATA",
        "libref": "myteradata",
        "engine": "teradata",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "libname sqlsrv sqlserver",
        "DB_CONNECTION": "Yes", 
        "connection_type": "LIBNAME_SQLSERVER",
        "libref": "sqlsrv",
        "engine": "sqlserver",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # More PROC SQL
    {
        "statement": "proc sql;",
        "PROC_SQL": "Yes",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "create table work.enriched_customers",
        "output_table": "work.enriched_customers",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SQL_CREATE",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "from work.customer_summary",
        "Input tables": "work.customer_summary",
        "tables_sourcejoin": "customer_summary",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "join sqlsrv.customer_master",
        "Input tables": "sqlsrv.customer_master",
        "tables_sourcejoin": "customer_master",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "from myteradata.sales_transactions",
        "Input tables": "myteradata.sales_transactions",
        "tables_sourcejoin": "sales_transactions",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Missing connection test
    {
        "statement": "proc sql;",
        "PROC_SQL": "Yes",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "create table work.missing_conn_test",
        "output_table": "work.missing_conn_test",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SQL_CREATE",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "select * from connection to undefined_db",
        "connection_name": "undefined_db",
        "MISSING_CONNECTION": "Yes",
        "connection_issue": "Pass-through query without connection",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Multiple output DATA step
    {
        "statement": "data work.high_value;",
        "output_table": "work.high_value",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # More PROC steps with outputs
    {
        "statement": "proc sort out=work.customers_sorted",
        "output_table": "work.customers_sorted",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SORT",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc summary out=work.regional_summary",
        "output_table": "work.regional_summary", 
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_SUMMARY",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc corr out=work.correlation_matrix",
        "output_table": "work.correlation_matrix",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_CORR",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc reg outest=work.regression_estimates",
        "output_table": "work.regression_estimates",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_REG",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc glm out=work.glm_residuals",
        "output_table": "work.glm_residuals",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_GLM",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc datasets modify customers_sorted",
        "output_table": "customers_sorted",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_DATASETS_MODIFY",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Embedded macro in DATA statement
    {
        "statement": "data customer_analysis_final;",
        "output_table": "customer_analysis_final",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # PROC IMPORT with variations
    {
        "statement": "proc import out=work.customer_updates",
        "Input tables": "/data/customer_updates.csv",
        "output_table": "work.customer_updates",
        "import proc": "Yes",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "%let import_path=/data/sales_&analysis_year..txt;",
        "LET_STATEMENT": "import_path",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc import out=work.sales_data",
        "Input tables": "&import_path",
        "output_table": "work.sales_data",
        "import proc": "Yes",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # PROC EXPORT
    {
        "statement": "proc export data=work.regional_summary",
        "output_table": "/reports/regional_analysis.&export_format",
        "export proc": "Yes", 
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Additional statistical procedures
    {
        "statement": "proc logistic out=work.logistic_predictions",
        "output_table": "work.logistic_predictions",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_LOGISTIC",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "proc npar1way out=work.wilcoxon_results",
        "output_table": "work.wilcoxon_results",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_NPAR1WAY",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # More steps
    {
        "statement": "proc append base=work.all_customers",
        "output_table": "work.all_customers",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_APPEND",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Complex merge
    {
        "statement": "merge work.customers_sorted(in=a) work.regional_summary(in=b) work.correlation_matrix(in=c);",
        "tables_sourcejoin": "work.customers_sorted, work.regional_summary, work.correlation_matrix",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "data work.final_analysis;",
        "output_table": "work.final_analysis",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # PROC TRANSPOSE
    {
        "statement": "proc transpose out=work.summary_transposed",
        "output_table": "work.summary_transposed",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_TRANSPOSE",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Arrays and loops DATA step
    {
        "statement": "data work.calculated_metrics;",
        "output_table": "work.calculated_metrics",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Error case with missing libref
    {
        "statement": "data work.error_prone;",
        "output_table": "work.error_prone",
        "WRITE_BACK": "Yes",
        "write_back_type": "DATA_STEP",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    {
        "statement": "set missinglib.phantom_table",
        "referenced_table": "missinglib.phantom_table",
        "libref": "missinglib", 
        "MISSING_CONNECTION": "Yes",
        "connection_issue": "Library referenced but no connection found",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # PROC FREQ with comments
    {
        "statement": "proc freq out=work.crosstab_results",
        "output_table": "work.crosstab_results",
        "WRITE_BACK": "Yes",
        "write_back_type": "PROC_FREQ",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Final macro call
    {
        "statement": "%comprehensive_analysis(input_table=work.customers_sorted,output_prefix=final,group_var=region,analysis_vars=total_spent order_count);",
        "MACRO_CALL": "comprehensive_analysis",
        "file_path": "testing/SAS Files/test_file_2.sas"
    },
    
    # Connection summary for file 2
    {
        "statement": "Connection Summary",
        "DB_CONNECTION": "Yes",
        "connection_type": "SUMMARY",
        "libname_connections": "myteradata, sqlsrv",
        "sql_connections": "teradata, sqlserver",
        "file_path": "testing/SAS Files/test_file_2.sas"
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("testing/final_analysis.xlsx", index=False)
print(f"✅ Created Excel answer key with {len(data)} expected output rows")
print("📊 Columns included:", list(df.columns))
