# intersight_reports
Create Intersight_report.xlsx file with below data:
- Inventory - FI, Chassis's, IOM's, Servers, PSUs, FANs, CPUs, DIMMs, etc.
- licensing info
- Contract Info
- FI Disk Usage
- Empty Chassis Slots Info
- Server Profile, Associated Server and Associated Policies 

# Usage
- Install Python Libraries: pip install requests jsonpath-ng openpyxl flatten-json
- Generate Intersight oAuth ClientID, ClientSecret and add thoses under the .env file.
- Update permissions on the script: chmod 755 generate_report.py
- Execute Script: ./generate_report.py

Sample Output:

```Python3
 % ./get_inventory.py
Successfuly obtained a new token
Creating Sheet: fi
Creating Sheet: chassis
Creating Sheet: iom
Creating Sheet: x-fabric_modules
Creating Sheet: motherboards
Creating Sheet: blades
Creating Sheet: racks
Creating Sheet: psu
Creating Sheet: fan_module
Creating Sheet: fan
Creating Sheet: cpu
Creating Sheet: memory
Creating Sheet: memory_array
Creating Sheet: network_adapter
Creating Sheet: storage_controller
Creating Sheet: physical_drive
Creating Sheet: virtual_drive
Creating Sheet: tpm
Creating Sheet: pci_devices
Creating Sheet: transceivers
Creating Sheet: Empty_Chassis_Slots
Creating Sheet: FI_Disk_Usage
Creating Sheet: Contracts
Creating Sheet: licenses
Creating Sheet: sp_policies
Creating Sheet: Hyperlinks
```

### Additional Info
- This script creates a single Intersight_reports.xlsx file with multiple sheets.
- Each Sheet contains data for invidividual report. 
  E.g. Sheet Names: fi, chassis, iom, etc. 
- Hyperlinks sheet includes pointers to all the sheets
