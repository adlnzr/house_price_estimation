pip install python-bidi
pip install arabic-reshaper

import pandas as pd
import re
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
import arabic_reshaper

df = pd.read_csv('Post-2023-11-17.csv')

def extract_non_null_values(df):
    non_null_values = {}
    for column in df.columns:
        non_null_values[column] = df[column].dropna().values
    return non_null_values

def extract_persian_words(text):
    persian_words = re.findall(r'[\u0600-\u06FF\s]+', text)
    return persian_words

def generate_word_cloud(word_counts):
    reshaped_text = arabic_reshaper.reshape(' '.join(word_counts.keys()))
    persian_text = get_display(reshaped_text)

    wordcloud = WordCloud(font_path='/content/Mj_Farsi Simple Normal_0.ttf', background_color='white',
                          width=800, height=400, regexp=r"[\u0600-\u06FF]+").generate_from_frequencies(word_counts)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def process_description(df):
    df_description = df['description']
    df_description_dist = df_description.str.split('|', expand=True)
    df_description_dist = df_description_dist[[0, 3]]

    series = df_description_dist[0].str.replace(r'[\d*]+', '', regex=True)
    series1 = series.str.split(',', expand=True)[0]
    series2 = series1.str.split('_', expand=True)
    series20 = series2[0].str.split(' ', expand=True)
    series21 = series2[1].str.split(' ', expand=True)
    series22 = series2[2].str.split(' ', expand=True)
    series23 = series2[3].str.split(' ', expand=True)
    series24 = series2[4].str.split(' ', expand=True)

    series20_dict = extract_non_null_values(series20)
    series21_dict = extract_non_null_values(series21)
    series22_dict = extract_non_null_values(series22)
    series23_dict = extract_non_null_values(series23)
    series24_dict = extract_non_null_values(series24)

    list_series20 = [series20_dict.get(i).tolist() for i in range(len(series20_dict.values()))]
    list_series21 = [series21_dict.get(i).tolist() for i in range(len(series21_dict.values()))]
    list_series22 = [series22_dict.get(i).tolist() for i in range(len(series22_dict.values()))]
    list_series23 = [series23_dict.get(i).tolist() for i in range(len(series23_dict.values()))]
    list_series24 = [series24_dict.get(i).tolist() for i in range(len(series24_dict.values()))]

    flattened_list_series20 = [item for sublist in list_series20 for item in sublist]
    flattened_list_series21 = [item for sublist in list_series21 for item in sublist]
    flattened_list_series22 = [item for sublist in list_series22 for item in sublist]
    flattened_list_series23 = [item for sublist in list_series23 for item in sublist]
    flattened_list_series24 = [item for sublist in list_series24 for item in sublist]

    list_series2 = [flattened_list_series20, flattened_list_series21, flattened_list_series22,
                    flattened_list_series23, flattened_list_series24]
    series0 = [item for sublist in list_series2 for item in sublist]

    series3 = df_description_dist[3].str.replace(r'[\d*]+', '', regex=True)
    series3 = series3.str.split(',', expand=True)[0]
    series3 = series3.str.replace(r'[\d*]+', '', regex=True)
    pattern = r'[\u0600-\u06FF\s]+'
    persian_words = series3.str.findall(pattern)
    persian_words_list = persian_words.apply(lambda x: extract_persian_words(str(x)))
    persian_words_list1 = persian_words_list.apply(lambda x: extract_persian_words(str(x)))
    ser = pd.Series(persian_words_list1)
    ser = ser.replace(' ', pd.NA)
    ser = ser.dropna()
    ser3 = [item for sublist in ser for item in sublist]
    series_ser3 = pd.Series(ser3)
    return series_ser3

def process_title(df):
    df['Contains_teras'] = df['title'].str.contains('تراس|بالکن', regex=True)
    df['Contains_komod'] = df['title'].str.contains('کمد')
    df['Contains_master'] = df['title'].str.contains('مستر')

    return df















