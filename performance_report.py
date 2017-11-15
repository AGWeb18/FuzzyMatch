import pandas as pd 
import re
from collections import Counter
import editdistance
from cleanco import cleanco

#  Performance Report Starts here
raw_data = pd.read_csv(r"Data Folder/Performance_data_Nov4 - Sheet1.csv",header=0)
raw_data = raw_data.iloc[1:,:]
perform_tracking_data = raw_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
comp_performance_key = pd.concat([perform_tracking_data[col].astype(str).str.lower() for col in perform_tracking_data.columns], axis=1)

def normalize_business_names(name):
    e = cleanco(name).clean_name()
    return e


normalize_l = []

for val in comp_performance_key["Name"].values:
    normalize_l.append(normalize_business_names(val))



def strip_clean(fields):
    fields = pd.Series(fields)
    fields = fields.str.replace(r"\W+","")
    fields = fields.str.lower()
    return fields

name_performance_key = strip_clean(normalize_l)




comp_performance_key["Clean Name"] = name_performance_key
comp_performance_key["Report"] = "Performance"
comp_performance_key = comp_performance_key[["Id","Name","Address1","City","Clean Name","Report"]]
name_dealer = comp_performance_key["Name"]
add_dealer = comp_performance_key["Address1"]
city_dealer = comp_performance_key["City"]


def create_unique_key(name, add, city, length_of_slice):
#   This function is where the name, address and city field (without special characters)
#   Are concatenated into a unique dealer key. This key is then used in the 
#   Levenshtein distance calculation.
    slice_name = name.str.slice(0, length_of_slice)
    slice_add = add.str.slice(0, length_of_slice)
    slice_city = city.str.slice(0, length_of_slice)
    unique_id = slice_name + slice_add + slice_city
    return unique_id

name_dealer = strip_clean(name_dealer)
add_dealer = strip_clean(add_dealer)
city_dealer = strip_clean(city_dealer)
concat_key = create_unique_key(name_dealer,add_dealer,city_dealer, 8)
comp_performance_key["Key"] = concat_key




#     Build out the Course Dealer Names here
course_tracking_data = pd.read_csv(r"Data Folder/course_data.csv")
course_tracking_data = course_tracking_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

normalize_name_key = []

for val in course_tracking_data["DealerName"].values:
    normalize_name_key.append(normalize_business_names(val))

comp_key = strip_clean(normalize_name_key)
course_tracking_data["Clean Name"] = comp_key
course_tracking_data["Report"]= "Course"
course_tracking_data = course_tracking_data[['DealerName', 'Clean Name',"Report", "Address", "City"]]
course_tracking_data.columns = ["DealerName", "Clean Name","Report", "Address", "City"]
course_name = course_tracking_data["DealerName"]
course_add = course_tracking_data["Address"]
course_city = course_tracking_data["City"]

course_name = strip_clean(course_name)
course_add = strip_clean(course_add)
course_city = strip_clean(course_city)
course_key = create_unique_key(course_name,course_add,course_city, 8)
course_tracking_data["Key"] = course_key



#     Build out the Course Dealer Names here
enrollment_data = pd.read_csv(r"Data Folder/MedallionCenturyenrollment.csv")
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



enrollment_data.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\enroll_data_Nov14.csv")
course_tracking_data.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\course_data_Nov14.csv")
comp_performance_key.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\Performance_data_Nov14.csv")
