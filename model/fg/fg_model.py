# encoding:utf-8

import json
import time
import requests
from model.model import Model
from common.log import logger
from common import log

user_session = dict()

# OpenAI对话模型API (可用)
class FastgptModel(Model):
    
    def __init__(self):
        log.info("[fg] start")

    def reply(self, query, context = None) :
        if not context or not context.get('type') or context.get('type') == 'TEXT':
            from_user_id = context['from_user_id']
            
            logger.info("from_user_id:"+str(from_user_id))
            
            if query in "#清除记忆":
                user_session[from_user_id] = []
                return '记忆已清除'
            
            tmp = user_session.get(from_user_id, [])
            if len(tmp) == 0:
                user_session[from_user_id] = []
            return self.reply_text(query, from_user_id)

    def reply_text(self, query, from_user_id):
        try:
            # user_session[from_user_id]
            prompts = user_session[from_user_id]
            
            
            baseurl = "https://ai.jianyandashu.com/api/openapi/v1/chat/completions" #可以出现在配置文件中

            # for msg in session:
            #     if "role" in msg and "content" in msg:
            #         if msg["role"] == "Human":
            #             prompt = {"role": "Human", "content": msg["content"]}
            #             prompts.append(prompt)
            #         if msg["role"] == "AI":
            #             prompt = {"role": "AI", "content": msg["content"]}
            #             prompts.append(prompt)

            #     else:
            #         logger.warn(f"无效的消息格式: {msg}")
                    
            if len(query)>0:
                prompt = {"role": "user", "content": query}
                prompts.append(prompt)
            
            # 最大的历史对话保留5个
            if len(prompts)>5 :
                prompts = user_session[from_user_id][-5:]
            
            logger.info(prompts) #打印出来prompts的所有元素,让其实现了连续对话功能.

            #"modelId": "646f8cb16b5becf2dfdf1bd3",#这里是modelid,在fastgpt的ai助手中获得.
            payload = json.dumps({
                "chatId": "",
                "stream": False,
                "messages": prompts
            })

            headers = {
                'Authorization': 'Bearer fastgpt-c7ihrm9s6rc91cu9rb72lfs4-646f8cb16b5becf2dfdf1bd3',
                'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", baseurl, headers=headers, data=payload)

            if response.status_code == 200:
                res = response.json()
                # session = self.sessions.session_reply(res["data"], session_id)
                answer = res["choices"][0]["message"][0]["content"]
                
                prompt = {"role": "assistant", "content": answer}
                prompts.append(prompt)
                user_session[from_user_id] = prompts
                
                return answer
                #return Reply(ReplyType.TEXT, res["data"]) #当然可以在这里增加广告了
            else:
                #time.sleep(2)
                return "error" #出错了

        except Exception as e:
            logger.exception(e)
            # retry
            # time.sleep(2)
            return "error"
