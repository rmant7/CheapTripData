# CheapTripData
## Structure of the validation process for "bus" transportation type

The whole process consists of two steps:
* Create classifier to reveal invalid cases in the raw dataset;
* Create regression model to predict the price for invalid cases.

Based on the predictors (price, duration, distance, latitude, longitude), and the binary outcome variable, the LDA classifier was created. 
It was further used to separate raw data into valid and invalid cases.
The dataset with valid cases was used to create a regression model to predict the prices for the earlier reviled invalid cases.
