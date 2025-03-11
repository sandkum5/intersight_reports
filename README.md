# intersight_reports
Create Intersight_report.xlsx file with below data:
- Inventory - FI, Chassis's, IOM's, Servers, PSUs, FANs, CPUs, DIMMs, etc.
- licensing info
- Contract Info
- FI Disk Usage
- Empty Chassis Slots Info
- Server Profile, Associated Server and Associated Policies
- vNIC and vHBA Info

# Usage
- Install Python Libraries: pip install requests jsonpath-ng openpyxl flatten-json
- Generate Intersight oAuth ClientID, ClientSecret and add thoses under the .env file.
- Update permissions on the script: chmod 755 generate_report.py
- Execute Script: ./generate_report.py

Sample Output:

```Python3
 % ./get_inventory.py
Successfuly obtained a new token
Creating Sheet: FI
Creating Sheet: Chassis
Creating Sheet: IOM
Creating Sheet: X-Fabric_modules
Creating Sheet: Motherboards
Creating Sheet: Blades
Creating Sheet: Racks
Creating Sheet: Psu
Creating Sheet: Fan_module
Creating Sheet: Fan
Creating Sheet: CPU
Creating Sheet: Memory
Creating Sheet: Memory_array
Creating Sheet: Network_adapter
Creating Sheet: Storage_controller
Creating Sheet: Physical_drive
Creating Sheet: Virtual_drive
Creating Sheet: Tpm
Creating Sheet: Pci_devices
Creating Sheet: Transceivers
Creating Sheet: Empty_Chassis_Slots
Creating Sheet: FI_Disk_Usage
Creating Sheet: Contracts
Creating Sheet: Licenses
Creating Sheet: ServerProfile_policies
Creating Sheet: Vnics
Creating Sheet: Vhbas
Creating Sheet: Hyperlinks
```

### Additional Info
- This script creates a single Intersight_reports.xlsx file with multiple sheets.
- Each Sheet contains data for invidividual report. 
  E.g. Sheet Names: fi, chassis, iom, etc. 
- Hyperlinks sheet includes pointers to all the sheets
