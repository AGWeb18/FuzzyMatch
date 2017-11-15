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

def strip_clean(fields):
    fields = pd.Series(fields)
    fields = fields.str.replace(r"\W+","")
    fields = fields.str.lower()
    return fields


name_performance_key = strip_clean(normalize_l)



comp_performance_key["Clean Name"] = name_performance_key
comp_performance_key["Report"] = "Performance"
comp_performance_key = comp_performance_key[["DealerNbr","DealerName","Report"]]



def create_unique_key(name, add, city, length_of_slice):
#   This function is where the name, address and city field (without special characters)
#   Are concatenated into a unique dealer key. This key is then used in the 
#   Levenshtein distance calculation.
    slice_name = name.str.slice(0, length_of_slice)
    slice_add = add.str.slice(0, length_of_slice)
    slice_city = city.str.slice(0, length_of_slice)
    unique_id = slice_name + slice_add + slice_city
    return unique_id



unit_data = raw_data[['Period', 'PeriodGoal', 'TotalUnitsPurchased', 'RequiredUnits', 'PrimaryUnits', 'Primary%', 'SecondaryUnits', 'Secondary%', 'QualifyingUnits', 'Qualifying%', 'Non-QualifyingUnits', 'Non-Qualifying%']]
unit_cols = ["DealerNbr","DealerName","Report",'Period', 'PeriodGoal', 'TotalUnitsPurchased', 'RequiredUnits', 'PrimaryUnits', 'Primary%', 'SecondaryUnits', 'Secondary%', 'QualifyingUnits', 'Qualifying%', 'Non-QualifyingUnits', 'Non-Qualifying%']
df_performance = pd.concat([comp_performance_key,unit_data], axis=1, ignore_index=True)
df_performance.columns = unit_cols




#     Build out the Course Dealer Names here
course__data = pd.read_csv(r"Data Folder/course_tracking_data.csv")

course_tracking_data = course__data.iloc[:,:24]
course_tracking_data = course_tracking_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print("The shape of the input course file is: " + str(course__data.shape))


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

g = courses_complete.sum(axis = 1)
g_series = pd.Series(g)


normalize_name_key = []

for val in course_tracking_data["Business Name"].values:
    normalize_name_key.append(normalize_business_names(val))

comp_key = strip_clean(normalize_name_key)
course_tracking_data["Clean Name"] = comp_key
course_tracking_data["Report"]= "Course"
course_tracking_data = course_tracking_data[['Business Name', 'Clean Name',"Report", "Address", "City"]]
course_tracking_data.columns = ["Name", "Clean Name","Report", "Address", "City"]
course_name = course_tracking_data["Clean Name"]
course_add = course_tracking_data["Address"]
course_city = course_tracking_data["City"]

course_name = strip_clean(course_name)
course_add = strip_clean(course_add)
course_city = strip_clean(course_city)
course_key = create_unique_key(course_name,course_add,course_city, 8)
course_tracking_data["Key"] = course_key
course_tracking_data["Count of Courses"] = g_series



#     Build out the Course Dealer Names here
enrollment_data = pd.read_csv(r"Data Folder/MedallionCenturyenrollment.csv")
print("The shape of the input performance file is: " + str(enrollment_data.shape))

enrollment_data = enrollment_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

normalize_enrol_key = []

for val in enrollment_data["Dealer Name"].values:
    normalize_enrol_key.append(normalize_business_names(val))

enroll_key = strip_clean(normalize_enrol_key)
enrollment_data["Clean Name"] = enroll_key

enroll_name = enrollment_data["Dealer Name"]
enroll_add = enrollment_data["Store Address Line 1"]
enroll_city= enrollment_data["Store City"]
enroll_name = strip_clean(enroll_name)
enroll_add = strip_clean(enroll_add)
enroll_city = strip_clean(enroll_city)

enroll_df_key = create_unique_key(enroll_name,enroll_add,enroll_city, 8)
enrollment_data["Key"] = enroll_df_key


print(enrollment_data.head())
enrollment_data.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\enroll_data_Nov14.csv")
course_tracking_data.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\course_data_Nov14.csv")
df_performance.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\Performance_data_Nov14.csv")
