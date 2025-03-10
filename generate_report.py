#!/usr/bin/env python3
"""
    Create Intersight Inventory.xlsx file
    Creates separate sheets for each component
    Components:
        FI, 
        Chassis, IOM, x-fabric_modules, PCI Nodes
        PSU, Fan Modules, FANs, 
        Server, CPU, Memory, Network Adapters, Storage Controllers
            Physical Drive, Virtual Drive, TPM, PCI Devices

"""
import os
import json
from pprint import pprint
from dotenv import load_dotenv, find_dotenv
from common import get_token, get_data, parse_data
from common import write_to_excel, remove_parameters, auto_size_columns
from common import find_empty_slots, create_hyperlinks_sheet, set_default_sheet
from common import get_licenses, get_sp_policies

load_dotenv(find_dotenv())

if __name__ == '__main__':
    # Set variables
    client_id = os.getenv("ClientId")
    client_secret = os.getenv("ClientSecret")

    # Get oAuth Token
    token = get_token(client_id, client_secret)

    with open('inventory_urls.json', 'r') as f:
        json_data = json.load(f)

    for k,v in json_data.items():
        base_path = "https://intersight.com/api/v1/"
        endpoint_path = v['path']
        query_parameters = v['query_parameters']

        api_count_url = f"{base_path}{endpoint_path}?$count=True"
        if query_parameters != "":
            api_url = f"{base_path}{endpoint_path}?{query_parameters}"
        else:
            api_url = f"{base_path}{endpoint_path}"
  

        # Intersight API Nested Data        
        data = get_data(client_id, client_secret, token, api_count_url, api_url)
        
        if data:
            # Flattened Data
            semi_parsed_data = parse_data(data)

            # Remove Parameters from Parsed Data before Writing
            parsed_data = remove_parameters(semi_parsed_data)

            # Write Flattened Data to a JSON file
            data_file = f"./Data/{k}.json"

            if k == "Empty_Chassis_Slots":
                data = find_empty_slots(parsed_data)
                parsed_data = data

            if k == "licenses":
                data = get_licenses(parsed_data)
                parsed_data = data
            
            if k == "sp_policies":
                # pprint(parsed_data)
                data = get_sp_policies(parsed_data)
                parsed_data = data

            if k == "network_veths":
                vnic_data = get_vnic_ethifs(client_id, client_secret, token, parsed_data)
                parsed_data = vnic_data

            # Create Data json file
            with open(data_file, 'w') as f:
                f.write(json.dumps(parsed_data))

            # Create Excel File
            file_name = "./Data/Inventory.xlsx"   # Update
            sheet_name = k           # Update
        
            print(f"Creating Sheet: {k}")
            header_list = []
            for d in parsed_data:
                for k in d.keys():
                    if k not in header_list:
                        header_list.append(k)

            # header_list = list(parsed_data[0].keys())

            # for k,v in enumerate(json_data):
            #     row_data = list(v.values())

            # Write to Elsx file
            write_to_excel(file_name, sheet_name, header_list, parsed_data)

            # Autofit Columns in sheet
            auto_size_columns(file_name, sheet_name)

    # Create Hyperlinks Sheet
    file_name = "./Data/Inventory.xlsx"
    print(f"Creating Sheet: Hyperlinks")
    create_hyperlinks_sheet(file_name)

    # Set Hyperlinks as Default Sheet
    sheet_name = "Hyperlinks"
    set_default_sheet(file_name, sheet_name)
