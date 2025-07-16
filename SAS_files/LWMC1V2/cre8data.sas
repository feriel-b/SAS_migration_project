/*************************************************************
 Note: This program will not run properly on z/OS.
       Only Windows, Linux and UNIX are supported.

 STEP 1: Notice the default values for the %LET statements. 

 STEP 2: If your files will not be located in S:/workshop 
         change the value of PATH= in the %LET statement to 
         reflect your actual data location. 

 STEP 3: Submit the program to create the course data files. 

 STEP 4: Review the SAS log to ensure there are no errors. 

 STEP 5: View the Results and verify the CONTENTS procedure 
         report lists the names of the SAS data sets that 
         were created.
*************************************************************/
%let path=s:/workshop;

/*++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 WARNING: DO NOT ALTER CODE BELOW THIS LINE UNLESS DIRECTED 
          TO DO SO BY YOUR INSTURCTOR.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/

/*************************************************************
  Alternate Data Location paths:
*************************************************************/

*%let path=s:/workshop/mc1v2;
*%let path=c:/workshop/mc1v2;
*%let path=c:/SAS_Education/mc1v2;
*%let path=c:/SAS_Education/lwmc1v2;

%include "&path/data/mc1v2.sas" / encoding=wlatin1;


