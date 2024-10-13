'''
Runs all code in code folder.
'''
import os
os.chdir("C:\\Users\\isaac\\OneDrive\\Desktop\\example_codes\\Mapping\\")
# Define the directory where the Python files are located
code_directory = "C:\\Users\\isaac\\OneDrive\\Desktop\\example_codes\\Mapping\\code"

# Loop through each file in the directory
for filename in os.listdir(code_directory):
    if filename.endswith(".py"):
        file_path = os.path.join(code_directory, filename)
        
        with open(file_path, 'r') as file:
            exec(file.read())
        
        print(f"Executed {filename}")
