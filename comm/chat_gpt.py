# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
import openai
from comm.utils import *

openai.api_key = FileUtils.load_json('./conf/conf.json')['api_key'][0]


class ChatGPTHelper:
    @staticmethod
    def search(question: str):
        prompt = f"Human: {question}\nAI:",
        answer = ''
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=[" Human:", " AI:"]
            )
            answer = response.choices[0]['text']
            logger.info(f'A: {answer}')
        except Exception as e:
            logger.error(e)
            return answer
        return answer

    @staticmethod
    def search_from_prompt_json(prompt_path):
        is_finished, item_bp = BreakpointHandler.load()
        if is_finished:
            logger.success('finished getting all answer!')
            return
        prompt_data = FileUtils.load_json(prompt_path)
        for idx, item in enumerate(prompt_data):
            if idx < item_bp or item['A']: continue
            question = item['Q']

            try:
                logger.debug(f'====={idx}=====')
                logger.debug(f'querying in : {question}')
                res = ChatGPTHelper.search(question=question)
                prompt_data[idx]['A'] = res
                FileUtils.write2json(prompt_path, prompt_data)
            except Exception as e:
                logger.error(e)
                BreakpointHandler.save_breakpoint(idx, question)
                return
            except:
                BreakpointHandler.save_breakpoint(idx, question)
                return
        BreakpointHandler.finish()
