###       ARE DEALERS WITH HIGHER TRAINING SELLING MORE?   ###


#  This script will be customized to the Daily Performance Summary Report where it will consolidate dealers
#  And accurately report whether training Sales Associates is really worth
#  the investment.

#IDEAL#
#For every 1 training dollar spent, you"re receiving X much EXTRA revenue.
#(hint: we can do this)#


# import statements
import pandas as pd 
import re
from collections import Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#raw_data = pd.read_csv(r"Data Folder/Cooper Medallion and Century Daily Performance Summary Report.csv",skiprows= 1)
course_tracking_data = pd.read_csv(r"Data Folder/course_tracking_data.csv")
course_tracking_data = course_tracking_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# separate the dataset into the 2 important pieces
id_data = course_tracking_data.iloc[:,:24]
course_data = course_tracking_data.iloc[:,24:]

#  clean up the data to create either complete or emtpy
course_data = course_data.replace("not attempted","")
course_data = course_data.fillna("")
course_data_clean = course_data.replace("incomplete","")
course_data_clean = course_data.replace(r"\w+|/","Complete", regex=True)
course_data_clean = course_data_clean.replace("Complete CompleteCompleteCompleteCompleteComplete","Complete")
course_data_clean = course_data_clean.replace("Complete",1)

#  initialize empty list 
#  append the count of "1" - or completed course - to this empty list
#  indexed by row
v_of_rows = []

for idx, df in course_data_clean.iterrows():
    c = Counter(df.values)
    v_of_rows.append(c[1])


#  Append the count of courses to both dataframes (could be used to join)
course_data_clean["Courses Complete"] = v_of_rows
id_data["Courses Complete"] = v_of_rows

#  Drop unnecessary columns
#  Order the columns as you'd like
id_data = id_data.drop(["Customer Type","Program Membership","Preferred Language","Zip","Country","Sales Office","Last Login","Terms of Use"], 1)
l_of_id_columns = list(id_data.columns)

id_data = id_data[["First Name", "Last Name", "E-Mail", "Phone", "Job Title", "Business Name",
 "Address", "City", "State","Membership/Store Number","Tire Brands Carried",
  "Sales Group", "Cooper Region", "Date Registered",
 "User Status", "Points Earned", "Courses Complete"]]                

_key_data = id_data.copy()
#   Generate a concatenated key from clean data fields
#   Begin by creating a deep copy of the original df

comp_key = pd.concat([_key_data[col].astype(str).str.lower() for col in _key_data.columns], axis=1)



#  Find and replace all non-alphanumeric with nothing
name_key = comp_key["Business Name"].str.replace(r"\W+","")
add_key = comp_key["Address"].str.replace(r"\W+","")
city_key = comp_key["City"].str.replace(r"\W+","")


def create_unique_key(name, add, city, length_of_slice):
#   This function is where the name, address and city field (without special characters)
#   Are concatenated into a unique dealer key. This key is then used in the 
#   Levenshtein distance calculation.
    slice_name = name.str.slice(0, length_of_slice)
    slice_add = add.str.slice(0, length_of_slice)
    slice_city = city.str.slice(0, length_of_slice)
    unique_id = slice_name + slice_add + slice_city
    return unique_id

#   Store the key in a new var
#   Add the unique key to the dataframe
unique_key = create_unique_key(name_key, add_key, city_key, 8)
id_data["Generated Key"] = unique_key

#   sort the dataframe by this generated key to begin the edit distance process.
sorted_data = id_data.sort_values("Generated Key")
#   store the key column as unique_id
unique_id = sorted_data["Generated Key"]

sorted_data = sorted_data.drop(["First Name","Last Name","E-Mail","Phone","Job Title"], 1)
# ## Levenshtein's Calculation
###############################
distance = []
for i in range(0, len(unique_id)-1):
#   Calculate the levenshtein's distance on the unique_key column,
#   Against the row directly below (sorted)
    ed_distance= fuzz.token_sort_ratio(str(unique_id.iloc[i]), str(unique_id.iloc[i+1]))
    distance.append(int(ed_distance))

#   The edit distance is calculated on the current row compared to the next rows data. 
#   Since this is the case, the last item of the list has no target to calculate distance
#   Which is why I've appended a uniquely obvious number
distance.append(9999)
#   Add the edit distance to the dataframe
sorted_data["Edit Distance"] = distance

sorted_data.loc[sorted_data["Edit Distance"] <= 2, 'IsMatch'] = 'Dupe'
sorted_data.loc[sorted_data["Edit Distance"] > 2, 'IsMatch'] = 'NotDupe'

sorted_data.loc[sorted_data["IsMatch"] == "NotDupe" , 'Heirarchy'] = 'Unique'
sorted_data.loc[(sorted_data["IsMatch"] == "NotDupe") & (sorted_data["IsMatch"].shift(1) == "Dupe"), 'Heirarchy'] = 'G'
sorted_data.loc[sorted_data["IsMatch"] == "Dupe" , 'Heirarchy'] = 'G'


sorted_data.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\working_copy_Oct28.csv")

