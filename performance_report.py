import pandas as pd 
import re
from collections import Counter
import editdistance
from cleanco import cleanco

#  Performance Report Starts here
#  Import the data
#  Strip whitespace and lowercase all columns
raw_data = pd.read_csv(r"Data Folder/Cooper Medallion and Century Daily Performance Summary Report.csv",header=0)

raw_data = raw_data.iloc[1:,:]
print("The shape of the input performance file is: " + str(raw_data.shape))
perform_tracking_data = raw_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
comp_performance_key = pd.concat([perform_tracking_data[col].astype(str).str.lower() for col in perform_tracking_data.columns], axis=1)

#   Create a function to remove business entity naming from a business name
def normalize_business_names(name):
    e = cleanco(name).clean_name()
    return e

#  Remove the entity from the dealer name and convert to a pandas Series
normalize_l = []
for val in comp_performance_key["DealerName"].values:
    normalize_l.append(normalize_business_names(val))

name_series = pd.Series(normalize_l)

#  Find and replace all non-alphanumeric with nothing
name_performance_key = name_series.str.replace(r"\W+","")
name_performance_key = name_performance_key.str.lower()
comp_performance_key["Clean Name"] = name_performance_key
#comp_performance_key["Clean Name"] = comp_performance_key["Clean Name"].shift(1)
comp_performance_key["Report"] = "Performance"
comp_performance_key = comp_performance_key[["DealerName","Clean Name","Report"]]
unit_data = raw_data[['Period', 'PeriodGoal', 'TotalUnitsPurchased', 'RequiredUnits', 'PrimaryUnits', 'Primary%', 'SecondaryUnits', 'Secondary%', 'QualifyingUnits', 'Qualifying%', 'Non-QualifyingUnits', 'Non-Qualifying%']]
unit_cols = ['Dealer Name','Key','Report','Period', 'PeriodGoal', 'TotalUnitsPurchased', 'RequiredUnits', 'PrimaryUnits', 'Primary%', 'SecondaryUnits', 'Secondary%', 'QualifyingUnits', 'Qualifying%', 'Non-QualifyingUnits', 'Non-Qualifying%']
df_performance = pd.concat([comp_performance_key,unit_data], axis=1, ignore_index=True)
df_performance.columns = unit_cols
print(df_performance.head())







#     Build out the Course Dealer Names here
course__data = pd.read_csv(r"Data Folder/course_tracking_data.csv")
course_tracking_data = course__data.iloc[:,:24]
print("The shape of the input course file is: " + str(course__data.shape))
course_tracking_data = course_tracking_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


#    Clean the dataframe to numeric only
#    Count the number of completed courses.
courses_complete = course__data.iloc[:,24:]
courses_complete = courses_complete.fillna(0)
courses_complete = courses_complete.replace("not attempted", 0)
courses_complete = courses_complete.replace("not attempted ", 0)
courses_complete = courses_complete.replace("incomplete ", 0)
courses_complete = courses_complete.replace('browsed ', 0)
courses_complete.replace("incomplete \d\d\/\d\d\/\d\d\d\d", 0, inplace=True, regex=True)
courses_complete.replace("completed \d\d\/\d\d\/\d\d\d\d", 1, inplace=True, regex=True)
email = course__data.iloc[:,2]
g = courses_complete.sum(axis = 1)
g_series = pd.Series(g)


normalize_name_key = []

for val in course_tracking_data["Business Name"].values:
    normalize_name_key.append(normalize_business_names(val))

name_key = pd.Series(normalize_name_key)
name_key = course_tracking_data["Business Name"].str.replace(r"\W+","")
comp_key = name_key.str.lower()
course_tracking_data["Clean Name"] = comp_key
course_tracking_data["Report"]= "Course"
course_tracking_data["Course Score"] = g_series
course_tracking_data = course_tracking_data.sort_values("Clean Name", ascending=True)
course_tracking_data = course_tracking_data[["E-Mail","Clean Name", "Business Name","City","State","Program Membership","Points Earned","Course Score",
                                            "Report"]]
course_tracking_data.to_csv(r"C:\Users\DrSynapse\Documents\Python Scripts\Analysis\Output Files\course_data_Nov9.csv")
df_performance.to_csv(r"C:\Users\DrSynapse\Documents\Python Scripts\Analysis\Output Files\Performance_data_Nov9.csv")
print("The shape of the output course file is: " + str(course_tracking_data.shape))
print("The shape of the output performance file is: " + str(comp_performance_key.shape))


