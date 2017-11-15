import pandas as pd
import re

#     Build out the Course Dealer Names here
course__data = pd.read_csv(r"Data Folder/course_tracking_data.csv")
course_contact = course__data.iloc[:,:10]
courses_complete = course__data.iloc[:,24:]
email = course__data.iloc[:,2]
#len(email.unique()))

print(course_contact.head())
courses_complete = courses_complete.fillna(0)
courses_complete = courses_complete.replace("not attempted", 0)
courses_complete = courses_complete.replace("not attempted ", 0)
courses_complete = courses_complete.replace("incomplete ", 0)
courses_complete = courses_complete.replace('browsed ', 0)
courses_complete.replace("incomplete \d\d\/\d\d\/\d\d\d\d", 0, inplace=True, regex=True)

courses_complete.replace("completed \d\d\/\d\d\/\d\d\d\d", 1, inplace=True, regex=True)

###    DATA QUALITY CHECK   ###
#print(list(courses_complete.columns))

g = courses_complete.sum(axis = 1)
g_series = pd.Series(g)
course_contact["Course Score"] = g_series

#course_contact.to_csv(r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Output Files\course_score.csv")

test_course = pd.read_csv(r"Output Files/course_data_Nov14.csv")
print(test_course.head())
