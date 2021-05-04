import argparse
import csv
# from getpass2 import getpass2
import requests
import pandas

# modified code from here:https://gist.github.com/patrickfuller/e2ea8a94badc5b6967ef3ca0a9452a43

# indicate repo and if issues requested are open or closed
repo = 'thinkWhere/groundmapper-client'
state = 'open'
# provide username and password
username = "KirstenReilly"
password = "*token*"

auth = (username, password)


def write_issues(r, csvout):
    """Parses JSON response and writes to CSV."""
    if r.status_code != 200:
        raise Exception(r.status_code)
    for issue in r.json():
        if 'pull_request' not in issue:
            labels = ', ' .join([label['name'] for label in issue['labels']])
            date = issue['created_at'].split('T')[0]
            # Change the following line to write out additional fields
            csvout.writerow([labels, issue['title'], issue['state'], date,
                             issue['html_url']])


def get_issues():
    """Requests issues from GitHub API and writes to CSV file."""
    url = 'https://api.github.com/repos/{}/issues?state={}'.format(repo, state)
    r = requests.get(url, auth=auth)
    print(url)

    csvfilename = 'issues.csv'
    with open(csvfilename, 'w', newline='') as csvfile:
        csvout = csv.writer(csvfile)
        csvout.writerow(['Labels', 'Title', 'State', 'Date', 'URL'])
        write_issues(r, csvout)

        # Multiple requests are required if response is paged
        if 'link' in r.headers:
            pages = {rel[6:-1]: url[url.index('<')+1:-1] for url, rel in
                     (link.split(';') for link in
                      r.headers['link'].split(','))}
            while 'last' in pages and 'next' in pages:
                pages = {rel[6:-1]: url[url.index('<')+1:-1] for url, rel in
                         (link.split(';')for link in
                          r.headers['link'].split(','))}
                r = requests.get(pages['next'], auth=auth)
                write_issues(r, csvout)
                if pages['next'] == pages['last']:
                    break
get_issues()
