#!/usr/bin/env python3
"""
    Common Functions to use with Intersight API
    Libraries: pip install requests jsonpath-ng openpyxl flatten-json
"""
import sys
import os
import json
import re
import time
import requests
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def get_token(client_id, client_secret):
    """ Get oAuth Token """
    token_url="https://intersight.com/iam/token"
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {"grant_type": "client_credentials"}
    response = requests.post(url=token_url,
                            auth=client_auth,
                            data=post_data)
    if response.status_code != 200:
        print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)
    print("Successfuly obtained a new token")
    json_data = response.json()
    token = json_data["access_token"]
    return token


def get_api_data(client_id, client_secret, token, api_url):
    """ Get API Endpoint Data """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url=api_url, headers=headers)
    data = response.json()
    if	response.status_code == 401:
        print("-> Existing Token Expired. Generating a new one!")
        token = get_token(client_id, client_secret)
        get_api_data(client_id, client_secret, token, api_url)
    if response.status_code == 429:
        wait = response.headers.get("Retry-After", 600)
        print(f"-> got {response.status_code} from {api_url}. retrying after {wait}s")
        time.sleep(int(wait))
    elif response.status_code == requests.codes.ok:
        return data
    else:
        print(f"-> got {response.status_code} from {api_url}")


def get_count(client_id, client_secret, token, api_url):
    """
        Return count of API Endpoint objects
    """
    response = get_api_data(client_id, client_secret, token, api_url)
    total_count = response["Count"]
    return total_count


def get_all(client_id, client_secret, token, api_url, total_count):
    """
        Pagination code to get all the objects
    """
    increment = 1000
    skip = 0
    data = []
    while (skip <= total_count):
        if "?" in api_url:
            api_path = f"{api_url}&$top=1000&$skip={skip}"
        else:
            api_path = f"{api_url}?$top=1000&$skip={skip}"
        response = get_api_data(client_id, client_secret, token, api_path)
        data.extend(response["Results"])
        skip += increment
    return data


def get_data(client_id, client_secret, token, api_count_url, api_url):
    """
        Get Object Total Count and finally all the data
    """
    # Get Endpoint Data Count
    total_count = get_count(client_id, client_secret, token, api_count_url)
    # Get All Data
    data = get_all(client_id, client_secret, token, api_url, total_count)
    return data


def get_excel(file_name, sheet_name):
    """
        Verify if inventory file exists. If not, create one.
        Add Sheet Name based on provided sheet_name
        Return active sheet
    """
    if os.path.exists(file_name) and os.path.isfile(file_name):
        workbook = load_workbook(filename=file_name)
        sheet = workbook.active
        if len(workbook.sheetnames) == 1 and sheet.title == "Sheet":
            sheet.title = sheet_name
            workbook.save(file_name)
        elif sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.create_sheet(sheet_name)
            workbook.save(file_name)
    else:
        workbook = Workbook()
        workbook.save(file_name)
        sheet = workbook.active
        sheet.title = sheet_name
        workbook.save(file_name)
    return workbook, sheet
       

def add_header_row(sheet, header_list):
    """
        Add Headers Row to the Sheet
    """
    for column, value in enumerate(header_list, start=1):
        sheet.cell(row=1, column=column, value=value)
        cell = sheet.cell(row=1, column=column)
        custom_font = Font(name='Calibri', size=18)  
        blue_fill = PatternFill(start_color='66ccff', end_color='66ccff', fill_type='solid')
        cell.font = custom_font
        cell.fill = blue_fill


# def add_cell_data(sheet, data):
#     """
#         Add Data in Sheet Cells
#     """
#     for row, item in enumerate(data, start=2):
#         for column in range(1, len(list(item.keys()))+1):
#             sheet.cell(row=row,column=column, value=list(item.values())[column-1])
#             cell = sheet.cell(row=row, column=column)
#             custom_font = Font(name='Calibri', size=14)  
#             cell.font = custom_font
#             # cell.alignment=Alignment(vertical='center')

def add_cell_data(sheet, header_list, data):
    """
        Add Data in Sheet Cells
    """
    for row, item in enumerate(data, start=2):
        for column_name in item.keys():
            index = header_list.index(column_name)
            sheet.cell(row=row,column=index+1, value=item[column_name])
            cell = sheet.cell(row=row, column=index+1)
            custom_font = Font(name='Calibri', size=14)  
            cell.font = custom_font



def write_to_excel(file_name, sheet_name, header_list, data):
    """
        Add Data to an Excel file under the provided sheet name
    """
    # Get or Create Workbook and Sheet Name
    workbook, sheet = get_excel(file_name, sheet_name)

    # Write Sheet Headers
    # column_len = len(header_list)
    add_header_row(sheet, header_list)

    # Write Sheet Cells
    # add_cell_data(sheet, column_len, data)
    add_cell_data(sheet, header_list, data)
    
    # Save and Close Workbook
    workbook.save(file_name)
    workbook.close()


def flatten_json(y):
    """
        Flatten Json data
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def parse_data(data):
    """
        Apply flatten_json function on the data
    """
    parsed_data = []
    for item in data:
        flat_item = flatten_json(item)
        parsed_data.append(flat_item)
    return parsed_data


def remove_parameters(parsed_data):
    """
        Remove Default parameters from output
    """
    data = parsed_data
    parameters = ["ObjectType", "ClassId", "Parent_ObjectType", "Parent_ClassId", "Board_ObjectType", "Board_ClassId", "NetworkElement_ClassId", "NetworkElement_ObjectType", "RegisteredDevice_Moid", "RegisteredDevice_ClassId", "RegisteredDevice_ObjectType", "Contract_ClassId", "Contract_ObjectType", "Contract_BillTo_ClassId", "Contract_BillTo_ObjectType", "Contract_BillTo_Address1", "Contract_BillTo_Address2", "Contract_BillTo_Address3", "Contract_BillTo_City", "Contract_BillTo_Country", "Contract_BillTo_County", "Contract_BillTo_Location", "Contract_BillTo_Name", "Contract_BillTo_PostalCode", "Contract_BillTo_Province", "Contract_BillTo_State", "Contract_BillToGlobalUltimate_ClassId", "Contract_BillToGlobalUltimate_ObjectType", "Contract_BillToGlobalUltimate_Id", "Contract_BillToGlobalUltimate_Name", "Source_ClassId", "Source_ObjectType", "Source_Moid", "Source_Name", "Source_PlatformType"]
    for item in data:
        for p in parameters:
            if p in item:
                item.pop(p)
    return data


def auto_size_columns(file_name, sheet_name):
    """
        Iterate over all columns and adjust their widths
    """
    workbook, sheet = get_excel(file_name, sheet_name)
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 10)
        sheet.column_dimensions[column_letter].width = adjusted_width
    # Save and Close Workbook
    workbook.save(file_name)
    workbook.close()


def find_empty_slots(data):
    """
        Find Empty Slots in Chassis
        Output Domain Id, Chassis Id, Slot Id.
    """
    occupied_slots = {}
    for blade in data:
        server_name = blade["Name"]
        parsed_name = re.search(r"^(.+)-(\d+)-(\d)", server_name)
        domain_id = parsed_name.group(1)
        chassis_id = parsed_name.group(2)
        server_id = parsed_name.group(3)
        if domain_id not in occupied_slots.keys():
            occupied_slots[domain_id] = {}
        if chassis_id not in occupied_slots[domain_id].keys():
            occupied_slots[domain_id][chassis_id] = []
        if server_id not in occupied_slots[domain_id][chassis_id]:
            occupied_slots[domain_id][chassis_id].append(server_id)
    
    empty_slots = {}
    for domain_id,chassis in occupied_slots.items():
        for chassis_id,servers in chassis.items():
            for i in range(1,9):
                if str(i) not in servers:
                    domain_id = domain_id
                    chassis_id = chassis_id
                    server_id = str(i)
                    if domain_id not in empty_slots.keys():
                        empty_slots[domain_id] = {}
                    if chassis_id not in empty_slots[domain_id].keys():
                        empty_slots[domain_id][chassis_id] = []
                    if server_id not in empty_slots[domain_id][chassis_id]:
                        empty_slots[domain_id][chassis_id].append(server_id)
    
    parsed_data = []
    for domain_id,chassis in empty_slots.items():
        for chassis_id,servers in chassis.items():
            server_ids = ', '.join(servers)
            data_dict = {
                "domain_id": domain_id,
                "chassis_id": chassis_id,
                "server_slots": server_ids
            }
            parsed_data.append(data_dict)
    return parsed_data


def create_hyperlinks_sheet(file_name):
    """
        Create a Hyperlinks sheet pointing to all the Sheets in excel
    """
    sheet_name = "Hyperlinks"
    workbook, sheet = get_excel(file_name, sheet_name)

    # Set Header Row
    sheet.cell(row=1, column=1, value="Hyperlinks")
    cell = sheet.cell(row=1, column=1)
    custom_font = Font(name='Calibri', size=18)  
    blue_fill = PatternFill(start_color='66ccff', end_color='66ccff', fill_type='solid')
    cell.font = custom_font
    cell.fill = blue_fill

    # Add Hyperlinks
    sheets = workbook.sheetnames
    if "Hyperlinks" in sheets:
        sheets.remove('Hyperlinks')

    for i,sheet_name in enumerate(sheets, start=2):
        cell_font = Font(name="Calibri", underline="single", size=18, color="0066cc")
        cell_value = sheet_name.upper()
        link_value = f"#{sheet_name}!A{i}"
        sheet.cell(row=i, column=1, value=cell_value).hyperlink = link_value
        sheet.cell(row=i, column=1).font = cell_font

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 10)
        sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Save and close Workbook
    workbook.save(file_name)
    workbook.close()

def set_default_sheet(file_name, sheet_name):
    workbook = load_workbook(filename=file_name)

    # Get the sheet's current position (index)
    sheet_index = workbook.sheetnames.index(sheet_name)
    new_position = - sheet_index
    
    # Move sheet to Index 0
    workbook.move_sheet(sheet_name, new_position)

    # Set Active sheet
    workbook.active = workbook[sheet_name]

    # Save the changes
    workbook.save(file_name) 
    workbook.close()

def get_licenses(data):
    """
        Get Server Licenses
    """
    license_data = []
    for d in data:
        license_dict = {}
        license_dict['Name'] = d['Name']
        license_dict['Serial'] = d['Serial']
        license_dict['Model'] = d['Model']
        for k,v in d.items():
            if "Intersight.LicenseTier" == v:
                prefix = k.split("_Key")[0]
                license_key = f"{prefix}_Value"
                license_dict["LicenseTier"] = d[license_key]
        license_data.append(license_dict)
    return license_data


def get_sp_policies(data):
    """
        Get Server Profile and its associated Policies
    """
    sp_data = []
    for d in data:
        sp_dict = {}
        sp_dict['SP_Name'] = d['Name']
        sp_dict['SP_Moid'] = d['Moid']
        sp_dict['TargetPlatform'] = d['TargetPlatform']
        if 'AssociatedServer' in d.keys():
            if d['AssociatedServer'] == None:
                sp_dict['Server_Name'] = ""
                sp_dict['Server_Serial'] = ""
                sp_dict['Server_Model'] = ""
        else:
            if 'AssociatedServer_Name' in d.keys():
                sp_dict['Server_Name'] = d['AssociatedServer_Name']
            # if 'AssociatedServer_Serial' in d.keys():
                sp_dict['Server_Serial'] = d['AssociatedServer_Serial']
            # if 'AssociatedServer_Model' in d.keys():
                sp_dict['Server_Model'] = d['AssociatedServer_Model']
        for k,v in d.items():
            if "ClassId" in k and "PolicyBucket" in k:
                prefix = k.split("_ClassId")[0]
                policy_key = f"{prefix}_Name"
                sp_dict[v] = d[policy_key]                                                         
        sp_data.append(sp_dict)
    return sp_data
