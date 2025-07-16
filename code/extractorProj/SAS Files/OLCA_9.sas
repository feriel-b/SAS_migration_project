/* DATA SANDSLOPE; */
/* INFILE '/home/u63443858/my_shared_file_links/schimiak/DiameterofSandGradulesvsSlopeonBeach.csv' delimiter = ','; */
/* INPUT */
/* SAND */
/* SLOPE */
/* ; */
/* RUN; */
/* PROC PRINT DATA = SANDSLOPE; */
/* RUN; */
/* ODS GRAPHICS ON; */
/* PROC GPLOT DATA = SANDSLOPE; */
/* PLOT SAND*SLOPE; */
/* RUN; */
/* PROC CORR DATA = SANDSLOPE; */
/* VAR SAND SLOPE; */
/* RUN; */
/* PROC REG DATA = SANDSLOPE PLOTS = DIAGNOSTICS(STATS=NONE); */
/* MODEL SAND = SLOPE; */
/* RUN; */
/* QUIT; */

/* DATA CHIRPTEMP; */
/* INFILE '/home/u63443858/my_shared_file_links/schimiak/CricketChirpsvsTemperature.csv' delimiter = ','; */
/* INPUT */
/* CHIRP */
/* TEMP */
/* ; */
/* RUN; */
/* PROC PRINT DATA = CHIRPTEMP; */
/* RUN; */
/* ODS GRAPHICS ON; */
/* PROC GPLOT DATA = CHIRPTEMP; */
/* PLOT CHIRP*TEMP; */
/* RUN; */
/* PROC CORR DATA = CHIRPTEMP; */
/* VAR CHIRP TEMP; */
/* RUN; */
/* PROC REG DATA = CHIRPTEMP PLOTS = DIAGNOSTICS(STATS=NONE); */
/* MODEL CHIRP = TEMP; */
/* RUN; */
/* QUIT; */


/* DATA FIRETHEFT; */
/* INFILE '/home/u63443858/my_shared_file_links/schimiak/FireandTheftinChicago.csv' delimiter = ','; */
/* INPUT */
/* FIRE */
/* THEFT */
/* ; */
/* RUN; */
/* PROC PRINT DATA = FIRETHEFT; */
/* RUN; */
/* ODS GRAPHICS ON; */
/* PROC GPLOT DATA = FIRETHEFT; */
/* PLOT FIRE * THEFT; */
/* RUN; */
/* PROC CORR DATA = FIRETHEFT; */
/* VAR FIRE THEFT; */
/* RUN; */
/* PROC REG DATA = FIRETHEFT PLOTS = DIAGNOSTICS(STATS=NONE); */
/* MODEL FIRE = THEFT; */
/* RUN; */
/* QUIT; */

DATA PHBICARBONATE;
INFILE '/home/u63443858/my_shared_file_links/schimiak/pHvsBicarbonate.csv' delimiter = ',';
INPUT
PH
BICARBONATE
;
RUN;
PROC PRINT DATA = PHBICARBONATE;
RUN;
ODS GRAPHICS ON;
PROC GPLOT DATA = PHBICARBONATE;
PLOT PH * BICARBONATE;
RUN;
PROC CORR DATA = PHBICARBONATE;
VAR PH BICARBONATE;
RUN;
PROC REG DATA = PHBICARBONATE PLOTS = DIAGNOSTICS(STATS=NONE);
MODEL PH = BICARBONATE;
RUN;
QUIT;