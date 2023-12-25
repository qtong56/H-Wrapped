# @title Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import torch;
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("Torch version:",torch.__version__)
assert(device.type == 'cuda')

plt.style.use('ggplot')

# @title Load Data
# Load JSON data from file
with open('./test/matches.json', 'r') as f:
    data = json.load(f)

# Extract 'chats' data
chats_data = []
for item in data:
    if 'chats' in item:
        chats_data.extend(item['chats'])

# Create DataFrame from extracted chat data
df = pd.DataFrame(chats_data)

# Select desired columns
df = df[['body', 'timestamp']]

TimeZone = "US/Eastern" #@param {type:"string"}
date = pd.Timestamp.now(tz=TimeZone)
print("See if your timezone is correct: ", date)

# Fix timezones for DataFrames
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(TimeZone)
df['body'] = df['body'].astype(str)

# For simplifying purposes, shorten to first 500 texts
df = df.head(500)

# Reset index
df.reset_index().rename(columns={'index' : 'index'})

# @title GoEmotions Pipeline
from transformers import pipeline

emotion = pipeline('sentiment-analysis', model='bhadresh-savani/bert-base-go-emotion', device=0)
tokenizer_kwargs = {'padding':True,'truncation':True,'max_length':512 // 4}

emotion_labels = emotion(df['body'].to_list(), **tokenizer_kwargs)
df['Emotion'] = [v.get('label') for v in emotion_labels]

# @title Overall Emotion Profile
emotion_messages = df['Emotion'][df['Emotion'] != 'neutral']
data = emotion_messages.value_counts()
data = data / data.sum()

print(data.to_dict().keys())

ax = sns.barplot(x=data, y=data.index)
ax.set(xlabel='Emotion Frequency', title='Emotion Spectrum Profile')
