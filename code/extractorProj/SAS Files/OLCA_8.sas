DATA Questionnaire;

INPUT ID SEX $ AGE;

DATALINES;

001 M 15

023 M 35

224 F 76

031 M 55

187 F 18

063 F 42

223 M 38

212 M 66

149 F 24

103 F 17

;

/*Printing out data to make sure all is inputted correctly*/

PROC PRINT DATA= Questionnaire NOOBS;

   TITLE "Listing of Data Set";

RUN;

 

PROC UNIVARIATE DATA=QUESTIONNAIRE PLOT;

   VAR AGE;

RUN;

Proc Means DATA = Questionnaire CLM ALPHA = 0.10 MAXDEC = 1;

VAR AGE;

Run;

Proc Means DATA = Questionnaire CLM ALPHA = 0.05 MAXDEC = 1;

VAR AGE;

Run;

/*Remember, using ODS Graphics statement requests graphical output*/

ODS Graphics ON;

/*The VAR statement indicates that the Height variable is being studied  */

/*the H0= option specifies that the mean of the AGE variable should be*/ /*compared to the null value 55 rather than the default of 0           */

PROC ttest DATA = Questionnaire H0 = 55;

VAR AGE;

RUN;

ODS graphics ON;

/*Remember, using ODS Graphics statement requests graphical output*/

ODS Graphics ON;

/*SAS default is a two tailed test, so we add the option SIDES = L      */

/*If I want a two-tailed I could leave this option out or put SIDES = 2 */

/*If I want a right-tailed test I would use SIDES = U                   */

/* Also we do not want to use SAS’s default alpha */

/*of 0.05, so we use the option ALPHA=0.1                               */

PROC ttest DATA = Questionnaire H0 = 55 PLOTS (SHOWH0) SIDES = L ALPHA = 0.1;

VAR AGE;

RUN;

ODS graphics ON;

 

/* Part II of online: */

/*Inputting the data, for each breed we are inputting the calcium and*/ /*phosphate levels*/

DATA PIGS;

INPUT BREED $ CALCIUM PHOSPHATE @@;

DATALINES;

CHESTER 116 47 CHESTER 112 48 CHESTER 82 57 CHESTER 63 75 CHESTER 117 65

CHESTER 69 99 CHESTER 79 97 CHESTER 87 110

HAMPHIRE 62 230 HAMPHIRE 59 182 HAMPHIRE 80 162 HAMPHIRE 105 78 HAMPHIRE 60 220 HAMPHIRE 71 172 HAMPHIRE 103 79 HAMPHIRE 100 58

;

PROC PRINT DATA = PIGS;

RUN;

/*Check for Normality*/


PROC UNIVARIATE DATA=PIGS PLOTS;
CLASS BREED;
VAR CALCIUM;
RUN;


/*a 0.05 significance level t-test for differences in phosphate levels*/

/*between breeds*/
ODS GRAPHICS ON;
PROC TTEST DATA = PIGS SIDES=2 ALPHA=0.05;

CLASS BREED;

VAR CALCIUM;

RUN;
ODS GRAPHICS OFF;

/*Wilcoxon Rank-Sum test for difference in the phosphate level between*/

/*breeds*/
ODS GRAPHICS ON;
PROC NPAR1WAY  DATA=PIGS  WILCOXON;

CLASS BREED;

VAR CALCIUM;

EXACT WILCOXON;

RUN;
ODS GRAPHICS OFF;