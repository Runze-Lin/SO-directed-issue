import requests
import json
from time import sleep
import os
import pandas as pd
import csv


class GitHubGraphQLQuery(object):
    BASE_URL = "https://api.github.com/graphql"

    def __init__(self, token, query, variables=None, additional_headers=None):
        self._token = token
        self._query = query
        self._variables = variables or dict()
        self._additional_headers = additional_headers or dict()

    @property
    def headers(self):
        default_headers = dict(Authorization="token {}".format(self._token))
        return dict(list(default_headers.items()) + list(self._additional_headers.items()))

    def generator(self):
        while True:
            try:
                yield requests.request(
                    "post",
                    GitHubGraphQLQuery.BASE_URL,
                    headers=self.headers,
                    json={"query": self._query, "variables": self._variables},
                ).json()
            except requests.exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    def iterator(self):
        pass


class GithubSAMLIdentityProvider(GitHubGraphQLQuery):
    QUERY = """
                             query($owner:String!, $name: String!, $num: Int!){
                      repository(owner: $owner, name: $name) {
    issue(number: $num) {
      url
      title
      labels(first:10){
        totalCount
        edges {
          node {
            name
          }
        }
      }
      body
      state
      createdAt
      closedAt
      author {
        login
        avatarUrl
      }
      comments(first:10){
        totalCount
        nodes{
          createdAt
          bodyText
          author{
            login
            avatarUrl
          }
        }
      }
    }
  }
  }

                    
                            """
    ADDITIONAL_HEADERS = dict(Accept="application/vnd.github.vixen-preview+json")

    def __init__(self, token, reponame, cur_num):
        cur_owner, cur_name = reponame.split('/')
        super(GithubSAMLIdentityProvider, self).__init__(
            token=token,
            query=GithubSAMLIdentityProvider.QUERY,
            variables=dict(owner=cur_owner, name=cur_name, num=cur_num),
            additional_headers=GithubSAMLIdentityProvider.ADDITIONAL_HEADERS,
        )
        self._identities = list()

    def iterator(self):
        generator = self.generator()
        response = next(generator)
        return response



def getIssueComments(inputobject, projName, issueId ):
    #headercomment = ['projName', 'issueId',  'createdAt', 'commentAuthorName','commentAuthorId','body']
    result = []
    for onecomment in inputobject:
        outputdata = {}
        outputdata['projName'] = projName
        outputdata['issueId'] = issueId
        outputdata['createdAt'] = onecomment['createdAt']
        try:
            outputdata['commentAuthorName'] = onecomment['author']['login']
            outputdata['commentAuthorId'] = onecomment['author']['avatarUrl'].replace("https://avatars.githubusercontent.com/","")
        except:
            outputdata['commentAuthorName'] = 'ghost'
            outputdata['commentAuthorId'] = 'ghost'
        outputdata['body'] = onecomment['bodyText'].replace('\n', ' ').replace('\r', '')
        result.append(outputdata)
    return result


def getIssueLabels(issue_label):
    result = []
    for onelabel in issue_label:
        result.append(onelabel['node']['name'])

    # i use comma to combine labels, you can replace this if label can contain comma.
    return ",".join(result)



def jsonPR2row(jsonObj, writerPR, writerPRcomments):

    try:
        PR = jsonObj["data"]["repository"]["issue"]
    except:
        print('debug')
        return
    
    if PR is None:
        return

    outputdata = {}
    temp = PR['url'].replace("https://github.com/","").split("/")
    outputdata['projName'] = temp[0]+'/'+temp[1]
    outputdata['issueId'] = temp[3]
    outputdata['createdAt'] = PR['createdAt']
    outputdata['closedAt'] = PR['closedAt']
    outputdata['body'] = PR['body'].replace('\n', ' ').replace('\r', '')
    outputdata['title'] = PR['title']
    outputdata['state'] = PR['state']
    outputdata['totalLabels'] = PR['labels']['totalCount']
    outputdata['labels'] = getIssueLabels(PR['labels']['edges'])
    outputdata['totalComments'] = PR['comments']['totalCount']

    try:
        outputdata['issueAuthorName'] = PR['author']['login']
        outputdata['issueAuthorId'] = PR['author']['avatarUrl'].replace("https://avatars.githubusercontent.com/","")
    except:
        outputdata['issueAuthorName'] = 'ghost'
        outputdata['issueAuthorId'] = 'ghost'

    writerPR.writerow(outputdata)

    outputcommentdata = getIssueComments(PR['comments']['nodes'],outputdata['projName'],outputdata['issueId'])
    for eachcomment in outputcommentdata:
        writerPRcomments.writerow(eachcomment)




def JSON2File(jsonlist, writerPR, writerPRcomments):
    for row in jsonlist:
        jsonPR2row(row, writerPR,writerPRcomments)


def pullGitPRinfo(inputPRIds, outputprFile, outputcommentFile, reponame):
    tokens = [
        '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',
        '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',
        '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',
        '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',
        #the following tokens, i don't know if they still works
        '6f7a442d2c5ef19bffc925107970a4723ba22c69',
        '3722aed91851d1fd31c6358918d9cc0d2bee32e0',
        'a6868dec20b06c5f1b1ca2ed3a0d3270aaa0c080',
        'a84aa6e0775c0b9cd6db97cabb277e2f75af9970'
    ]

    cur_token = 0
    switchtoken = False

    processedPRs = []
    
    writerPR = open(outputprFile, 'w', encoding='utf-8', newline='')
    header = ['projName', 'issueId', 'state', 'createdAt', 'closedAt', 'issueAuthorName','issueAuthorId','title', 
              'labels', 'totalLabels', 'totalComments', 'body']
    CSVPRwriter = csv.DictWriter(writerPR, fieldnames=header, quoting=csv.QUOTE_ALL)
    CSVPRwriter.writeheader()  

    
    writerPRcomments = open(outputcommentFile, 'w', encoding='utf-8', newline='')
    headercomment = ['projName', 'issueId',  'createdAt', 'commentAuthorName','commentAuthorId','body']
    CSVPRcommentwriter = csv.DictWriter(writerPRcomments, fieldnames=headercomment, quoting=csv.QUOTE_ALL)
    CSVPRcommentwriter.writeheader()
    

   

    counter = 0
    with open(inputPRIds, 'r') as f:    
        contents = f.read()
  
    PRids = [int(x.replace("'","").strip(",")) for x in contents.strip().split()]
    
    start_num = 0

    PRids = PRids[start_num:None]
    for curPRid in PRids:
        curPRid = int(curPRid)
        if counter % 100 == 0 and counter > 0:
            print("processed:" + str(counter))
            JSON2File(processedPRs,CSVPRwriter, CSVPRcommentwriter)
            processedPRs.clear()
            sleep(10)

        token = tokens[cur_token]

        runone = GithubSAMLIdentityProvider(token, reponame,curPRid)
        response = runone.iterator()
        counter += 1

        if 'Could not resolve to a PullRequest with the number' in str(response):
            continue

        if ('Bad credentials' in str(response) and "message" in response.keys()) or ('API rate limit exceeded for' in str(response) and "errors" in response.keys()):
            switchtoken = True
            cur_token += 1
            cur_token = cur_token % len(tokens)
            print("token switched")
            token = tokens[cur_token]
            runone = GithubSAMLIdentityProvider(token, reponame, curPRid)
            response = runone.iterator() 
          

        if switchtoken:
            counter -= 1
            switchtoken = False
        else:
            processedPRs.append(response)
            JSON2File(processedPRs,CSVPRwriter,CSVPRcommentwriter)
            processedPRs.clear()

    if len(processedPRs) > 0:
        JSON2File(processedPRs,CSVPRwriter,CSVPRcommentwriter)
        processedPRs.clear()



if __name__ == '__main__':
    root = 'E:/qrf/Lab Stuff/newDataset'

    projName = 'flutter'
    reponame = 'flutter/flutter'

    prIdFile = root + '/' + projName + '.txt'
    outputprFile = root + '/' + projName + '_PRs.txt'
    outputcommentFile = root + '/' + projName + '_PRcomments.txt'

    pullGitPRinfo(prIdFile,outputprFile, outputcommentFile, reponame)
    print('completed for this project!')
