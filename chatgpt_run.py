# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
from comm.utils import *
from comm.chat_gpt import ChatGPTHelper

if __name__ == '__main__':
    cfg_data = FileUtils.load_json('./conf/conf.json')
    logger = Logger.init_logger(
        logger_path=cfg_data['path']['log'],
        level='INFO'
    )

    FileUtils.exl2json(cfg_data['path']['prompt'],
                       cfg_data['path']['answer'],
                       'Q')
    ChatGPTHelper.search_from_prompt_json(prompt_path=cfg_data['path']['answer'])
    FileUtils.json2excel(cfg_data['path']['answer'],
                         cfg_data['path']['response'])
