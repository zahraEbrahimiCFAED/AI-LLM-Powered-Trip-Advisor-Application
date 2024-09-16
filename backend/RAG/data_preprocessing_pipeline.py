from util import clean_and_merge_data, add_categories_and_riddles
import os
from pathlib import Path

## 1. JOIN CSV FILES
# Clean and merge data
data_folder = os.path.join(Path(__file__).parent, "data")
df = clean_and_merge_data(data_folder)

# Save to CSV
df.to_csv(os.path.join(data_folder, "cleaned_merged_data.csv"), index=False)

## 2. ADD CATEGORIES AND RIDDLES
add_categories_and_riddles(
    os.path.join(data_folder, "cleaned_merged_data.csv"), 
    os.path.join(data_folder, "cleaned_merged_data_labeled.csv")
)
