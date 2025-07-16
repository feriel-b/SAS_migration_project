%macro replacespace(text);
	%sysfunc(tranwrd(&text,%str( ),_))
%mend replacespace;

