libname wrds "F:\wrds";
data comp;
  set wrds.comp19932018;
run;

proc freq data=comp;table SIC;run;
data comp1;
  set comp;
  if substr(sic,1,2)="60" or substr(sic,1,2)="61" or substr(sic,1,2)="62";
  if CIK ne "";
run;

proc sort data=comp1 nodupkey; by CIK CUSIP ;run;
proc sort data=comp1 nodupkey out=comp2; by CIK;run;

data bankcik;
  set comp1;
  keep cik;
run;


PROC EXPORT DATA= WORK.Bankcik 
            OUTFILE= "E:\Researchcode\Banktext\Bankcik.csv" 
            DBMS=CSV REPLACE;
     PUTNAMES=YES;
RUN;


libname wrds "E:\wrds";
data comp;
  set wrds.compbank19932018;
  if CIK ne "";
run;

proc freq data=comp;table SIC;run;


proc sort data=comp nodupkey; by CIK CUSIP ;run;
proc sort data=comp nodupkey out=comp2; by CIK;run;

data bankcik;
  set comp;
  keep cik;
run;


PROC EXPORT DATA= WORK.Bankcik 
            OUTFILE= "E:\Researchcode\Banktext\CompBankcik.csv" 
            DBMS=CSV REPLACE;
     PUTNAMES=YES;
RUN;








