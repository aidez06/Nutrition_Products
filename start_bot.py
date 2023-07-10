import time
import subprocess

import os

# Start the program as a subprocess
process = subprocess.Popen(["scrapy", "crawl", "product_extract_data"], cwd=f"{os.getcwd()}/nutrition_product_data/nutrition_product_data/spiders/")

