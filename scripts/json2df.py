# coding: utf-8
import json
import re
import pandas as pd

with open("mehrab.json", "r") as fin:
    rawData = json.load(fin)

titles = rawData.keys()
pattern = "^[0-9]+\.\ "
regex = re.compile(pattern, re.IGNORECASE)
for title in titles:
    v = rawData.pop(title)
    clean_title = title.lstrip().rstrip()
    rawData[re.sub(regex, "", title)] = v

df = pd.DataFrame.from_records(rawData)
df = pd.DataFrame(index=df.T.index, columns=df.T.columns)
df.fillna(value="", inplace=True)

for title, rowData in df.iterrows():
    df.loc[title] = pd.Series(rawData[title])

df.to_csv("tabularcfp.tsv", sep="\t", index_label="title", encoding="utf8")
