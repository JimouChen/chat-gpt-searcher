# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
import json
from loguru import logger
import pandas as pd


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
    def save_breakpoint(cls, item_idx, question):
        logger.warning(f'breakpoint in idx {item_idx}')
        cls.cfg = FileUtils.load_json(cls.conf_path)
        cls.cfg['breakpoint']['item_bp'] = item_idx
        cls.cfg['breakpoint']['question'] = question
        FileUtils.write2json(cls.conf_path, cls.cfg)

    @classmethod
    def finish(cls):
        cls.cfg['breakpoint']['is_finished'] = True
        FileUtils.write2json(cls.conf_path, cls.cfg)

    @classmethod
    def load(cls):
        is_finished = cls.cfg['breakpoint']['is_finished']
        item_bp = cls.cfg['breakpoint']['item_bp']
        return is_finished, item_bp
