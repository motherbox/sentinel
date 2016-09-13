""".."""

from bs4 import BeautifulSoup as Bs
import requests
import traceback
import json
import sys


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
            self.result[title] = temp

        # from pprint import pprint
        # # Printing data
        # pprint(self.result)
        return self.result

if __name__ == '__main__':
    results = Scrape(sys.argv[1]).start()
    with open(sys.argv[2], "w") as f_out:
        json.dump(results, f_out)
