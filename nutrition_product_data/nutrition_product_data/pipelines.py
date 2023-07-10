# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pandas as pd
import os
import threading
import requests

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# Get the current directory path
current_directory = os.getcwd()


# Move two directories up to the grandparent directory
grandparent_directory = os.path.abspath(os.path.join(current_directory, "../../../"))

# Specify the path to the "Nutrition" directory to read the files here
nutrition_directory = os.path.join(grandparent_directory, "export.xlsx")

read_file = pd.read_excel(nutrition_directory)
class NutritionProductDataPipeline:
    def process_item(self, item, spider):
        return item



class DataCleaningPipeline:
    def process_item(self, item, spider):
        ingredients = item['ingredients']
        product_name = item['product_name']

        result_string =  self.chatgpt_cleaning_data(ingredients)
        item['ingredients'] = result_string['choices'][0]['message']['content']
        # Start a new thread to update the read_file concurrently
        thread = threading.Thread(target=self.update_read_file, args=(product_name, result_string['choices'][0]['message']['content']))
        thread.start()
        return item
    def update_read_file(self, product_name, result_string):
        matching_rows = read_file.index[read_file.eq(product_name).any(axis=1)].tolist()
        if len(matching_rows) >= 1:
            read_file.loc[matching_rows[0], 'INGREDIENTS'] = result_string

        else:
            print(product_name)
        save = threading.Thread(target=self.save_excel_file, args=(read_file,))
        save.start()
        

    def save_excel_file(self, df):
        output_path = "Output.xlsx"

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Save the modified DataFrame to the new Excel file
                df.to_excel(writer, index=False, sheet_name="My Excel")
            print("Excel file saved successfully.")
        except Exception as e:
            print("An error occurred while saving the Excel file:", e)
            print("Attempting to recover and save with modified settings...")
            try:
                with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="My Excel")
                print("Excel file saved successfully after recovery.")
            except Exception as e:
                print("Failed to save the Excel file after recovery:", e)


            
    def chatgpt_cleaning_data(self,data):
        api_endpoint = "https://api.openai.com/v1/chat/completions"
        api_key = ""  # Replace with your OpenAI API key

        request_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }

        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": 'Revise and condense the list by removing unnecessary names and metrics, and separate each item with a comma. For example, from the input "250 gi Ascorbic acid 280 mg," the desired output is "Ascorbic acid."' +data
                }
            ],
            "temperature": 1
        }
        try:
            response = requests.post(api_endpoint, headers=request_headers, json=request_data)
            response_json = response.json()
        except (requests.RequestException, ValueError, KeyError) as e:
            print("An error occurred while requesting data from OpenAI API:", e)
            return "Error "  # or any appropriate fallback value

        return response_json


     
