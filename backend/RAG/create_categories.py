import os
from pathlib import Path
import numpy as np
import pandas as pd

import openai
from _key import api_key  # Your API key

output_file = "cleaned_merged_data_labeled_with_riddle_unique.csv"

# Setup openai
openai.api_type = "azure"
openai.api_base = "https://gpt-ressource.openai.azure.com/"  # Your Azure OpenAI resource URL
openai.api_version = "2024-02-01"
openai.api_key = api_key

def row_to_markdown(obj: dict) -> str: 
    s_type = obj["type"] if type(obj["type"]) == str else "unknown"
    s_title = obj["title"] if type(obj["title"]) == str else "unknown"
    s_short_description = obj["short_description"] if type(obj["short_description"]) == str else "unknown"
    s_long_description = obj["long_description"] if type(obj["long_description"]) == str else "unknown"
    s_region = obj["region"] if type(obj["region"]) == str else "unknown"
    s = "## " + s_type
    s = s + "\n\n**Title**: " + s_title
    s = s + "\n\n**Short Description**: " + s_short_description
    s = s + "\n\n**Long Description**: " + s_long_description
    s = s + "\n\n**Region**: " + s_region
    return s

try:
    data_file = os.path.join(Path(__file__).parent, "data", "cleaned_merged_data_labeled_with_riddle_unique.csv")
    df = pd.read_csv(data_file)
except:
    data_file = os.path.join(Path(__file__).parent, "data", "cleaned_merged_data_labeled.csv")
    df = pd.read_csv(data_file)
    df["riddle"] = None
    df["answer"] = None
    df["false_answers"] = None
    df["explanation"] = None
    df = df.drop_duplicates(subset='title', keep='first')

def get_prompt(info):
    return f"""
    You are a tour giude for the German state Mecklenburg Vorpommern. You are given a description of a location or an event. 
    Your task is to generate a riddle for this location or event.

    The riddle should be a little bit funny and should be easy to understand for a tourist.
    The tourist will be given a multiple choice question based on your riddle.
    Your answer should be a JSON object with the following structure:
    {{
        "riddle": "The riddle",
        "answer": "The answer",
        "false_answers": ["False answer 1", "False answer 2", "False answer 3"],
        "explanation": "The explanation for the riddle"
    }}
    return the json object as a string. Nothing else.

    Here is the description of the location or event:
    {info}
    """

def query_openai(prompt: str):
    response = openai.ChatCompletion.create(
        engine="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt,  # Your question
            },
        ],
    )
    return response['choices'][0]['message']['content']

# Configure the client for Azure OpenAI usage
for index, row in df.iterrows():
    if not pd.isna(row["riddle"]):
        continue
    try:
        info = row_to_markdown(row)
        prompt = get_prompt(info)
        response = query_openai(prompt)
        response = eval(response.replace("```json", "").replace("```", ""))
        df.loc[index, "riddle"] = response["riddle"]
        df.loc[index, "answer"] = response["answer"]
        df.loc[index, "false_answers"] = np.array(response["false_answers"]).__str__()
        df.loc[index, "explanation"] = response["explanation"]
        print(row.to_json())
        print(df.loc[index, ["riddle", "answer", "false_answers", "explanation"]])
    except Exception as e:
        print(f"Error at index {index}: {e}")
    print(f"Processed {index + 1} of {df.index.size}")
    if index % 10 == 0:
        df.to_csv(os.path.join(Path(__file__).parent, "data", output_file), index=False)

df.to_csv(os.path.join(Path(__file__).parent, "data", output_file), index=False)

print("done")
