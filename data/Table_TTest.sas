/* Validating and organizing input data into a table and running various T-Tests */

/* Printing Table of All Data */
DATA OLDCLASSDATA;
	INFILE '/home/u63443858/my_shared_file_links/schimiak/OldClassData.csv' DSD;
	INPUT
		SUBJECT $
		GENDER $
		PHONE $
		CAMPUS $
		GRADE $
		CAR $
		OPTIMIST
		MATH
		SIBLINGS
		PETS
		CREDIT_HOURS
		SOCIAL_MEDIA
		EXTRA_CURRICULAR
		HEIGHT
		HS_GPA
		EXERCISE
		TIME_TO_GET_READY
		DISTANCE
		;
		
RUN;


PROC PRINT DATA=OLDCLASSDATA;
	TITLE "OLDCLASSDATA";
RUN;


/* Creating formats for GENDER, MATH, HS_GPA->LETTER_GRADE */
PROC FORMAT;
	VALUE $GENDER    	
       'M'='MALE'
       'F'='FEMALE'
       ;
       
    VALUE MATH
    	1 = 'I really like math.'
		2 = 'I somewhat like math.'
		3 = 'I could take math or leave it.'
		4 = 'I really do not like math.'
		5 = 'I would rather have a root canal'
		;
		
	VALUE GRADE
		0-<1.0 = 'F'
		1.0-<2.0 = 'D' 
		2.0-<3.0 = 'C'
		3.0-<4.0 = 'B'
		OTHER = 'A'
		;
RUN;


DATA OLDCLASSDATA;
	SET OLDCLASSDATA;
	LETTER_GRADE = HS_GPA;
	
	FORMAT LETTER_GRADE GRADE.;
	FORMAT GENDER GENDER.;
	FORMAT MATH MATH.;
RUN;

PROC PRINT DATA=OLDCLASSDATA(KEEP=GENDER MATH LETTER_GRADE);
	TITLE "FORMATTED OLDCLASSDATA GENDER MATH LETTER_GRADE";
RUN;


/* Frequency Chart for LETTER_GRADE */
PROC SGPLOT DATA = OLDCLASSDATA;
	VBAR LETTER_GRADE;
	TITLE "Frequency Plot: High School Grade";
RUN;
QUIT;


PROC TTEST DATA = OLDCLASSDATA SIDES=2 ALPHA=.05 H0=0;
	TITLE "HS GPA TWO SAMPLE T-TEST: GENDER";
	CLASS GENDER;
	VAR HS_GPA;
RUN;


/* EXERCISE TIME TTEST */
PROC TTEST DATA = OLDCLASSDATA SIDES=U ALPHA=.05 H0=3.5;
	TITLE "EXERCISE T-TEST";
	VAR EXERCISE;
RUN;


/* Getting Ready 95% CI */
PROC TTEST DATA = OLDCLASSDATA;
	TITLE "95% CI FOR TIME TO GET READY";
	VAR TIME_TO_GET_READY;
RUN;






/* v Unnecessary v */
/* DATA GENDER_GRADES; */
/* SET OLDCLASSDATA; */
/* 	SELECT(GENDER); */
/* 		WHEN ('M') M = HS_GPA; */
/*     	OTHERWISE F = HS_GPA; */
/*     END; */
/*      */
/* KEEP M F; */
/* RUN; */
/*  */
/* Deleting Missing Value */
/* DATA GENDER_GRADES_M; */
/* 	SET GENDER_GRADES (KEEP = M); */
/* 	IF CMISS(OF M) THEN DELETE; */
/* RUN; */
/*  */
/* DATA GENDER_GRADES_F; */
/* 	SET GENDER_GRADES (KEEP = F); */
/* 	IF CMISS(OF F) THEN DELETE; */
/* RUN; */
/*  */
/* DATA GENDER_GRADES; */
/* 	MERGE GENDER_GRADES_M GENDER_GRADES_F; */
/* RUN; */
/*  */
/*  */
/* PROC PRINT DATA=GENDER_GRADES; */
/* 	TITLE "HS GPA BY GENDER"; */
/* RUN; */
/* ^ I did not need to do any of this ... ^ */