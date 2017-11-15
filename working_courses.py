import pandas as pd
import re

#     Build out the Course Dealer Names here
course__data = pd.read_csv(r"Data Folder/course_tracking_data.csv")
courses_complete = course__data.iloc[:,24:]
email = course__data.iloc[:,2]
print(len(email.unique()))
print(len(course__data))
courses_complete = courses_complete.fillna(0)
courses_complete = courses_complete.replace("not attempted", 0)
courses_complete = courses_complete.replace("not attempted ", 0)
courses_complete = courses_complete.replace("incomplete ", 0)
courses_complete = courses_complete.replace('browsed ', 0)
courses_complete.replace("incomplete \d\d\/\d\d\/\d\d\d\d", 0, inplace=True, regex=True)

courses_complete.replace("completed \d\d\/\d\d\/\d\d\d\d", 1, inplace=True, regex=True)

###    DATA QUALITY CHECK   ###
#print(list(courses_complete.dtypes))

g = courses_complete.sum(axis = 1)
g_series = pd.Series(g)
courses_complete["Course Score"] = g_series

print(courses_complete.head())
