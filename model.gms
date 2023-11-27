* Core Model
Set t            "stages" / 1*4 /;
Set st(t)        "stages where sales occur" / 2*4 / ;

Positive Variables
     y(t)        "units to be bought in time period t"
     i(t)        "ending inventory in period t"
     s(t)        "units sold in time period t" ;
Free Variable
     profit ;

Scalars
    kappa        "capacity of storage building"                   / 5000 /
    alpha        "cost per unit bought"                           /   10 /
    beta         "revenue per unit sold"                          /   20 /
    delta        "cost per unit stored at the end of time period" /    4 / ;
 
Parameters
     k           "shape of demand (1st parameter of gamma distribution)" / 16         /
     d_theta(st) "scale of demand (2nd parameter of gamma distribution)" / 2 208.3125
                                                                           3 312.5
                                                                           4 125      /
     d(st)       "demand" ;

d(st) = k * d_theta(st);
 
Equations
     defprofit   "definition of profit"
     balance(t)  "balance equation"
     sales1(st)  "sales cannot exceed demand"
     sales2(t)   "sales cannot exceed inventory of previous time period" ;

defprofit..        profit =e= sum(t, beta * s(t)$st(t) - alpha * y(t) - delta * i(t));
balance(t)..       i(t-1) + y(t) =e= s(t)$st(t) + i(t) ;
sales1(st)..       s(st) =l= d(st);
sales2(t)$st(t)..  s(t) =l= i(t-1);
 
i.up(t) = kappa;
Model inventory /all/;

* EMP Annotations
File emp / '%emp.info%' /; 
put emp; emp.nd=6;
put "randvar d('2') gamma ", k d_theta('2') /;
put "randvar d('3') gamma ", k d_theta('3') /;
put "randvar d('4') gamma ", k d_theta('4') /;
$onput
stage 1 y('1') i('1') balance('1')
stage 2 y('2') d('2') s('2') i('2') balance('2') sales1('2') sales2('2')
stage 3 y('3') d('3') s('3') i('3') balance('3') sales1('3') sales2('3')
stage 4 y('4') d('4') s('4') i('4') balance('4') sales1('4') sales2('4')
$offput
putclose emp;

* Dictionary
Set scen          "scenarios" / s1*s216 /;
Parameters
     s_d(scen,st) "demand realization by scenario"
     s_y(scen,t)  "units bought by scenario"
     s_s(scen,t)  "units sold by scenario"
     s_i(scen,t)  "units stored by scenario" ;
 
Set dict /
   scen .scenario.''
   d    .randvar .s_d
   s    .level   .s_s
   y    .level   .s_y
   i    .level   .s_i  /;

option emp=lindo; 
solve inventory max profit using emp scenario dict;
display s_d, s_s, s_y, s_i;