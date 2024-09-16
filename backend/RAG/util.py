from typing import Tuple, List
import pandas as pd

SPEED = 20
CURRENT_LOCATION = tuple([54.485116, 13.505989])

def get_time_between_locations(current_location: Tuple, target_location: Tuple) -> float:
    """Calculate distance in km between the two locations and estimate a time based on an average speed"""
    from haversine import haversine, Unit
    from ast import literal_eval
    return haversine(current_location, target_location, unit=Unit.KILOMETERS) / SPEED * 60

def load_json_as_dict(path: str): 
    with open(path, 'r') as file:
        config = file.read()
    config = config.replace('false', 'False').replace('true', 'True').replace('null', 'None')
    return eval(config)

def save_as_json(config: dict, path: str, pretty: bool=True, mode: str='w', newline: bool=False):
    import json
    if pretty:        
        output = json.dumps(config, 
                            sort_keys=False, 
                            indent=2, 
                            separators=(',', ': '))
    else:
        output = json.dumps(config)
    if newline: output = output + '\n' 
    
    with open(path, mode) as file:     
        file.write(output)

def parse_df_to_json(df, type: str=None):
    data = []
    for index, row in df.iterrows():
        obj = {
            "index": index
        }
        if type is not None:
            obj.update({
                "type": type
            })
        obj.update({
            col: row[col] for col in df.columns
        })
        data.append(obj)
    return data

def dict_to_markdown(obj: dict) -> str: 
    s = "## " + obj["type"]
    for k, v in obj.items():
        if k == "type": continue
        s = s + "\n\n**" + k + "**: " + str(v).replace("\"", "'")
    return s

def replace_double_newlines(s: str) -> str:
    if "\n\n" in s:
        return replace_double_newlines(s.replace("\n\n", "\n"))
    else:
        return s

def printmd(s: str) -> None:
    from IPython.display import Markdown, display
    display(Markdown(s))

def clean_and_merge_data(data_folder: str):
    import os
    df_events = pd.read_csv(os.path.join(data_folder, "events.csv"))
    df_events["coordinates"] = df_events["location_coordinates"].apply(lambda v: tuple(float(s) for s in v.split(",")))
    df_events.drop(columns=["location_coordinates"], inplace=True)
    df_events["address"] = df_events.apply(lambda r: r["location_title"] + ", " + r["location_street"] + ", " + r["location_postal_code"] + " " + r["location_city"], axis=1)
    df_events.drop(columns=["location_title", "location_street", "location_postal_code", "location_city"], inplace=True)
    df_events["short_description"] = df_events["short_description"].apply(lambda s: replace_double_newlines(s))
    df_events["long_description"] = df_events["long_description"].apply(lambda s: replace_double_newlines(s))
    df_events["type"] = "event"

    df_locations = pd.read_csv(os.path.join(data_folder, "locations.csv"))
    df_locations["coordinates"] = df_locations.apply(lambda s: (float(s["long"].replace(",", ".")), float(s["lat"].replace(",", "."))), axis=1)
    df_locations.drop(columns=["long", "lat"], inplace=True)
    df_locations["address"] = df_locations.apply(lambda r: str(r["company"]) + ", " + str(r["street"]) + str(r["house_number"]) + ", " + str(r["postal_code"]) + " " + str(r["city"]), axis=1)
    df_locations.drop(columns=["company", "street", "house_number", "postal_code", "city"], inplace=True)
    df_locations["short_description"] = df_locations["short_description"].apply(lambda s: replace_double_newlines(s))
    df_locations["long_description"] = df_locations["long_description"].apply(lambda s: replace_double_newlines(s))
    df_locations["type"] = "location"

    df_events.rename(columns={"location_region": "region"}, inplace=True)
    df = pd.concat([df_events, df_locations])
    df = df.loc[df["coordinates"] != (0.0, 0.0)].reset_index(drop=True)
    
    return df

def get_closest_points(number: int, data: pd.DataFrame, position: Tuple):
    '''Add a column with the distance to the current location and filter the by the n lowest values'''
    data["distance"] = data["coordinates"].apply(lambda x: get_time_between_locations(current_location=position, target_location=x))
    closest_pois = data.nsmallest(number, "distance")
    return closest_pois

def filter_data(data: pd.DataFrame, filters: dict, max_number_of_pois: int = 10) -> pd.DataFrame:
    '''Filter the dataset based on user criteria'''
    from datetime import datetime as dt

    data["start_time"] = pd.to_datetime(data["start_time"], format='mixed', errors="coerce")
    # now = pd.to_datetime("now")
    now = dt.strptime(filters["date"]["from"][0:-5], "%Y-%m-%dT%H:%M:%S")
    end_time = now + pd.Timedelta("1 day")

    # Create a boolean mask for each filter condition
    mask = (
        ((data["restaurant_label"] == "ja") & ("restaurant" in filters["pointsOfInterest"])) |
        ((data["historic_sight_label"] == "ja") & ("historic_sight" in filters["pointsOfInterest"])) |
        ((data["museum_label"] == "ja") & ("museum" in filters["pointsOfInterest"])) |
        ((data["shopping_label"] == "ja") & ("shopping" in filters["pointsOfInterest"])) |
        ((data["nature_label"] == "ja") & ("nature" in filters["pointsOfInterest"])) |
        ((data["entertainment_label"] == "ja") & ("entertainment" in filters["pointsOfInterest"])) |
        ((data["indoor_label"] == "ja") & ("indoor" in filters["pointsOfInterest"]))
    )

    # Filter rows where at least one condition matches
    data = data[mask]

    tf_start = data["start_time"] >= now
    if tf_start.sum() >= max_number_of_pois:
        data = data.loc[tf_start]
    tf_end = data["start_time"] < end_time
    if tf_end.sum() >= max_number_of_pois:
        data = data.loc[tf_end] 

    current_location = (filters["location"]["coords"]["latitude"], filters["location"]["coords"]["longitude"])
    if len(data) < max_number_of_pois:
        max_number_of_pois = len(data)
    data = get_closest_points(number=max_number_of_pois, data=data, position=current_location)

    return data

def add_categories_and_riddles(input_csv_file: str, output_csv_file: str):
    import csv

    # Function to determine the category of the text and provide riddles
    def check_category(text, keywords, riddles):
        if text is None or text == '':
            return 'nein', '', ''
        text = text.lower()
        for keyword in keywords:
            if keyword in text:
                return 'ja', riddles[keyword], keyword  # Return 'ja', the riddle, and the keyword as the answer
        return 'nein', '', ''

    # Keywords and their corresponding riddles
    categories = {
        'restaurant': {
            'keywords': ['essen', 'restaurant', 'café', 'bistro', 'gasthaus', 'taverne', 'mahlzeit', 'gericht', 'speise', 'küche', 'nahrung', 'einkaufen', 'kochen', 'koch', 'küchenchef', 'kochkunst', 'rezept', 'speisekarte', 'gastronomie'],
            'riddles': {
                'essen': "I am a necessity for life and often enjoyed three times a day. What am I?",
                'restaurant': "A place where you go to enjoy a meal without cooking. What is it called?",
                'café': "I am a cozy spot for coffee and pastries. What is this place called?",
                'bistro': "A small and informal place to get a quick meal, often with a French touch. What is it?",
                'gasthaus': "A place where you can stay overnight and enjoy a home-cooked meal. What is it?",
                'taverne': "An old-fashioned place to drink and eat, often found in historical settings. What is it?",
                'mahlzeit': "This word describes the time or act of eating a meal. What is it?",
                'gericht': "A single item of food served on a plate is called what?",
                'speise': "Another word for a dish or food served at a meal. What is it?",
                'küche': "The room where meals are prepared and cooked is called what?",
                'nahrung': "The term for everything you consume to sustain life and health. What is it?",
                'einkaufen': "The act of buying food or other items. What is it called?",
                'kochen': "The process of preparing food by heating it. What is it called?",
                'koch': "The person who prepares and cooks meals professionally is called what?",
                'küchenchef': "The head of the kitchen in a restaurant, responsible for creating the menu. What is this role?",
                'kochkunst': "The art of preparing and presenting food beautifully. What is this called?",
                'rezept': "The instructions to make a dish or meal are known as what?",
                'speisekarte': "The list of food options available at a restaurant is called what?",
                'gastronomie': "The study or practice of cooking and eating good food is known as what?"
            }
        },
        'historic_sight': {
            'keywords': ['historisch', 'sehenswürdigkeit', 'denkmal', 'historische stätte', 'ruine', 'schloss', 'burg', 'kulturdenkmal', 'architektur', 'gedenkstätte', 'historisches gebäude', 'historisches zentrum', 'altstadt', 'erinnerungsstätte', 'glockenturm', 'festung'],
            'riddles': {
                'historisch': "Describing something from the past that has historical significance. What is this word?",
                'sehenswürdigkeit': "A place or object of interest for visitors, often with historical or cultural value. What is it?",
                'denkmal': "A structure built to commemorate a person or event. What is this called?",
                'historische stätte': "A location with significant historical importance. What is this called?",
                'ruine': "The remains of a building that has fallen into disrepair. What is this called?",
                'schloss': "A large, historic residence often surrounded by gardens. What is this called?",
                'burg': "A fortified building or castle from the medieval period. What is it?",
                'kulturdenkmal': "A site or building that is protected due to its cultural and historical importance. What is it?",
                'architektur': "The art and science of designing and constructing buildings. What is this called?",
                'gedenkstätte': "A place set up to remember or honor a significant person or event. What is this called?",
                'historisches gebäude': "A building that has historical value due to its age or past significance. What is it?",
                'historisches zentrum': "The central area of a city known for its historical buildings and importance. What is this called?",
                'altstadt': "The older part of a city, often with historic buildings and streets. What is this called?",
                'erinnerungsstätte': "A place dedicated to preserving memories of significant events or people. What is this called?",
                'glockenturm': "A tower built to house and ring bells, often found in old churches. What is it?",
                'festung': "A fortified place built for defense and protection, often historic. What is this?"
            }
        },
        'museum': {
            'keywords': ['museum', 'kunstausstellung', 'ausstellung', 'galerie', 'kunstgalerie', 'historisches museum', 'kunstmuseum', 'naturkundemuseum', 'wissenschaftsmuseum'],
            'riddles': {
                'museum': "A building where artifacts and artworks are displayed for public education. What is this called?",
                'kunstausstellung': "A public display of works of art. What is this called?",
                'ausstellung': "An event where objects are displayed to the public, often in a museum. What is this?",
                'galerie': "A room or building where art is exhibited. What is this called?",
                'kunstgalerie': "A gallery specializing in the exhibition of artworks. What is it?",
                'historisches museum': "A museum dedicated to preserving and displaying artifacts from the past. What is it called?",
                'kunstmuseum': "A museum that focuses on visual arts. What is it?",
                'naturkundemuseum': "A museum focused on natural history. What is it?",
                'wissenschaftsmuseum': "A museum focused on science and technology. What is it?"
            }
        },
        'shopping': {
            'keywords': ['einkaufszentrum', 'geschäft', 'supermarkt', 'kaufhaus', 'markt', 'laden', 'shopping', 'boutique', 'einkaufen'],
            'riddles': {
                'einkaufszentrum': "A large building with many stores and sometimes restaurants. What is this called?",
                'geschäft': "A place where goods are sold to customers. What is this called?",
                'supermarkt': "A large store that sells food and household goods. What is it called?",
                'kaufhaus': "A large store with different sections selling a wide range of goods. What is it?",
                'markt': "A place where vendors sell goods, often outdoors. What is it?",
                'laden': "A small shop where goods are sold. What is this called?",
                'shopping': "The act of visiting stores to buy goods. What is this called?",
                'boutique': "A small shop that sells fashionable clothes or accessories. What is this called?",
                'einkaufen': "The activity of purchasing goods from stores. What is it called?"
            }
        },
        'nature': {
            'keywords': ['park', 'wald', 'fluss', 'strand', 'garten', 'wildnis', 'pfad', 'naturschutzgebiet', 'hügel', 'talsperre', 'naturlandschaft'],
            'riddles': {
                'park': "A large public green area in a town, used for recreation. What is this called?",
                'wald': "A large area covered chiefly with trees and undergrowth. What is this called?",
                'fluss': "A natural stream of water flowing towards an ocean, sea, or lake. What is this called?",
                'strand': "The shore of a body of water, especially when sandy. What is this called?",
                'garten': "An area of ground where plants such as flowers or vegetables are grown. What is this called?",
                'wildnis': "An unspoiled, uncultivated area of land. What is this called?",
                'pfad': "A narrow track or path, often in a natural setting. What is this called?",
                'naturschutzgebiet': "A protected area established to preserve natural habitats and wildlife. What is this called?",
                'hügel': "A small hill or mound of earth. What is this called?",
                'talsperre': "A dam built to create a reservoir or control water flow. What is this called?",
                'naturlandschaft': "An area of land with natural features, untouched by human development. What is this called?"
            }
        },
        'entertainment': {
            'keywords': ['kino', 'theater', 'konzert', 'veranstaltung', 'zirkus', 'show', 'film', 'musik', 'bühne', 'aufführung', 'event', 'performance'],
            'riddles': {
                'kino': "A place where films are shown. What is this called?",
                'theater': "A building where plays and performances are shown live. What is this called?",
                'konzert': "A live music performance in front of an audience. What is this called?",
                'veranstaltung': "An organized public or social occasion. What is this called?",
                'zirkus': "A traveling show with clowns, acrobats, and animals. What is this called?",
                'show': "A performance or event for entertainment. What is it?",
                'film': "A movie or motion picture. What is this called?",
                'musik': "An art form that uses sound and rhythm to produce melodies and harmonies. What is this?",
                'bühne': "The platform or area where performances take place. What is this called?",
                'aufführung': "The presentation of a play, concert, or other performance. What is it?",
                'event': "A planned public or social gathering for entertainment. What is this called?",
                'performance': "An act of presenting a form of entertainment to an audience. What is it?"
            }
        },
        'indoor': {
            'keywords': ['kino', 'museum', 'theater', 'bibliothek', 'schwimmbad', 'bowling', 'kletterhalle', 'fitnessstudio', 'spielhalle'],
            'riddles': {
                'kino': "A place where films are shown. What is this called?",
                'museum': "A building where artifacts and artworks are displayed for public education. What is this called?",
                'theater': "A building where plays and performances are shown live. What is this called?",
                'bibliothek': "A place where books are stored and borrowed. What is it called?",
                'schwimmbad': "A large area filled with water, often indoors, where people can swim. What is it called?",
                'bowling': "A game where players roll a heavy ball to knock down pins. What is it called?",
                'kletterhalle': "A gym where you can practice rock climbing indoors. What is it called?",
                'fitnessstudio': "A place with equipment for physical exercise. What is this called?",
                'spielhalle': "An entertainment venue with arcade games and other amusements. What is it called?"
            }
        }
    }

    # Open the input CSV file and read the data
    with open(input_csv_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames  # Read header
        rows = [row for row in reader]  # Read all rows

    # Create new headers for added columns
    new_headers = [
        'restaurant_label', 'restaurant_riddle', 'restaurant_answer',
        'historic_sight_label', 'historic_sight_riddle', 'historic_sight_answer',
        'museum_label', 'museum_riddle', 'museum_answer',
        'shopping_label', 'shopping_riddle', 'shopping_answer',
        'nature_label', 'nature_riddle', 'nature_answer',
        'entertainment_label', 'entertainment_riddle', 'entertainment_answer',
        'indoor_label', 'indoor_riddle', 'indoor_answer'
    ]

    header.extend(new_headers)

    # Process each row and add the label, riddle, and answer columns
    new_rows = []
    for row in rows:
        new_row = row.copy()
        short_description = row.get('short_description', '')
        long_description = row.get('long_description', '')

        for category, info in categories.items():
            text = f"{short_description} {long_description}"
            label, riddle, answer = check_category(text, info['keywords'], info['riddles'])
            new_row[f'{category}_label'] = label
            new_row[f'{category}_riddle'] = riddle if label == 'ja' else ''
            new_row[f'{category}_answer'] = answer if label == 'ja' else ''

        new_rows.append(new_row)

    # Write the updated data to a new CSV file
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()  # Write header
        writer.writerows(new_rows)  # Write rows
