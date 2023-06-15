import time
import openai
from comm.utils import *

REQ_TIME = 15

api_key_index = 0
openai.api_key = FileUtils.load_json('./conf/conf.json')['api_key'][api_key_index]


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
            return str(e)
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
                if 'You exceeded your current quota' in res:
                    logger.warning('账号次数用完，请换账号或者隔一段时间再试试！')
                    BreakpointHandler.save_breakpoint(idx, question)
                    exit(0)
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

    @staticmethod
    def multi_search(messages):
        MODEL = "gpt-3.5-turbo-16k"
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6
        )
        return response['choices'][0]['message']['content']

    @staticmethod
    def multi_search_each_conversation(json_path: str):
        is_finished, item_bp = BreakpointHandler.load(search_type='mt')
        if is_finished:
            logger.success('finished getting all answer!')
            return
        multi_json = FileUtils.load_json(json_path)
        for idx, (pid, items) in enumerate(multi_json.items()):
            # 只记录到当前轮
            if idx < item_bp: continue
            messages = [{"role": "user", "content": ""}]
            for sub_idx, item in enumerate(items):
                question = item['question']
                try:
                    logger.debug(f'====={idx}=====')
                    d = {"role": "user", "content": question}
                    messages.append(d)
                    answer = ChatGPTHelper.multi_search(messages)
                    multi_json[pid][sub_idx]['answer'] = answer
                    logger.info(f'Q: {question}')
                    logger.info(f'A: {answer}')
                    FileUtils.write2json(json_path, multi_json)
                    d = {"role": "assistant", "content": answer}
                    messages.append(d)
                except Exception as e:
                    logger.error(e)
                    messages.pop()
                    BreakpointHandler.save_breakpoint(idx, question, search_type='mt')
                    return
                except:
                    BreakpointHandler.save_breakpoint(idx, question, search_type='mt')
                    messages.pop()
                    return
                logger.warning('sleeping...')
                for _ in range(REQ_TIME):
                    time.sleep(1)
                    print(f'{_ + 1}s===>', end=' ')
                print()
        BreakpointHandler.finish(search_type='mt')
