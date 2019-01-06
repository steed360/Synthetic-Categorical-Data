import numpy
from pulp import *
import itertools

#######################################################
#
# Program to generate a synthetic dataset with categorical
# variables where the conditional probabilities relating to relative
# frequencies are known.
#
# Two possible applications for this:
# - Create a challenging dataset to test/compare analysis procedures (or use for data viz)
# - Uses these techniques to generate synthetic populations based on census and survey data.
#
# Examples:  
# - Define cond Prob, e.g.  (Var B == "Always Hungry" | "VarA == "Dog") = 0.7   
# - Set the sample size, e.g. N = 100
# - Set the total proportions: Prob (VarA == "Dog" ) = 0.5
# 
# How does it it work:
# - Use the pulp linear programming package
# - Set up a large number of variables including:
#   - Define the handful of categorical variables that will be the eventual column names (e.g. animal, appetite, cuteness) 
#   - Define the leaf level "combination variables" (e.g. {dog,always hungry,v. cute}, {dog, often hungry, v. cute} ... etc
#   - Define intermediate level variables, e.g. dog_always_hungry, dog_often_hungry, cat_always_hungry etc
#   - Define a variable that is the total number of samples
# - Set up a pulp lp problem that will calculate number for each of the above combination variables 
#   where certain intermediate level variable quantities and ratios are satisfied. 
# - Conditional probabilities can be included, for example:
#   P( always_hungry | is(DOG) ) = 0.6 
#   -- here always_hungry would be an intermediate variable ( = always_hungry, dog, low_cuteness) + (always_hungry, dog, cute)
#   -- and other variable (DOG) would be categorical variable.
#   -- the intermediate variables have to sum to the categorical variables.
#
# It turns out that you can set whatever conditional probablities you would like.
# It's necessary to set the absolute probabilities for one variable relative to N (e.g. dogs are 60percent)
# - Then all other variables should be defined as conditional probabilities following a tree of priority from the 
#   above mentioned variable (see example below)
#
#######################################################

# TODO:
# Create a numpy data table with the resulting data table.
# Create the combination variables...
# Create a CSV file by iterating over the combination variables
# How to load the specification (variabes, category names, conditional probabilities)

# Because of combinatorial explosion of the combination variables, this cannot scale beyond 10-20 variables
# with 2 levels each. IPF offers a better solution there, but this is still useful for investigation.


# Spoof some input data
l_gender  = ['m', 'f']
l_colours = ['t', 'p']
l_degree  = ['e', 'a']

allVars = [l_gender, l_colours, l_degree]

# mt, mp, me, ma,  -- for p(mt|mt+mp) = 0.6


# -----------------------------------------------------
# Define The Categorical Variables Needed
# -----------------------------------------------------

gender_var  =  LpVariable.dicts  ( 'gender' , (['m','f']) )
colours_var  = LpVariable.dicts  ( 'colours', (['t','p']) )
degree_var   = LpVariable.dicts  ( 'degree' , (['e','a']) )

# Set up the lowest level variables (the individual cell values)
# [ ('m', 't', 'e'), ('m', 't', 'a') ... ]

combinations = list (itertools.product ( gender_var, colours_var, degree_var ) )
decVars = LpVariable.dicts("elements",(combinations) )

# -----------------------------------------------------
# A variable for the total count
# -----------------------------------------------------

N = LpVariable ('N')

# -----------------------------------------------------
# The Intermediate Variables
# -----------------------------------------------------

# Place in a dictionary with keys made up of the variable names.
# E.g. int_var { ('m', 't') : LP_Variable ('int_var_m_t'), 
#                ('m', 'p') : LP_Variable ('int_var_m_p') ... }
#
# Having intermediate variables will enable conditional probabilities to be built in.
#
# TODO: This is quite cumbersome and should be tidied up!!

# Obtain list of lists like [ ['m','f', 't','p'], ['a','b','a', 'e'] ... ]
a = list ([ sorted(i+j) for i in allVars for j in allVars if i != j] ) 
# Turn it into a Set of tuples - this de-duplicates the list.
b_set = set( map(tuple, a ) ) # de-duplicate the lists.
c = list (map(list,b_set ) ) # back to a list of lists.

# Now get all combinations within each of the segments, e.g. all combos of 2*categorical vars
# ['m','f', 't','p'] ... => ('m','f'), ('m','t'), ('m','p'), ('f','t') etc.
d = [ list(itertools.combinations(i,2)) for i in c]
e = [tuple(sorted(x)) for sublist in d for x in  sublist] # flatten the list

# remove the variables that are currently in the same variable..
# - Get a set of tuples each representing the same categories in different variables.
allVarsSorted = [ sorted(i) for i in allVars ] 
f =  set (map (tuple, allVarsSorted) )

# Remove out the unwanted pairs to provide the final list of intermediate variable pairs.
intVarPairTuples = list (set(e) - f)

intVars = LpVariable.dicts("intermediate",(intVarPairTuples) )
# print ( intVars )

# -----------------------------------------------------
# Set up the problem.
# -----------------------------------------------------

prob = LpProblem("Simple Addition",LpMaximize)

# Define N to be the sum of all the elements
prob += N == lpSum ( [decVars[(i,j,k)]   for i in gender_var for j in colours_var for k in degree_var] )

# -----------------------------------------------------
# Constraints
# -----------------------------------------------------

# And all elements are positive
for i in gender_var:
   for j in colours_var:
        for k in degree_var:
            decVars[(i,j,k)].positive()        

# Define total size of of N
prob += lpSum (N) ==    100

# -----------------------------------------------------
# Constraints: Have the categorical and intermediate variables 
# add up to their matching combination variables
# -----------------------------------------------------

# Set up the meanings of gender variables in terms of combination elements
gender_var['m'] +=  lpSum ( [decVars[('m',j,k)] for j in colours_var for k in degree_var] )
gender_var['f'] +=  lpSum ( [decVars[('f',j,k)] for j in colours_var for k in degree_var] )

# Set up the meanings of colour variables in terms of combination elements
prob +=  colours_var ['t'] == lpSum ( [decVars[(i,'t',k)] for i in gender_var for k in degree_var] )
prob +=  colours_var ['p'] == lpSum ( [decVars[(i,'p',k)] for i in gender_var for k in degree_var] )

# Set up the intermediate variables in terms of the combination variables
# E.g. me + met + mep ... 

for thisIntVar in intVars: # loop through the keys (e.g. ('a', 'f') )
    varA = thisIntVar[0]
    varB = thisIntVar[1]
    # constrain the intermediate variables to the sum of the relevant unerlying combinaitons which wil include additional 
    # vars 
    prob += intVars[thisIntVar] == lpSum ( [decVars[combs] for combs in decVars if varA in combs and varB in combs] )

print (prob)

#elements_('m',_'t',_'e') + 8.0
#elements_('m',_'t',_'a') + 12.0
#elements_('m',_'p',_'e')
#elements_('m',_'p',_'a') + 20.0
#elements_('f',_'t',_'e') + 11.2
#elements_('f',_'t',_'a') + 12.8
#elements_('f',_'p',_'e') + 12.8
#elements_('f',_'p',_'a') + 23.2


# -----------------------------------------------------
# Constraints: Absolute Probabilities
# -----------------------------------------------------

# Absolute Probabilities, there are more females
prob += gender_var['m'] == 0.4 * N
prob += gender_var['f'] == 0.6 * N

# -----------------------------------------------------
# Constraints: Conditional Probabilities
# -----------------------------------------------------

# For Males (favourite colour)
prob +=  intVars [ ('m', 't' ) ] == 0.5 * gender_var['m'] 
prob +=  intVars [ ('m', 'p' ) ] == 0.5 * gender_var['m'] 

# (degree)
prob +=  intVars [ ('e', 'm' ) ] == 0.2 * gender_var['m'] 
prob +=  intVars [ ('a', 'm' ) ] == 0.8 * gender_var['m'] 

# For Females (favourite colour)
prob +=  intVars [ ('f', 't' ) ] == 0.4 * gender_var['f'] 
prob +=  intVars [ ('f', 'p' ) ] == 0.6 * gender_var['f'] 
# (degree)
prob +=  intVars [ ('e', 'f' ) ] == 0.4 * gender_var['f'] 
prob +=  intVars [ ('a', 'f' ) ] == 0.6 * gender_var['f'] 

# For engineers ( favourite colour)
prob +=  intVars [ ('e', 't' ) ] == 0.6 * degree_var['e'] 
prob +=  intVars [ ('e', 'p' ) ] == 0.4 * degree_var['e'] 

# For artists ( faviourite colour)
prob +=  intVars [ ('a', 't' ) ] == 0.1 * degree_var['a'] 
prob +=  intVars [ ('a', 'p' ) ] == 0.9 * degree_var['a'] 

s = prob.solve()

# -----------------------------------------------------
# Show the solution
# -----------------------------------------------------


for i in decVars:
   print  ( decVars[i] +  value (decVars[i] ) )

# -----------------------------------------------------
# Test that conditional probabilities were retained correctly
# -----------------------------------------------------


print ('Num m == 40?' )
print (value ( gender_var['m']) ) 
print ( value ( gender_var['m']) == 40 ) 

print ('Num f == 60?' )
print (value ( gender_var['f']) ) 
print ( value ( gender_var['f']) == 60 )

print ('Prob ( e|m == 0.2?' )
print (value ( intVars[('e','m')] ) / value (gender_var['m'] ) )
print (value ( intVars[('e','m')] ) / value (gender_var['m'] ) == 0.2 )

print ('Prob ( a|m == 0.8?' )
print (value ( intVars[('a','m')] ) / value (gender_var['m'] ) )
print (value ( intVars[('a','m')] ) / value (gender_var['m'] ) == 0.8 )
 
print ('Prob ( t|m == 0.5?' )
print (value ( intVars[('m','t')] ) / value (gender_var['m'] )  )
print (value ( intVars[('m','t')] ) / value (gender_var['m'] ) == 0.5 )

print ('Prob ( p|m == 0.5?' )
print (value ( intVars[('m','p')] ) / value (gender_var['m'] ) )
print (value ( intVars[('m','p')] ) / value (gender_var['m'] ) == 0.5 )

print ('Prob ( t|f == 0.4?' )
print (value ( intVars[('f','t')] ) / value (gender_var['f'] )  )
print (value ( intVars[('f','t')] ) / value (gender_var['f'] ) == 0.4 )

print ('Prob ( p|f == 0.6?' )
print (value ( intVars[('f','p')] ) / value (gender_var['f'] ) )
print (value ( intVars[('f','p')] ) / value (gender_var['f'] ) == 0.6 )

print ('Prob ( e|f == 0.4?' )
print (value ( intVars[('e','f')] ) / value (gender_var['f'] )  )
print (value ( intVars[('e','f')] ) / value (gender_var['f'] ) == 0.4 )

print ('Prob ( a|f == 0.6?' )
print (value ( intVars[('a','f')] ) / value (gender_var['f'] ) )
print (value ( intVars[('a','f')] ) / value (gender_var['f'] ) == 0.6 )

print ('Prob ( t|e == 0.6?' )
print (value ( intVars[('e','t')] ) / value (degree_var['e'] ) )
print (value ( intVars[('e','t')] ) / value (degree_var['e'] ) == 0.6 )

print ('Prob ( p|e == 0.4? )' )
print (value ( intVars[('e','p')] ) / value (degree_var['e'] ) )
print (value ( intVars[('e','p')] ) / value (degree_var['e'] ) == 0.4 )

print ('Prob ( p|a == 0.9?' )
print (value ( intVars[('a','p')] ) / value (degree_var['a'] ) )
print (value ( intVars[('a','p')] ) / value (degree_var['a'] ) == 0.9 )

print ('Prob ( t|a == 0.1?' )
print (value ( intVars[('a','t')] ) / value (degree_var['a'] ) )
print (value ( intVars[('a','t')] ) / value (degree_var['a'] ) == 0.1 )


# -----------------------------------------------------
# Output as CSV (via pandas data frame)
# -----------------------------------------------------

# 

