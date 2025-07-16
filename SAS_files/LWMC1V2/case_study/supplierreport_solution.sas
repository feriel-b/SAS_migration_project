**********************************************************
*  Concepts used:                                        *
*  1) Create a macro function, store as AUTOCALL         *
*  2) Use %SYSFUNC                                       *
*  3) Create macro with a parameter                      *
*  4) Use %IF/%THEN based on macro parameter value       *
*  5) Use %PUT to generate custom messages in log        *
*  6) Create a series of macro variables                 *
*  7) Use %DO loop and indirect macro variable reference *
**********************************************************;

**********************************************************
* Be sure to first run cre8data.sas and libname.sas      *
**********************************************************;

/*Create REPLACESPACE macro to replace spaces with underscores*/
/*Save in autocall folder*/
/*Solution code for REPLACESPACE macro in ReplaceSpace_Solution.sas*/

options sasautos=("&path/autocall", SASAUTOS);

/*Create macro SupplierReport to generate PDF for each of the top 5 suppliers*/

%macro supplierreport(ot) / minoperator;
%local i;
%if &ot= %then %do;
    %put ERROR: You did not specify an Order_Type code (required).;
	%put ERROR- Valid Order_Type values include blank, 1 (retail), 2 (catalog), or 3 (internet).;
    %put ERROR- Program will stop executing;
    %return;
%end;

%else %if not(&ot in 1 2 3) %then %do;
	%put ERROR: Valid Order_Type values include blank, 1 (retail), 2 (catalog), or 3 (internet).;
	%put ERROR- Program will stop executing;
	%return;
%end;

%else %do;

/*PART 1*/
/*This step creates the OrderDetail table that joins Orders with Products and Country_Codes.
  It calculates Profit for each row and include Retail Sales (order_type=1) only */
	proc sql;
	create table OrderDetail as
		select Order_ID, o.Product_ID, Order_Type, Product_Category,
	           Product_Group, Product_Line, Product_Name,
	           (total_retail_price-(costprice_per_unit*quantity)) as Profit,
	           Supplier_ID, Supplier_Name, Supplier_Country
		from mc1.orders as o
			left join mc1.products as p
			on o.Product_ID=p.Product_ID
		where order_type=&ot;
	quit;		

	/*This step summarizes profit and ranks suppliers*/
	/*Generate macro variables for top 5 suppliers ID, Name and sum of Profit*/
	proc sql;
	select Supplier_ID format=12.,
	       Supplier_Name,
	       Supplier_Country,
	       sum(profit) as Profit
	    into :topsupp1-:topsupp5, :name1-:name5, :country1-:country5, :profit1-:profit5
	    from OrderDetail
	    group by Supplier_ID, Supplier_Name, Supplier_Country
	    order by Profit desc;
	quit;

    /*Use CALL SYMPUTX to create a series of macro variables named Country_CC where
	  CC is the 2-letter CountryCode. Assign the corresponding CountryName value.*/
	data _null_;
		set mc1.country_codes;
		call symputx(cats('country_',CountryCode),CountryName);
	run;

	options nodate;
	ods graphics on / imagefmt=png;
	%do i=1 %to 5;

	ods pdf file="&path/case_study/%replacespace(&i &&name&i).pdf" style=meadow startpage=no nogtitle notoc;

	%let cc=&&country&i;
	title "Orders for #&i &&name&i, &&country_&cc";
	%if &ot=1 %then %do;
		title2 "Retail Sales Only";
	%end;
	%else %if &ot=2 %then %do;
		title2 "Catalog Sales Only";
	%end;
	%else %if &ot=3 %then %do;
		title2 "Internet Sales Only";
	%end;
	%else %if &ot= %then %do;
		title2 "All Sales";
	%end;
		
	proc sgplot data=OrderDetail;
		hbar Product_Category / response=profit stat=sum group=Product_Group categoryorder=respdesc;
		where Supplier_ID=&&topsupp&i;
		format profit dollar8.;
	run;

	title;
	footnote "As of %sysfunc(today(),weekdate.) at %sysfunc(time(),timeampm.)";
	proc sql;
		select Product_Group,
	           count(order_id) as NumOrders "Number of Orders",
	           sum(profit) as TotalProfit "Total Profit" format=dollar8.,
	           avg(profit) as AvgProfit "Average Profit per Order" format=dollar6.
		from OrderDetail
		where Supplier_ID=&&topsupp&i
		group by Product_Group
		order by calculated numorders desc;
	quit;

	footnote;
	%end;
%end;
ods pdf close;
%mend supplierreport;

%supplierreport(1)
*%supplierreport(2)
*%supplierreport(3)
*%supplierreport(4)
*%supplierreport()
