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
  result = {'id': [], 'title': [], 'description': [], 'tags': [], 'likes':[], 'dislikes':[], 'acRate':[], 'dis_tags':[]}

  for problem in tqdm(problems):
    question_details, dis_tags = get_problem_by_slug(problem)

    result['id'].append(int(question_details['questionId']))
    result['title'].append(question_details['questionTitle'])
    result['description'].append(extractDescription(question_details['content']))
    result['tags'].append([t['slug'] for t in question_details['topicTags']])
    result['likes'].append(int(question_details['likes']))
    result['dislikes'].append(int(question_details['dislikes']))
    stats = json.loads(question_details['stats'])
    result['acRate'].append(stats['acRate'])
    result['dis_tags'].append([(tag['name'],tag['numTopics']) for tag in dis_tags])

  return result

def generateAsCSV(fileName='problemData.csv'):
  problems = get_problems()
  print('{} problem titles retrieved.'.format(len(problems)))
  result = getDataFor(problems)
  pd.DataFrame(result).to_csv(fileName, index=False)

if __name__ == '__main__':
  BOLD = '\033[1m'
  END = '\033[0m'

  testProblems = ['two-sum', 'number-of-orders-in-the-backlog', '132-pattern', 'transform-to-chessboard']
  result = getDataFor(testProblems)

  # for i in range(len(result['id'])):
  #   print(BOLD + result['title'][i] + END)
  #   print('-' * 30)
  #   print(result['description'][i])
  #   print('\n')

  pd.DataFrame(result).to_csv('testData.csv', index=False)

  # generateAsCSV()