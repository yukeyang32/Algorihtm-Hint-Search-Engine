import requests,json,re
from requests_toolbelt import MultipartEncoder

session = requests.Session()
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

"""
def login(username, password):
    url = 'https://leetcode.com'
    cookies = session.get(url).cookies
    for cookie in cookies:
        if cookie.name == 'csrftoken':
            csrftoken = cookie.value

    url = "https://leetcode.com/accounts/login"
        
    params_data = {
        'csrfmiddlewaretoken': csrftoken,
        'login': username,
        'password':password,
        'next': 'problems'
    }
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', 'Referer':         'https://leetcode.com/accounts/login/',
        "origin": "https://leetcode.com"}
    m = MultipartEncoder(params_data)   

    headers['Content-Type'] = m.content_type
    session.post(url, headers = headers, data = m, timeout = 10, allow_redirects = False)
    is_login = session.cookies.get('LEETCODE_SESSION') != None
    return is_login
"""

def get_problems():
    url = "https://leetcode.com/api/problems/all/"
    result = []
    
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    resp = session.get(url, headers = headers, timeout = 10)
       
    question_list = json.loads(resp.content.decode('utf-8'))

    for question in question_list['stat_status_pairs']:
        # 题目编号
        # question_id = question['stat']['question_id']
        # 题目名称
        question_slug = question['stat']['question__title_slug']
        # 题目状态
        # question_status = question['status']

        # 题目难度级别，1 为简单，2 为中等，3 为困难
        # level = question['difficulty']['level']

        # 是否为付费题目
        if not question['paid_only']:
          result.append(question_slug)

    return result

def get_problem_by_slug(slug):
    url = "https://leetcode.com/graphql"
    headers = {'User-Agent': user_agent, 'Connection':
        'keep-alive', 'Content-Type': 'application/json',
        'Referer': 'https://leetcode.com/problems/' + slug}

    ###############################################
    ## crawle question details
    ################################################
    # params for crawling each leetcode question details
    question_params = {'operationName': "getQuestionDetail",
        'variables': {'titleSlug': slug},
        'query': '''query getQuestionDetail($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                questionTitle
                questionTitleSlug
                content
                difficulty
                dislikes
                likes
                stats
                similarQuestions
                categoryTitle
                topicTags {
                        name
                        slug
                }
            }
        }'''
    }

    json_data = json.dumps(question_params).encode('utf8')
    resp = session.post(url, data = json_data, headers = headers, timeout = 10)
    question_details = resp.json()['data']['question']

    ##############################################
    ## crawle discussion tags
    ################################################
    # get questionId
    quesionId = question_details['questionId']
    # params for crawling each leetcode question's discussion tags
    diss_tag_params = {"operationName": "discussQuestionTopicTags",
                      "variables": {"selectedTags": [], "questionId": quesionId},
                      "query": '''query discussQuestionTopicTags($tagType: String, $questionId: String!, $selectedTags: [String!]) {
            discussQuestionTopicTags(tagType: $tagType, questionId: $questionId, selectedTags: $selectedTags) {
                ...TopicTag\n}\n}

                fragment TopicTag on DiscussTopicTagNode {
                name
                slug
                numTopics
                }
                '''
                      }

    json_data = json.dumps(diss_tag_params).encode('utf8')
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    dis_tags = resp.json()['data']['discussQuestionTopicTags']
    return question_details, dis_tags
