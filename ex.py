
import pandas as pd
from openpyxl.workbook import Workbook
import csv
import os 

# Read the log file into a DataFrame
a = []
log_file_path = 'log.txt'
with open(log_file_path,"rt") as st:
    a = st.readlines()
print(a)
valuess = []
for i in a:
    if "down" in i:
        valuess.append([i[4],i[20:24],i[39:47],i[48:-1]])
    if "up" in i:
        valuess.append([i[4],i[20:23],i[37:45],i[46:-1]])
    
print(valuess)

names=['ID', 'Direction', 'Time', 'Year']
with open('GFG', 'w') as f:
     
    # using csv.writer method from CSV package
    write = csv.writer(f)
     
    write.writerow(names)
    write.writerows(valuess)


os.remove('Book1.xlsx')
fp = open('Book1.xlsx', 'x')
fp.close()


read_file = pd.read_csv (r'C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\GFG')
read_file.to_excel (r'C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\Book1.xlsx', index = None, header=True)
    # Add more DataFrames to other sheets if needed\
print(r'Excel file saved at Excel File C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\Book1.xlsx') 

