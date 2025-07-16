
* This is a comprehensive SAS script for testing extraction tools.
* It includes database connections, data import, manipulation, and macros.

* --- Database Connections --- *;

* 1. Oracle Connection using LIBNAME;
libname myoracle oracle user="scott" pass="tiger" path="orcl" schema="hr";

* 2. SQL Server Connection using LIBNAME;
libname myserver oledb "Provider=SQLOLEDB;Data Source=myserver;Initial Catalog=AdventureWorks;Integrated Security=SSPI;";

* 3. PostgreSQL Connection using LIBNAME;
libname mypostgres postgres user="pguser" password="pgpassword" database="sales" server="localhost" port="5432";

* 4. Teradata Connection using PROC SQL;
proc sql;
    connect to teradata (user="tduser" password="tdpassword" server="tdprod");
quit;


* --- Data Import --- *;

* Import data from Oracle;
proc sql;
    create table work.employees as
    select * from connection to myoracle
    (
        select employee_id, first_name, last_name, hire_date, salary
        from employees
        where department_id = 50
    );
quit;

* Import data from Teradata;
proc sql;
    create table work.sales_data as
    select * from connection to teradata
    (
        select product_id, sale_date, quantity, price
        from sales_history
        where sale_date >= '2024-01-01'
    );
quit;


* --- Data Manipulation --- *;

* Create a sample customer dataset;
data work.customers;
    infile datalines;
    input customer_id name $ city $;
    datalines;
101 Alice London
102 Bob Paris
103 Charlie Tokyo
;
run;

* Sort data for merging;
proc sort data=work.employees out=work.sorted_employees;
    by employee_id;
run;

proc sort data=work.sales_data out=work.sorted_sales;
    by product_id;
run;

* Merge datasets;
data work.employee_sales_info;
    merge work.sorted_employees(in=a) work.sorted_sales(in=b);
    by employee_id;
    if a and b;
run;


* --- Data Analysis --- *;

* Calculate summary statistics;
proc means data=work.employee_sales_info;
    var salary quantity;
    output out=work.summary_stats mean=avg_salary total_quantity=total_sales;
run;

* Frequency analysis;
proc freq data=work.customers;
    tables city;
run;


* --- Macro Definition and Call --- *;

%macro print_dataset(dsn);
    proc print data=&dsn;
        title "Contents of &dsn";
    run;
%mend print_dataset;

* Call the macro;
%print_dataset(work.summary_stats);


* --- Data Export --- *;

* Export summary to a CSV file;
proc export data=work.summary_stats
    outfile="c:/temp/summary_stats.csv"
    dbms=csv
    replace;
run;

* --- DATA _NULL_ step for creating macro variables --- *;
data _null_;
  set work.customers;
  call symput(compress('customer_'||customer_id), name);
run;

%put &customer_101;
