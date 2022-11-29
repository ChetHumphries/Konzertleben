import csv
import json
import pandas as pd
from tqdm import tqdm
from urllib.request import urlopen


# We read in a csv of GND numbers, and save this to a dataframe
gnd_csv = open('/Users/chestonhumphries/Desktop/gnd_test.csv', 'r')
data = list(csv.reader(gnd_csv, delimiter=','))
gnd_csv.close()
# gnd_csv = pd.read_csv('/Users/chestonhumphries/Desktop/gnd_test.csv')
data_list = []


# We iteratively append the GND numbers to our base URL string to reach the corresponding JSON
def get_json(gnd_number):
    base_url = 'https://hub.culturegraph.org/entityfacts/'
    record_url = base_url+gnd_number

    response = urlopen(record_url)
    data_json = json.loads(response.read())
    cols = ['id', 'preferredName', 'surname', 'forename', 'dateOfBirth', 'dateOfDeath', 'placeOfBirth', 'placeOfDeath']
    alt_cols = ['alternate_names', 'id']
    row = []
    row.append(gnd_number)
    # We parse the JSON for the information we're interested in, and save it to a dataframe
    try:
        row.append(data_json['preferredName'])
    except:
        row.append('unknown')
    try:
        row.append(data_json['surname'])
    except:
        row.append('unknown')
    try:
        row.append(data_json['forename'])
    except:
        row.append('unknown')
    try: 
        row.append(data_json['dateOfBirth'])
    except:
        row.append('unknown')
    try:
        row.append(data_json['dateOfDeath'])
    except:
        row.append('unknown')
    try:
        row.append(data_json['placeOfBirth'][0]['preferredName'])
    except:
        row.append('unknown')
    try:
        row.append(data_json['placeOfDeath'][0]['preferredName'])
    except:
        row.append('unknown')       
    if 'variantName' in data_json:
        df_nested_list = pd.json_normalize(data_json, record_path =['variantName'])
        df_nested_list['id'] = gnd_number
        df_nested_list.columns = alt_cols
    else:
        df_nested_list = pd.DataFrame(columns=alt_cols)

    
    reshaped = pd.DataFrame([row])
    reshaped.columns=cols


    return reshaped, df_nested_list

data = data[0]
alternate_names_concat_list = []
for gnd_number in tqdm(data):
    data_json, alternate_names = get_json(gnd_number)
    data_list.append(data_json)
    alternate_names_concat_list.append(alternate_names)

final_data = pd.concat(data_list, ignore_index=True)
final_alt_names = pd.concat(alternate_names_concat_list, ignore_index=True)
print('Data collection complete')

# We dump the dataframe as a JSON
print('Writing person data to JSON...')
out_file = open("konzertleben_persons.json", "w")
json.dump(final_data.to_dict(), out_file, indent = 6)
out_file.close()
print('Person file complete!')

print('Writing alternate names to JSON...')
out_file = open('konzertleben_alt_persons.json', 'w')
json.dump(final_alt_names.to_dict(), out_file, indent=6)
out_file.close()
print('Alternate names file complete!')