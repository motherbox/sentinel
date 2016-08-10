import json
import pandas as pd
import re


def json2df(fname, year):
    with open(fname, "r") as f_in:
        orgData = json.load(f_in)
    cleanTitles = {}
    pattern = "[0-9]+\."
    for k, v in orgData.iteritems():
        title = re.sub(pattern, "", k.lstrip().rstrip())
        cleanTitles[title.lstrip().rstrip()] = v
    df = pd.DataFrame(index=cleanTitles.keys())
    for key in v.keys():
        df[key] = ""
    for ix, rowData in df.iterrows():
        propData = cleanTitles[ix]
        for k, v in propData.iteritems():
            if k != "comments":
                rowData.loc[k] = v
    df.columns = [c.lower().replace(" ", "_").replace(":", "") for c in df]
    df['n_comments'] = df.pop('comments')
    for ix, rowdata in df.iterrows():
        rowdata.loc["n_comments"] = len(cleanTitles[ix]['comments'])
    df['year'] = year
    return df

if __name__ == '__main__':
    df1 = json2df("cfp2015.json", 2015)
    df2 = json2df("cfp2016.json", 2016)
    df = pd.concat((df1, df2), axis=0)
    df.to_csv("cfp.tsv", encoding="utf-8", sep="\t", index_label="title")
