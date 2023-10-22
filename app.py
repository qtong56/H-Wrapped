from flask import Flask, render_template, request, jsonify, redirect, flash
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "secret key"

# Global variables
df = pd.DataFrame()
likematch_df = pd.DataFrame()

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

            print("File uploaded successfully.")
            return redirect('/analysis')
        except:
            flash("Error occurred while processing the request.")
            return jsonify(message="Error occurred while processing the request."), 400

    return render_template("index.html/#visualization")

@app.route("/analysis")
def analysis():
    match_data = match_stats()
    match_data = json.loads(match_data[0].data)
    return render_template("index.html/#visualization", match_data = match_data)

# Basic statistics for matches
def match_stats():
    try:
        global likematch_df
        # Count Number of Matches
        num_matches = likematch_df['type'].value_counts()['match']

        num_likes_given = likematch_df['type'].value_counts()['like']

        likes_given_of_matches = likematch_df['id'].duplicated().sum()

        likes_received_of_matches = num_matches - likes_given_of_matches

        return jsonify({"num_matches": str(num_matches),
                        "num_likes_given": str(num_likes_given),
                        "likes_given_of_matches": str(likes_given_of_matches),
                        "likes_received_of_matches": str(likes_received_of_matches)}), 200
    
    except Exception as e:
        print(e)
        return jsonify(message="Error occurred while processing the request."), 400
    



if __name__ == "__main__":
    app.run(debug=True)
