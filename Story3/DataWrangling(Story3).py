#!/usr/bin/env python

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cdc.gov", None)

# Example authenticated client (needed for non-public datasets):
# client = Socrata(data.cdc.gov,
#                  MyAppToken,
#                  username="user@example.com",
#                  password="AFakePassword")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("489q-934x", limit=2000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)

## look at the unique entries in the dataset..
results_df['cause_of_death'].unique()

## Find the fire-arm related injury..

results_df = results_df[results_df['cause_of_death'] == 'Firearm-related injury']

## Each state is a wide format but I have to convert it to long format.. 

results_df.columns

## Return results with 12 months ending with quarter..
results_df = results_df[results_df['time_period']== '12 months ending with quarter']

## drop irrelevant columns in the dataset..

## First state column starts with 6 we don't want genders or male gender
results_df.drop(results_df.columns[[6,7]],axis = 1,inplace = True)

## These columns are the age rate for each mortality which we don't need.. 
results_df.drop(results_df.iloc[:,57:68],axis = 1,inplace = True)

## For the rate-type column we don't need age-adjusted rates we need crude rates which are rates per 100k population..

results_df = results_df[results_df['rate_type'] == 'Crude']

## Now that we have gathered the relevant information we can get rid of the other columns (time_period,cause_ofdeath,rate_type)

results_df.columns

results_df.drop(results_df.iloc[:,1:5],axis = 1,inplace = True)

results_df

## Now we need to convert the dataframe into a wide format into a short format and then we can rename the state columns into proper state names.

melt_df = pd.melt(results_df,id_vars = 'year_and_quarter',var_name= 'State',value_name='Firearm Mortality Per 100K')

melt_df = melt_df.sort_values(by = ['year_and_quarter','State'])

## After converting it, I will get rid of some irrelevant columns..

melt_df = melt_df[melt_df['State'] != 'rate_overall']

## Clean up the column names of the states
melt_df['State'] = melt_df['State'].apply(lambda x: x.replace('rate_',''))

## There appears to be no 2022 q4 data for the dataset so I will get rid of these entries 

melt_df = melt_df[melt_df['year_and_quarter'] != '2022 Q4']

## Captialize The State Name..
melt_df['State'] = melt_df['State'].str.capitalize()

## Remove the slash between some of the names..

melt_df['State'] = melt_df['State'].apply(lambda x: x.replace('_',' '))


## Replace all states with two words with Captial 

melt_df.replace('New york','New York',inplace = True)
melt_df.replace('New hampshire','New Hampshire',inplace = True)
melt_df.replace('New jersey','New Jersey',inplace = True)
melt_df.replace('New mexico','New Mexico',inplace = True)
melt_df.replace('District of columbia','District of Columbia',inplace = True)
melt_df.replace('North carolina','North Carolina',inplace = True)
melt_df.replace('North dakota','North Dakota',inplace = True)
melt_df.replace('Rhode island','Rhode Island',inplace = True)
melt_df.replace('South carolina','South Carolina',inplace = True)
melt_df.replace('South dakota','South Dakota',inplace = True)
melt_df.replace('West virginia','West Virginia',inplace = True)

## Now that everything is clean save it to a csv..

melt_df.to_csv('firearms-related-injury.csv',index = False)

## Now we can determine how safe a city is from glifford gun's law with various rating on state's gun laws..

dataF = pd.read_csv('https://raw.githubusercontent.com/CUNY-SPS-Data-Science-Program/your-bio-AldataSci/main/Story3/strictest-gun-laws-by-state.csv')

dataF = dataF[['state','gunLawsGiffordGrade','gunLawsGunDeathRateRank']]

dataF

## I am going to merge the two dataframe into one

new_data = pd.merge(melt_df,dataF,left_on = "State",right_on = "state",how = "left")

new_data.head(6)

## get rid of the double state column
new_data = new_data[['year_and_quarter','State','Firearm Mortality Per 100K','gunLawsGiffordGrade','gunLawsGunDeathRateRank']]


## We will have to get rid of Washington D.C sincw there are no gun laws for D.C and get the most recent year within the dataset.

new_data = new_data[new_data['State'] != 'District of Columbia']

## Just return the most recent year and quarter within the dataset
new_data = new_data[new_data['year_and_quarter'] == '2022 Q3']


## Save the clean-up data into a csv..

new_data.to_csv('FinalData.csv',index = False)





