DATA EX1;
INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata.csv' delimiter=',' dsd;
INPUT GROUP $ X Y Z;
PROC Print;
Run;

DATA EX2;
/*We are now beginning the Merging statement*/
IF TESTEND NE 1 THEN INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata.csv' dsd dlm=','
END = TESTEND;
ELSE INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata1.csv' delimiter=',' dsd;
/*Merging Statement has ended*/
INPUT GROUP $ X Y Z;
PROC PRINT DATA = EX2;
Run;

DATA EX3;
INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata2.csv' delimiter=',' dsd;
INPUT GROUP $ X Y Z;
PROC PRINT DATA= EX3;
RUN;

DATA EX3b;
INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata2.csv' MISSOVER ;
INPUT GROUP $ x y z;
Run;
PROC PRINT DATA = EX3b;
RUN;

DATA EX4;
INFILE '/home/u63443858/my_shared_file_links/schimiak/mydata.csv' dlm=',' dsd;
FILE '/home/u63443858/my_shared_file_links/schimiak/mydata5.csv' dlm=',' dsd;
/*creating the new and true CSV file called mydata5.csv that will be added to the*/
/*directory*/
INPUT GROUP $ X Y Z;
SUM = X+Y+Z;
/*Again, the PUT statement puts these variables in the file we just made*/
PUT GROUP $ X Y Z SUM;
PROC PRINT DATA= EX4;
RUN;

DATA Chicken;
INPUT SEX $ AGE Weight;
DATALINES;
M 60 8.5
M 90 9.1
F 56 6.4
M 44 8.5
F 23 6.4
F 55 6.7
F 59 6.3
M 38 8.3
F 77 6.4
;
PROC PRINT DATA=Chicken;
RUN;

DATA EX6;
INPUT Department $ AGE PROJECT $ INCOME;
DATALINES;
M 60 B 150000
M 90 C 10000
F 56 C 100000
M 44 B 80000
F 23 B 123444
F 55 C 87000
F 59 C 200001
M 38 C 132000
F 77 B 120000
;
PROC PRINT DATA = EX6;
RUN;
/*Subsetting in a PROC FREQ statement. REMEMBER: WHERE not IF must be used*/
PROC FREQ DATA=EX6;
WHERE Department = 'F';
TABLES RACE INCOME;
RUN;

DATA MASTER;
INPUT ID NAME $;
DATALINES;
123 CODY
987 SMITH
111 GREG
222 HAMER
777 JACK
;
DATA TEST;
INPUT ID SCORE;
DATALINES;
123 89
987 55
111 78
222 84
;
/*Note that DATA TEST is Missing Jacks ID number and Score*/
PROC SORT DATA=MASTER;
BY ID;
RUN;
PROC SORT DATA=TEST;
BY ID;
RUN;
/*Now merging the data sets MASTER and TEST together*/
DATA COMB;
MERGE MASTER TEST;
BY ID;
RUN;
PROC PRINT DATA=COMB;
RUN;

DATA EX8;
DO i = 1 TO 10;
/*Creating Data values from the Normal Distribution*/
/*with a mean of 0 and variance of 1N(0,1) */
X =RANNOR(29);
OUTPUT;
END;
RUN;
PROC PRINT DATA = EX8;
RUN;

DATA EX8a;
DO i = 1 TO 10;
/*Creating Data values from the Normal Distribution*/
/*with a mean of 0 and variance of 1N(0,1) */
X =RANNOR(46);
OUTPUT;
END;
RUN;
PROC PRINT DATA = EX8a;
RUN;

DATA EX8b;
DO i = 1 TO 10;
/*Creating Data values from the Normal Distribution*/
/*with a mean of 0 and variance of 1N(0,1) */
X =RANNOR(29);
OUTPUT;
END;
RUN;
PROC PRINT DATA = EX8b;
RUN;

DATA EX9;
DO i = 1 TO 10;
/*Creating Data values from the Normal Distribution*/
/*with a mean of 10 and variance of 6.25 N(10,6.25) */
X = 10 + 2.5* RANNOR(809);
OUTPUT;
END;
RUN;
PROC PRINT DATA = EX9;
RUN;

DATA EX9a;
DO i = 1 TO 1000;
/*Creating Data values from the Normal Distribution*/
/*with a mean of 10 and variance of 6.25 N(10,6.25) */
X = 10 + 2.5* RANNOR(809);
OUTPUT;
END;
RUN;
/*Means procedure*/
PROC MEANS DATA = EX9a MAXDEC = 1;
VAR X;
RUN;

