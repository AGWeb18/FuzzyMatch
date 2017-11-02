import pandas as pd 
import re
from collections import Counter
import editdistance
from cleanco import cleanco

#  Performance Report Starts here
raw_data = pd.read_csv(r"Data Folder/Cooper Medallion and Century Daily Performance Summary Report.csv",header=0)
raw_data = raw_data.iloc[1:,:]
perform_tracking_data = raw_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
comp_performance_key = pd.concat([perform_tracking_data[col].astype(str).str.lower() for col in perform_tracking_data.columns], axis=1)

def normalize_business_names(name):
    e = cleanco(name).clean_name()
    return e


normalize_l = []

for val in comp_performance_key["DealerName"].values:
    normalize_l.append(normalize_business_names(val))


name_series = pd.Series(normalize_l)

#  Find and replace all non-alphanumeric with nothing
name_performance_key = name_series.str.replace(r"\W+","")
comp_performance_key["Clean Name"] = name_performance_key
comp_performance_key["Clean Name"] = comp_performance_key["Clean Name"].shift(1)
comp_performance_key["Report"] = "Performance"
comp_performance_key = comp_performance_key[["DealerName","Clean Name","Report"]]


#     Build out the Course Dealer Names here
course_tracking_data = pd.read_csv(r"Data Folder/course_tracking_data.csv")
course_tracking_data = course_tracking_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


normalize_name_key = []

for val in course_tracking_data["Business Name"].values:
    normalize_name_key.append(normalize_business_names(val))

name_key = pd.Series(normalize_name_key)

name_key = course_tracking_data["Business Name"].str.replace(r"\W+","")
comp_key = name_key.str.lower()
course_tracking_data["Clean Name"] = comp_key

course_tracking_data["Report"]= "Course"
course_tracking_data = course_tracking_data[['Business Name', 'Clean Name',"Report"]]
course_tracking_data.columns = ["DealerName", "Clean Name","Report"]
print(name_performance_key)

#performance_name = name_performance_key["Clean Name"]

#  Append these two dataframes, keep their index's
df_master = comp_performance_key.append(course_tracking_data)
#df_master = df_master.dropna()
df_master = df_master.sort_values("Clean Name", ascending=True)


df_master["Match"] = ""

for x in df_master["Clean Name"]:
    if [comp_key.isin([x]) & name_performance_key.isin([x])]:
        df_master["Match"] = "Match Found"
        
#df_master["Match"] = ["Both Found" if comp_key.isin([x]) and name_performance_key["Clean Name"].isin([x]) else '' for x in df_master["Clean Name"]]


df_master.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\working_copy_Oct29_v3.csv")

