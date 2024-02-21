from googleapiclient.discovery import build
from py_expression_eval import Parser
import re, time, os
import requests, json


#google search api key
os.environ["GOOGLE_CSE_ID"] = ""
os.environ["GOOGLE_API_KEY"] = ""

#Google search engine
def search(search_term):
    print(search_term)
    search_result = ""
    service = build("customsearch", "v1", developerKey=os.environ.get("GOOGLE_API_KEY"))
    res = service.cse().list(q=search_term, cx=os.environ.get("GOOGLE_CSE_ID"), num = 10).execute()
    print(res)

    if "items" not in res.keys():
      return None
    else:
      for result in res['items']:
          search_result = search_result + result['snippet']
      return search_result

#Calculator
parser = Parser()
def calculator(str):
    return parser.parse(str).evaluate({})


System_prompt = """
回答以下问题并尽可能遵守以下命令：

您可以使用以下工具：

Search：当您需要回答有关时事的问题时很有用。您应该提出有针对性的问题。
Calculator：当您需要回答数学问题时很有用。使用python代码，例如：2 + 2
Response To Human：当您需要对正在与您交谈的人做出反应时。

您将收到来自人类的消息，然后您应该开始一个循环并执行以下两件事之一

选项1：使用工具来回答问题。
为此，您应该使用以下格式：
Thought：你应该思考现在该做什么
Action：要使用的工具，应该是[Search、Calculator]之一
Action Input：要发送到工具的动作的输入

此后，人类将通过观察做出回应，您将继续。

选项 2：你对人类做出回应。
为此，您应该使用以下格式：
<begin>
Action: Response To Human
Action Input: 你回复人类的内容，总结您所做的和学到的内容
<eos>
Begin!
"""


from openai import OpenAI, AsyncOpenAI


#openai api key
client = OpenAI(
    api_key="",
)

def Stream_agent(prompt):

    message = [
        { "role": "system", "content": System_prompt },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    def extract_action_and_input(text):
          action_pattern = r"Action: (.+?)\n"
          input_pattern = r"Action Input:(.+?)\n"
          action = re.findall(action_pattern, text)
          action_input = re.findall(input_pattern, text)
          print(action)
          print(action_input)
          return action, action_input
    while True:

        response = client.chat.completions.create(
          model="gpt-3.5-turbo",  # Your desired model
          messages=message
        )

        #res_json = json.loads(response.text)
        response_text = response.choices[0].message.content
        print(response_text)
        #To prevent the Rate Limit error for free-tier users, we need to decrease the number of requests/minute.
        #time.sleep(20)
        action, action_input = extract_action_and_input(response_text)
        if "Search" in action[-1]:
            tool = search
        elif "Calculator" in action[-1]:
            tool = calculator
        else:
            res = re.findall(r"Action Input:(.+?)$", response_text)
            print(f"Response: {res}")
            break

        observation = tool(action_input[-1].strip("\""))
        print("Observation: ", observation)
        message.extend([
            { "role": "system", "content": response_text },
            { "role": "user", "content": f"Observation: {observation}" },
            ])


Stream_agent("中国A股的走势")
