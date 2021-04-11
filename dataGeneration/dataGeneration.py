from leetCodeCrawler import *
import html
import re
import pandas as pd
from tqdm import tqdm

HTML_RE = re.compile(r'<[^>]+>')

def extractDescription(raw):
  # Discard all texts since the first example.
  match = re.search("<strong>Example.*:</strong>", raw)

  if match:
    raw = raw[:match.start()]

  # Remove HTML tags.
  raw = HTML_RE.sub('', raw)

  # Replace HTML entities (such as &nbsp; and &lt;) with ASCII symbols and strip spaces
  return html.unescape(raw).strip()

def getDataFor(problems):
  # id: List[int], title: List[str], description: List[str], tags: List[List[str]]
  result = {'id': [], 'title': [], 'description': [], 'tags': []}

  for problem in tqdm(problems):
    data = get_problem_by_slug(problem)

    result['id'].append(int(data['questionId']))
    result['title'].append(data['questionTitle'])
    result['description'].append(extractDescription(data['content']))
    result['tags'].append([t['slug'] for t in data['topicTags']])

  return result

def generateAsCSV(fileName='problemData.csv'):
  problems = get_problems()
  print('{} problem titles retrieved.'.format(len(problems)))
  result = getDataFor(problems)
  pd.DataFrame(result).to_csv(fileName, index=False)

if __name__ == '__main__':
  BOLD = '\033[1m'
  END = '\033[0m'

  # problems = getProblems()
  testProblems = ['two-sum', 'number-of-orders-in-the-backlog', '132-pattern', 'transform-to-chessboard']
  result = getDataFor(testProblems)

  for i in range(len(result['id'])):
    print(BOLD + result['title'][i] + END)
    print('-' * 30)
    print(result['description'][i])
    print('\n')

  pd.DataFrame(result).to_csv('data.csv', index=False)
