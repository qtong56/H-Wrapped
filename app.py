from flask import Flask, render_template, request, jsonify, redirect, flash
import pandas as pd
import json
import requests
import numpy as np
from collections import Counter
import secrets
import torch
from transformers import pipeline

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global variables
df = pd.DataFrame()
likematch_df = pd.DataFrame()
unprocessed_df_info = pd.DataFrame()

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def file_input():
    if request.method == "POST":
        file = request.files["file"]

        # Check if a file was selected
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        # Move data into dataframe for analysis
        try:
            data_dict = {
                "filename": file.filename,
                "content_type": file.content_type,
                "data": json.load(file),
            }

            global df, likematch_df
            
            # Extract 'chats' data
            chats_data = []
            for item in data_dict["data"]:
                if "chats" in item:
                    chats_data.extend(item["chats"])

            # Extra likes and matches data
            likematch_data = []
            id = 0
            for item in data_dict['data']:
                if 'like' in item and 'match' in item:
                    likematch_data.extend(item['like'])
                    likematch_data.extend(item['match'])
                    likematch_data[id]["id"] = id
                    likematch_data[id + 1]["id"] = id
                    id += 2

                if 'like' in item and 'match' not in item:
                    likematch_data.extend(item['like'])
                    likematch_data[id]["id"] = id
                    id += 1
                if 'match' in item and 'like' not in item:
                    likematch_data.extend(item['match'])
                    likematch_data[id]["id"] = id
                    id += 1

            # Create DataFrame from extracted chat data
            df = pd.DataFrame(chats_data)

            # Create DataFrame from extracted likes and match data
            likematch_df = pd.DataFrame(likematch_data)

            # Select desired columns
            df = df[['body', 'timestamp']]

            # Fix timezones for DataFrames
            TimeZone = "US/Eastern"
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(TimeZone)
            df['body'] = df['body'].astype(str)

            # Convert timestamps to datetime objects and format them
            # causes issues sometimes
            likematch_df['timestamp'] = likematch_df['timestamp'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m-%dT%H:%M:%S'))

            # Localize timestamps to US/Eastern timezone
            likematch_df['timestamp'] = pd.to_datetime(likematch_df['timestamp']).dt.tz_localize(TimeZone)

            # Convert type column to string
            likematch_df['type'] = likematch_df['type'].astype(str)

            # Convert comment column to string
            likematch_df['comment'] = likematch_df['comment'].astype(str)

            # Limit both dataframes to timestamps in 2022
            df = df[df['timestamp'].dt.year == 2022]
            likematch_df = likematch_df[likematch_df['timestamp'].dt.year == 2022]

            print("File uploaded successfully.")
            return redirect("/analysis")
        except:
            flash("Error occurred while processing the request.")
            return jsonify(message="Error occurred while processing the request."), 400

    return render_template("index.html")

@app.route("/analysis")
def analysis():
    try:
        final_data = match_stats()
        message_data = message_stats()
        profanity_data = profanity_stats()
        emotion_data = emotions()

        # Combine the two dictionaries
        final_data.update(message_data)
        final_data.update(profanity_data)
        final_data.update(emotion_data)

        return jsonify(final_data), 200
    except:
        return jsonify(message="Error occurred while processing the request."), 400


# Basic statistics for matches
def match_stats():
    try:
        global likematch_df
        # Count Number of Matches
        num_matches = likematch_df['type'].value_counts()['match']

        num_likes_given = likematch_df['type'].value_counts()['like']

        likes_given_of_matches = likematch_df['id'].duplicated().sum()

        likes_received_of_matches = num_matches - likes_given_of_matches

        return {"num_matches": str(num_matches),
                    "num_likes_given": str(num_likes_given),
                    "likes_given_of_matches": str(likes_given_of_matches),
                    "likes_received_of_matches": str(likes_received_of_matches)}

    except Exception as e:
        print(e)
        return jsonify(message="Error with match_stats portion of the request."), 400
    
# Statistics for messages
def message_stats():
    global df, unprocessed_df_info

    unprocessed_df_info = pd.DataFrame({
        'Timestamp': df['timestamp'],
        'BodyLength': df['body'].str.len()
    })

    # Replace any NaN values with 0
    unprocessed_df_info.fillna(0, inplace=True)

    # Aggregate by month
    unprocessed_df_info['Timestamp'] = pd.to_datetime(unprocessed_df_info['Timestamp'])
    monthly_message_lengths = unprocessed_df_info.set_index('Timestamp').resample('M').count()
    
    # Messages sent over time
    total_messages_sent = len(unprocessed_df_info.index)
    total_characters_sent = int(unprocessed_df_info["BodyLength"].sum())
    avg_char_per_message = total_characters_sent // total_messages_sent

    # Find the weekday with the most messages sent
    weekday_with_most_messages = unprocessed_df_info['Timestamp'].dt.day_name().value_counts().idxmax()

    # convert to json
    message_lengths = monthly_message_lengths.reset_index().to_json(orient='records', date_format='iso')

    # Hour of day with longest messages sent
    hour_vs_message_length = {h + 1: unprocessed_df_info[unprocessed_df_info['Timestamp'].dt.hour == h]['BodyLength'].value_counts() for h in range(0, 24)}
    hour_vs_message_length = pd.DataFrame(hour_vs_message_length)

    # Find the hour with the longest messages on average
    hour_with_longest_messages = hour_vs_message_length.mean().idxmax()

    # Format the hour with the longest messages on average
    hour_with_longest_messages_formatted = pd.to_datetime(hour_with_longest_messages, format='%H').strftime('%I:%M %p')
    
    # Find the top 10 most used words
    top5_words = Counter(" ".join(df["body"]).split()).most_common(5)
    top5_words_keys = [word for word, count in top5_words]

    return {"total_messages_sent": str(total_messages_sent),
            "total_characters_sent": str(total_characters_sent),
            "avg_char_per_message": str(avg_char_per_message),
            "monthly_message_lengths": message_lengths,
            "most_freq_weekday": weekday_with_most_messages,
            "most_freq_hour": hour_with_longest_messages_formatted,
            "top5_words": str(top5_words_keys)}

# Statistics for profanity
def profanity_stats():
    global df
    
    PROFANE_WORDS_URL = "https://raw.githubusercontent.com/zacanger/profane-words/master/words.json"

    profane_words = requests.get(PROFANE_WORDS_URL).json()
    profane_words_regex = f'(?<![a-zA-Z0-9])({"|".join(profane_words)})(?![a-zA-Z0-9])'

    profane_words_matches = df['body'].str.extract(profane_words_regex)
    profane_words_matches = profane_words_matches[profane_words_matches.values != np.NaN].value_counts()

    top5_profanities = [swear[0] for swear in profane_words_matches.head(5).index.tolist()]

    return {"profanities": top5_profanities}

# Emotional analysis
def emotions():
    try:
        global df
        emotion = pipeline('sentiment-analysis', model='bhadresh-savani/bert-base-go-emotion', device=0)
        tokenizer_kwargs = {'padding':True,'truncation':True,'max_length':512 // 4}

        emotion_labels = emotion(df['body'].to_list(), **tokenizer_kwargs)
        df['Emotion'] = [v.get('label') for v in emotion_labels]
        emotion_messages = df['Emotion'][df['Emotion'] != 'neutral']
        data = emotion_messages.value_counts()
        data = data / data.sum()
        
        return {"emotion_spectrum": data.to_dict()}
    except Exception as e:
        print(e)
        return jsonify(message="Error with emotions portion of the request."), 400

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
