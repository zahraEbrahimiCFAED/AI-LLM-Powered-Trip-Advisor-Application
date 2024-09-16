import pandas as pd
import os
from pathlib import Path
import numpy as np

data_folder = os.path.join(Path(__file__).parent, "data")
df_labeled = pd.read_csv(os.path.join(data_folder, "cleaned_merged_data_labeled.csv"))
df_riddle_unique = pd.read_csv(os.path.join(data_folder, "cleaned_merged_data_labeled_with_riddle_unique.csv"))

# df_riddle_unique = df_riddle_unique.loc[np.logical_not(df_riddle_unique["riddle"].isna())]

for index, row in df_riddle_unique.iterrows():
    tf = df_labeled["title"] == row["title"]
    print(index, tf.sum())
    df_labeled.loc[tf, "riddle"] = row["riddle"]
    df_labeled.loc[tf, "answer"] = row["answer"]
    df_labeled.loc[tf, "false_answers"] = row["false_answers"].replace("' '", "','") if not pd.isna(row["false_answers"]) else None
    df_labeled.loc[tf, "explanation"] = row["explanation"]

df_labeled.to_csv(os.path.join(data_folder, "merged_data.csv"), index=False)