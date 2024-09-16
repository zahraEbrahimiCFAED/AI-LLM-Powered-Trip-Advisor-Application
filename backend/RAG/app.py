from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from util import parse_df_to_json, filter_data
import os
from pathlib import Path
import numpy as np

data_file = os.path.join(Path(__file__).parent, "data", "merged_data.csv")

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

df = pd.read_csv(data_file)
df = df.loc[np.logical_not(df["riddle"].isna())] # only the rows with a riddle
df = df.replace({np.nan: None})
df["coordinates"] = df["coordinates"].apply(lambda x: eval(x))
# df_filtered = filter_data(df, settings, 10)

# API endpoint to handle POST requests
@app.route('/filter', methods=['POST'])
def filter_data_endpoint():
    try:
        # Get the JSON from the POST request
        criteria = request.json

        # # Filter the DataFrame using the criteria
        df_filtered = filter_data(df, criteria, 10)
        
        # # Convert the filtered DataFrame to JSON
        # result = filtered_df.to_dict(orient='records')
        
        data = parse_df_to_json(df_filtered.sample(1))[0]
        msg_dict = {
            "index": data["index"],
            "title": data["title"],
            "location_website": data["location_website"],
            "region": data["region"],
            "start_time": data["start_time"],
            "duration": data["duration"],
            "short_description": data["short_description"],
            "long_description": data["long_description"],
            "riddle": data["riddle"],
            "answer": data["answer"],
            "false_answers": data["false_answers"],
            "explanation": data["explanation"],
            "distance": data["distance"],
            "coordinates": data["coordinates"]
        }
        print(msg_dict)
        return jsonify(msg_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
