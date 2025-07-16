%let year = 2024
libname mylib "/home/data"
proc print data=sashelp.class
run;

%macro report;
    data new;
        set old
        where age > 18;
    run
%mend
