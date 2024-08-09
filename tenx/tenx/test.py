import json

def format_currency(value):
    if value is None:
        return value
    try:
        if value >= 1_000_000_000:
            formatted_value = f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            formatted_value = f"${value / 1_000_000:.1f}M"
        elif value >= 1_000:
            formatted_value = f"${value / 1_000:.1f}k"
        else:
            formatted_value = f"${value}"
        return formatted_value
    except (TypeError, ValueError):
        return value
    
def format_as_percentage(value):
    if value is None:
        return value
    try:
        # Try to convert the value to a float and format as a percentage
        float_value = float(value)
        return f"{float_value}%"
    except ValueError:
        # If conversion fails, return the original value
        return value
    
def format_number(value):
    if value is None:
        return value
    try:
        # Try to convert the value to a float
        float_value = float(value)
        
        # Check if the float value is an integer
        if float_value.is_integer():
            float_value = int(float_value)
        
        # Format based on the value
        if float_value >= 1_000_000_000:
            return f"{float_value / 1_000_000_000:.1f}B"
        elif float_value >= 1_000_000:
            return f"{float_value / 1_000_000:.1f}M"
        elif float_value >= 1_000:
            return f"{float_value / 1_000:.1f}k"
        else:
            return float_value if isinstance(float_value, float) else int(float_value)
    except ValueError:
        # If conversion fails, return the original value
        return value
    
def convert_to_percentage(value):
    if value is None:
        return value
    try:
        # Try to convert the value to a float
        float_value = float(value)
        
        # Convert to percentage and format to one decimal place
        percentage_value = float_value * 100
        formatted_percentage = f"{percentage_value:.1f}%"
        
        return formatted_percentage
    except ValueError:
        # If conversion fails, return the original value
        return value



# Specify the path to your JSON file
file_path = 'cc.json'

# Open the file and load the data
with open(file_path, 'r') as file:
    costar_data = json.load(file)


datas=costar_data.get('data','').get('marketOverview','').get('salesVolume','').get('header','')
item={}
if len(datas)>0:
    for data in datas:
        header_1 = data.get('displayName','')
        item[header_1] = format_currency(data.get('value',''))
datas2=costar_data.get('data','').get('marketOverview','').get('salesVolume','').get('rows','')
if len(datas2)>0:
    for dat in datas2:
        header_1 = dat.get('displayName','')
        value_type = dat.get('valueType','')
        sub_datas=dat.get('columns','')
        if len(sub_datas)>0:
            for sub_dt in sub_datas:
                sub_header1 = sub_dt.get('displayName','')
                if value_type =='CURRENCY':
                    
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = format_currency(sub_dt.get('value',''))
                elif value_type == 'PERCENTAGE':
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = convert_to_percentage(sub_dt.get('value',''))
                
                elif value_type == 'NUMBER':
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = format_number(sub_dt.get('value',''))
                else:
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = sub_dt.get('value','')
datas3=costar_data.get('data','').get('marketOverview','').get('salesPrice','').get('header','')
# item={}
if len(datas3)>0:
    for idx, data_3 in enumerate(datas3):
        header_1 = data_3.get('displayName','')
        if idx==0:
            
            item[header_1] = convert_to_percentage(data_3.get('value',''))
        else:
            item[header_1] = convert_to_percentage(data_3.get('value',''))

datas4=costar_data.get('data','').get('marketOverview','').get('salesPrice','').get('rows','')
if len(datas4)>0:
    for dat4 in datas4:
        header_1 = dat4.get('displayName','')
        value_type = dat4.get('valueType','')
        sub_datas=dat4.get('columns','')
        if len(sub_datas)>0:
            for sub_dt in sub_datas:
                sub_header1 = sub_dt.get('displayName','')
                if value_type =='CURRENCY':
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = format_currency(sub_dt.get('value',''))
                elif value_type == 'PERCENTAGE':
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = format_as_percentage(sub_dt.get('value',''))
                
                elif value_type == 'NUMBER':
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = format_number(sub_dt.get('value',''))
                else:
                    sub_header_value = sub_dt.get(sub_header1)
                    item[f'{header_1}_{sub_header1}'] = sub_dt.get('value','')

# Extract sales volume data
# sales_volume_headers = costar_data.get('data', {}).get('marketOverview', {}).get('salesVolume', {}).get('header', [])
# sales_volume_rows = costar_data.get('data', {}).get('marketOverview', {}).get('salesVolume', {}).get('rows', [])

# # Initialize dictionary to store formatted data
# formatted_data = {}

# # Process sales volume headers
# for header_data in sales_volume_headers:
#     header_name = header_data.get('displayName', '')
#     formatted_data[header_name] = format_currency(header_data.get('value', ''))

# # Process sales volume rows and their columns
# for row_data in sales_volume_rows:
#     row_name = row_data.get('displayName', '')
#     value_type = row_data.get('valueType', '')
#     columns = row_data.get('columns', [])

#     for column_data in columns:
#         column_name = column_data.get('displayName', '')
#         sub_header_value = column_data.get(column_name)
        
#         if value_type == 'CURRENCY':
#             formatted_data[f'{row_name}_{column_name}'] = format_currency(column_data.get('value', ''))
#         elif value_type == 'PERCENTAGE':
#             formatted_data[f'{row_name}_{column_name}'] = format_as_percentage(column_data.get('value', ''))
#         elif value_type == 'NUMBER':
#             formatted_data[f'{row_name}_{column_name}'] = format_number(column_data.get('value', ''))
#         else:
#             formatted_data[f'{row_name}_{column_name}'] = column_data.get('value', '')

# # Extract sales price data
# sales_price_headers = costar_data.get('data', {}).get('marketOverview', {}).get('salesPrice', {}).get('header', [])
# sales_price_rows = costar_data.get('data', {}).get('marketOverview', {}).get('salesPrice', {}).get('rows', [])

# # Process sales price headers
# for idx, header_data in enumerate(sales_price_headers):
#     header_name = header_data.get('displayName', '')
#     if idx == 0:
#         formatted_data[header_name] = format_currency(header_data.get('value', ''))
#     else:
#         formatted_data[header_name] = header_data.get('value', '')

# # Process sales price rows and their columns
# for dat4 in sales_price_rows:
#     header_name = dat4.get('displayName', '')
#     value_type = dat4.get('valueType', '')
#     sub_datas = dat4.get('columns', [])

#     for sub_dt in sub_datas:
#         sub_header_name = sub_dt.get('displayName', '')
#         sub_header_value = sub_dt.get(sub_header_name)
        
#         if value_type == 'CURRENCY':
#             formatted_data[f'{header_name}_{sub_header_name}'] = format_currency(sub_dt.get('value', ''))
#         elif value_type == 'PERCENTAGE':
#             formatted_data[f'{header_name}_{sub_header_name}'] = format_as_percentage(sub_dt.get('value', ''))
#         elif value_type == 'NUMBER':
#             formatted_data[f'{header_name}_{sub_header_name}'] = format_number(sub_dt.get('value', ''))
#         else:
#             formatted_data[f'{header_name}_{sub_header_name}'] = sub_dt.get('value', '')
breakpoint()
# Print or return formatted data as needed
print(item)
