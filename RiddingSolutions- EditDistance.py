
# coding: utf-8
import pandas as pd
import editdistance
from unidecode import unidecode
import pickle

#   Load the CSV file, encoding was required and index was set
file = r"C:\Users\DrSynapse\Downloads\RiddingSolutions - CooperTires\Data Folder\SalesChannel.csv"
original_df = pd.read_csv(file, sep=',', header=0, encoding="ISO-8859-1")

#   Sort original Df
original_df = original_df.sort_values(['Name'], ascending=[1])

#   Creating series variables to allow for easier access.
dealer_id = original_df["Id"]
dealer_name = original_df["Name"]
dealer_add = original_df["Address1"]
dealer_city = original_df["City"]
dealer_state = original_df["StateId"]
dealer_zip = original_df["Zip"]
dealer_phone = original_df["Phone"]
dealer_level1 = original_df["ParentId"]


#   Lowering all string because case sensitivity
dealer_name = dealer_name.str.lower()
dealer_add = dealer_add.str.lower()
dealer_city = dealer_city.str.lower()
dealer_state = dealer_state.str.lower()
dealer_zip = dealer_zip.str.lower()

#   create a list of special characters to remove from the dealer list
spec_char = ['#',',','!','`','-',' ',"'",'/','\.','&','\*',':',"\+","@","\(","\)","","\?","|","\"","$",";","%","=","^","_","$","|"]

#   Remove special characters ==== ADD MORE SPEC CHARS IF NEEDED HERE === from column variables
dealer_name = dealer_name.replace(spec_char,'',regex=True)
dealer_add = dealer_add.replace(spec_char,'',regex=True)
dealer_city = dealer_city.replace(spec_char,'',regex=True)
dealer_state = dealer_state.replace(spec_char,'',regex=True)
dealer_zip = dealer_zip.replace(spec_char,'',regex=True)
dealer_phone = dealer_phone.replace(spec_char,'',regex=True)


#   Import package to convert special characters to 

decoded_dealer_name = []


#   loop through dealer_name and append the decoded version to the empty list created above. 
for name in dealer_name:
    decoded_dealer_name.append(unidecode(str(name)))
    
#   Convert list to Series
dealer_name_decoded = pd.Series(decoded_dealer_name)

#   Regex to confirm whether all strings are alphanumeric or not. 
dealer_name_decoded.str.strip()
dealer_name_decoded.str.isalnum()
dealer_name_decoded[dealer_name_decoded.str.isalnum()==False]


#   Create a subset of dealer_level1 where it equals "ValidatedDealers",'NewERDealer', 'YokohamaMasterList'
ER_series = [dealer_id, dealer_name, dealer_add, dealer_city, dealer_state, dealer_zip, dealer_phone, dealer_level1]
df = pd.DataFrame(ER_series)

#   Transpose the DataFrame and preview the data. 
df = df.T
df.tail()

#

#   Create function to concatenate fields and create unique key
#   This key is generated by combining the lowercase dealer name, address, city and state, up to 9 characters
#   
def create_unique_key(name, add, city, length_of_slice):
#   This function is where the name, address and city field (without special characters)
#   Are concatenated into a unique dealer key. This key is then used in the 
#   Levenshtein distance calculation.
    slice_name = name.str.slice(0, length_of_slice)
    slice_add = add.str.slice(0, length_of_slice)
    slice_city = city.str.slice(0, length_of_slice)
    unique_id = slice_name + slice_add + slice_city
    return unique_id


#   Uses the function, with 8 characters - Store as "unique_id"
unique_id = create_unique_key(dealer_name,dealer_add, dealer_city, 8)
unique_id = unique_id.fillna(0)


#   Create a Deep Copy of the dataset as to keep the process clean.
#   Add the newly created unique_key to the DataFrame.
validated_dealers = df.copy()
validated_dealers["Unique_Key"] = unique_id


# ## Levenshtein's Calculation

distance = []

for i in range(0, len(unique_id)-1):
#   Calculate the levenshtein's distance on the unique_key column,
#   Against the row directly below (sorted)
    ed_distance= editdistance.eval(str(unique_id.iloc[i]), str(unique_id.iloc[i+1]))
    distance.append(int(ed_distance))

#   The edit distance is calculated on the current row compared to the next rows data. 
#   Since this is the case, the last item of the list has no target to calculate distance
#   Which is why I've appended a uniquely obvious number
distance.append(9999)

#   Add the editdistance to the DataFrame
validated_dealers["Distance"] = distance
validated_dealers["Parent/Child"] = ""
validated_dealers["Child Dealer Ids"] = ""


for i in range(1, len(validated_dealers)-1):
    #   In this loop, I will be setting the Parent/Child Heirarchy, 
    # as well as include the Dealer ID of the Child to all the respective parents
    if validated_dealers.iloc[i,9] < 2:
        temp_series = validated_dealers.iloc[i,:5]
        temp_series2 = validated_dealers.iloc[i+1,:5]
        validated_dealers.iloc[i,10] = "Parent - Validated"
        validated_dealers.iloc[i+1,10] = "Child - Validated"
        validated_dealers.iloc[i,11] = validated_dealers.iloc[i+1,0] 
        #print(temp_series,"\n",temp_series2,"\n","="*50,"\n")



dupe_dealers_CooperTires = validated_dealers[validated_dealers["Parent/Child"] != ""]
validated_id_list = validated_dealers[validated_dealers["Parent/Child"] == ""]
dupe_dealers_CooperTires.to_csv(r"C:\Users\DrSynapse\Downloads\dupe_dealers_CooperTires.csv")
validated_id_list.to_csv(r"C:\Users\DrSynapse\Downloads\nondupe-dealers.csv")

pickle.dump( dupe_dealers_CooperTires, open( "dupe_dealers_CooperTires.p", "wb" ) )
pickle.dump(validated_id_list, open( "validated_id_list.p", "wb" ) )

