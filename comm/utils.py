# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
import copy
import json
from loguru import logger
import pandas as pd
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


class FileUtils:
    @staticmethod
    def write2json(json_path: str, data):
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info(f'write json to: {json_path}')

    @staticmethod
    def load_json(json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def exl2json(exl_path, json_path, col_name=''):
        json_data = []
        prompt = pd.read_excel(exl_path, engine='openpyxl')
        question = prompt[col_name] if col_name else prompt.iloc[:, 0]
        for q in question:
            json_data.append({
                'Q': q,
                'A': ''
            })
        FileUtils.write2json(json_path, json_data)

    @staticmethod
    def json2excel(json_path: str, excel_path: str, col_name: str = 'Response'):
        data = FileUtils.load_json(json_path)
        df = pd.DataFrame()
        df[col_name] = [item['A'] for item in data]
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)

    @staticmethod
    def mt_json2excel(json_path: str, excel_path: str):
        data = FileUtils.load_json(json_path)
        pid_list, ppid_list, q_list, a_list = [], [], [], []

        data_list = sorted(list(data.items()), key=lambda x: x[0])
        for key, items in data_list:
            for item in items:
                pid_list.append(key)
                ppid_list.append(item['ppid'])
                q_list.append(item['question'])
                a_list.append(item['answer'])
        df = pd.DataFrame()
        df['pid'] = [item for item in pid_list]
        df['ppid'] = [item for item in ppid_list]
        df['query'] = [item for item in q_list]
        df['answer'] = [item for item in a_list]
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)

    @staticmethod
    def multi_excel2json(excel_path: str, json_path: str,
                         col_names: list = None):
        try:
            data = FileUtils.load_json(json_path)
            if data:
                logger.warning('文件存在')
                return
        except:
            pass
        json_data = dict()
        col_names = ['pid', 'ppid', 'prompt'] if not col_names else col_names
        df = pd.read_excel(excel_path, header=None, names=col_names)

        # 先存
        for index, row in df.iterrows():
            if index == 0: continue
            pid, ppid, prompt = row['pid'], row['ppid'], row['prompt']
            key = str(pid)
            if key not in json_data.keys():
                json_data[key] = []

            json_data[key].append({
                'ppid': ppid,
                'question': prompt,
                'answer': ''
            })
        # 再排序
        new_dict = copy.deepcopy(json_data)
        # 对字典中的每个列表进行排序
        for key in new_dict:
            new_dict[key] = sorted(new_dict[key], key=lambda x: x["ppid"])
        new_dict = dict(sorted(new_dict.items(), key=lambda x: x[0]))
        FileUtils.write2json(json_path, new_dict)


class Logger:
    @staticmethod
    def init_logger(logger_path, filter_word='', level='WARNING'):
        logger.add(logger_path, rotation='10 MB',
                   level=level, filter=lambda x: filter_word in x['message'],
                   encoding="utf-8", enqueue=True, retention="30 days")
        logger.info(f'logger file load in: {logger_path}')
        return logger


class BreakpointHandler:
    conf_path = './conf/conf.json'
    cfg = FileUtils.load_json(conf_path)

    @classmethod
    def save_breakpoint(cls, item_idx, question, search_type='sg'):
        item_str = 'mt_item_bp' if search_type == 'mt' else 'item_bp'
        question_str = 'mt_question' if search_type == 'mt' else 'question'
        logger.warning(f'breakpoint in idx {item_idx}')
        cls.cfg = FileUtils.load_json(cls.conf_path)
        cls.cfg['breakpoint'][item_str] = item_idx
        cls.cfg['breakpoint'][question_str] = question
        FileUtils.write2json(cls.conf_path, cls.cfg)

    @classmethod
    def finish(cls, search_type='sg'):
        finished_str = 'mt_is_finished' if search_type == 'mt' else 'is_finished'
        cls.cfg['breakpoint'][finished_str] = True
        FileUtils.write2json(cls.conf_path, cls.cfg)
        logger.success('finished')

    @classmethod
    def load(cls, search_type='sg'):
        finished_str = 'mt_is_finished' if search_type == 'mt' else 'is_finished'
        item_str = 'mt_item_bp' if search_type == 'mt' else 'item_bp'
        is_finished = cls.cfg['breakpoint'][finished_str]
        item_bp = cls.cfg['breakpoint'][item_str]
        return is_finished, item_bp


class DESCryptoUtils:
    conf_path = './conf/conf.json'

    @staticmethod
    def des_crypto(text: str):
        # 定义一个8位的密钥
        key = b'abcdefgh'
        des = DES.new(key, DES.MODE_ECB)
        padded_text = pad(text.encode('utf-8'), DES.block_size)
        encrypted_text = des.encrypt(padded_text)
        print(encrypted_text)
        plain_text = des.decrypt(encrypted_text)
        plain_text = unpad(plain_text, DES.block_size).decode()
        print(plain_text)
        return plain_text
