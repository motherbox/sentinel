""".."""

from bs4 import BeautifulSoup as Bs
import requests
import traceback
import json
import re
import pandas as pd
import numpy as np


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
    df['n_comments'] = df['n_comments'].astype(int)
    df['n_votes'] = df['n_votes'].astype(int)
    df['year'] = year
    for col in df:
        if df[col].dtype is np.dtype('O'):
            df[col] = df.pop(col).apply(lambda x: x.lstrip().rstrip())
    return df


class Scrape:
    """.."""

    def __init__(self, proposal_url):
        """Intializing varibales."""
        self.proposal_url = proposal_url
        self.base_url = 'https://in.pycon.org'
        self.result = {}
        self.headers = {}

    def make_request(self, url):
        """Making request to get html page of given url.

        :params url
        Return
            BeautifulSoup object or None
        """
        try:
            self.headers['User-Agent'] = ("Mozilla/5.0 (Macintosh; Intel Mac"
                                          " OS X 10_11_5) AppleWebKit/537.36"
                                          "(KHTML, like Gecko) Chrome/51.0."
                                          "2704.103 Safari/537.36")
            r = requests.get(url, headers=self.headers)
            if r.ok:
                return Bs(r.text)
        except:
            print traceback.format_exc()
        return None

    def start(self):
        """Call to start scraping in.pycon.org proposals.

        Return
            dict of proposals.
        """
        soup = self.make_request(self.proposal_url)
        if not soup:
            return
        soup_proposals = soup.findAll(
            'div', attrs={'class': 'row user-proposals'})
        for proposal in soup_proposals:
            p = proposal.find('h3', attrs={'class': 'proposal--title'})
            title, url = p.text, "".join([self.base_url,
                                          p.find('a').get('href', '')])
            soup = self.make_request(url)
            if not soup:
                continue
            soup_proposal = soup.findAll(
                'div', attrs={'class': 'proposal-writeup--section'})
            temp = {}
            for data in soup_proposal:
                try:
                    temp[data.find('h4').text] = "".join(
                        [ptag.text for ptag in data.findAll('p')])
                except:
                    print traceback.format_exc()
            temp['comments'] = []
            for comment in soup.findAll("div", attrs={'class': 'comment-description'}):
                text = comment.find("span")
                if text:
                    temp['comments'].append(dict(
                        text=text.text.strip(),
                        by=comment.find('b').text.strip(),
                        time=comment.find('small').text.strip()))
            talk_details = soup.findAll('tr')
            for section in talk_details:
                row = section.findAll('td')
                temp[row[0].text] = row[1].text
            try:
                vCount = soup.findAll('h1', attrs={'class': 'vote-count'})[0]
                temp["n_votes"] = int(vCount.text.lstrip().rstrip())
            except IndexError:
                from IPython.core.debugger import Tracer
                Tracer()()
            self.result[title] = temp

        # from pprint import pprint
        # # Printing data
        # pprint(self.result)
        return self.result

if __name__ == '__main__':
    cfp_2015_url = "https://in.pycon.org/cfp/pycon-india-2015/proposals/"
    cfp_2016_url = "https://in.pycon.org/cfp/2016/proposals/"
    results = Scrape(cfp_2015_url).start()
    with open("cfp2015.json", "w") as f_out:
        json.dump(results, f_out)
    results = Scrape(cfp_2016_url).start()
    with open("cfp2016.json", "w") as f_out:
        json.dump(results, f_out)
    df1 = json2df("cfp2015.json", 2015)
    df2 = json2df("cfp2016.json", 2016)
    df = pd.concat((df1, df2), axis=0)
    df.to_csv("cfp.tsv", encoding="utf-8", sep="\t", index_label="title")
