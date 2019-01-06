# Synthetic-Categorical-Data
In development but as an example have 3 variables for example:
- Animal Type
- Animal Appetite
- Animal Size

If you have summary data on the relationship between size and appetite and between Type and Size and other conditional probabilities 
then you can create a full (but synetetic) dataset containing all three variable names together (though that would be a toy 
example).

This could be useful for:
- Developing new data viz techniques (e.g. how to show how that two categorical variables vary togther in the presence of a 
 third)
- Testing different data mining techniques ( i.e. if we already know "the answer", what technique can best replicate it?)
- The technique is also useful for market research in that if you perform this procedure at scale on small area geogrphies 
you can then to some extent extrapolate attitudes from survey data beyond the sample survey to various regions. This is a 
quantititve geogrpahy technique used at Leeds University.

Credits:
- Pulp Package in Python 
- Idea of synthesizing data from Leeds University, Geography Dept, though I have never seen anyone else try a LP approach.

Notes:
An alternative and much more scalable method is to use Iterative Proportional Fitting. I thought this would be easier to set up, though
that turned out to be incorrect :(

This method is not really scalable beyond 10-20 variables with small numbers of levels. This is because the number of 
combinations that need to be enumerated rapidly explodes into millions.
