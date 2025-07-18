/* ================================================== */
/* MASTER SAS EDGE CASE TEST PROGRAM                 */
/* Covers macro, DATA step, PROC SQL, I/O, and more  */
/* ================================================== */

/* SECTION 1: COMPLEX MACRO DEFINITIONS */
/* ----------------------------------- */

/* 1. Nested macro with conditional logic */
%macro outer_macro;
  %put Outer macro executing;
  
  %macro inner_macro(param);
    %if &param = 1 %then %do;
      %put Condition 1 met;
      %let status = SUCCESS;
    %end;
    %else %if &param = 2 %then %do;
      %put Condition 2 met;
      %let status = WARNING;
    %end;
    %else %do;
      %put Invalid parameter;
      %let status = ERROR;
    %end;
  %mend inner_macro;
  
  %inner_macro(1);  /* Calls nested macro */
%mend outer_macro;

%outer_macro;  /* Edge: Nested %if-%then in macros */

/* 2. Macro with reserved word parameters */
%macro risky_macro(data=, where=, class=);
  /* Edge: Uses SAS keywords as parameters */
  proc freq data=&data;
    tables &class;
    where &where;  /* Potential injection risk */
  run;
%mend risky_macro;

%risky_macro(data=sashelp.class, where=age>12, class=sex);


/* SECTION 2: DATA STEP EDGE CASES */
/* ------------------------------ */

/* 3. DATA _NULL_ with external file write */
filename outfile "%sysfunc(getoption(WORK))/output.txt";

data _null_;
  set sashelp.class;
  file outfile;
  put name $10. age 3.;  /* Edge: External I/O */
run;

/* 4. SET/MERGE with dataset options */
data merged_data;
  merge sashelp.class(in=a where=(age>12) keep=name age)
        sashelp.cars(in=b rename=(make=name));
  by name;
  if a and b;  /* Edge: Complex merge logic */
run;

/* 5. Array/DO loop with potential error */
data array_test;
  array values[3] _temporary_ (1, 2, 3);
  do i = 1 to 4;  /* Edge: Will error on i=4 */
    x = values[i];
    output;
  end;
run;


/* SECTION 3: PROC SQL EDGE CASES */
/* ----------------------------- */

/* 6. Implicit Oracle pass-through */
proc sql;
  create table oracle_data as
  select * from oracle.customers  /* Edge: No explicit connection */
  where rownum < 100;
quit;

/* 7. EXECUTE with dynamic SQL */
proc sql;
  connect to oracle (user=myuser pw=mypw);
  
  /* Edge: Dynamic SQL in another dialect */
  execute(
    declare
      v_count number;
    begin
      select count(*) into v_count from &table;
      insert into audit_log values(sysdate, v_count);
    end;
  ) by oracle;
  
  disconnect from oracle;
quit;


/* SECTION 4: DATABASE CONNECTIONS */
/* ------------------------------ */

/* 8. LIBNAME with connection string */
libname mydb odbc noprompt="DSN=test;UID=user;PWD=pass";  /* Edge: Embedded credentials */

/* 9. Connection pooling example */
proc sql;
  connect to teradata (mode=teradata connection=shared);
  select * from connection to teradata (
    select * from sales.transactions
  );
  /* Edge: Missing disconnect - potential leak */
quit;


/* SECTION 5: MACRO VARIABLE TRAPS */
/* ------------------------------ */

/* 10. Indirect macro references */
%let dataset1 = sashelp.class;
%let dataset2 = sashelp.cars;
%let i = 1;

proc contents data=&&dataset&i;  /* Edge: Resolves to &dataset1 */
run;

/* 11. Macro vars with special chars */
%let bad_path = %str(C:\Program Files\SAS\Data);  /* Edge: Spaces in path */
%let sql_cond = %nostr(name like "%Smith%");  /* Edge: Nested quotes */

data test;
  set "&bad_path\mydata.sas7bdat";  /* Edge: Runtime failure if path invalid */
run;


/* SECTION 6: FILE PATH EDGE CASES */
/* ------------------------------ */

/* 12. Network/UNC paths */
filename remote "\\server\share\data.csv";  /* Edge: Windows UNC path */

/* 13. Environment variable paths */
filename temp "%sysget(TEMP)\output.txt";  /* Edge: OS-dependent */

data _null_;
  file temp;
  put "Test content";
run;


/* SECTION 7: ERROR HANDLING CASES */
/* ------------------------------ */

/* 14. Silent %SYSFUNC failure */
%if %sysfunc(fileexist(/invalid/path)) %then %do;
  %put File exists;
%end;
%else %do;
  %put File not found;  /* Edge: No error in log */
%end;

/* 15. OPTIONS OBS=0 side effects */
options obs=0;  /* Edge: Silently processes zero rows */
proc means data=sashelp.class;
run;
options obs=max;  /* Reset */


/* SECTION 8: SPECIALIZED EDGE CASES */
/* -------------------------------- */

/* 16. PROC HTTP API call */
filename response temp;
proc http
  url="https://api.example.com/data"
  out=response;  /* Edge: External connection */
run;

/* 17. Quote in comment breaking parsing */
/* This comment has a ' single quote */
data test;
  set sashelp.class;  /* Edge: May break naive parsers */
run;

/* 18. Macro variable in PROC OUT= */
%let outname = mylib.results;

proc means data=sashelp.class noprint;
  var height weight;
  output out=&outname mean=;  /* Edge: Dynamic output */
run;

/* 19. DATA step with multiple outputs */
data out1 out2 out3;
  set sashelp.class;
  if age < 13 then output out1;
  else if age < 15 then output out2;
  else output out3;  /* Edge: Multiple output streams */
run;

/* 20. Missing semicolon after macro */
%macro test();
  %put Hello;
%mend test

data work.error;  /* Edge: Missing ; merges lines */
  set sashelp.class;
run;


/* ================================================== */
/* CLEANUP                                            */
/* ================================================== */

/* Delete temporary files */
filename outfile clear;
filename remote clear;
filename temp clear;
filename response clear;

libname mydb clear;

/* Reset options */
options obs=max;