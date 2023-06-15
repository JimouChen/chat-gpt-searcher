# !usr/bin/env python3
# -*- coding: utf-8 -*-
from comm.utils import *
from comm.chat_gpt import ChatGPTHelper

if __name__ == '__main__':
    cfg_data = FileUtils.load_json('./conf/conf.json')
    logger = Logger.init_logger(
        logger_path=cfg_data['path']['mt_log'],
        level='INFO'
    )
    FileUtils.multi_excel2json(cfg_data['path']['mt_prompt'],
                               cfg_data['path']['mt_answer'])

    ChatGPTHelper.multi_search_each_conversation(json_path=cfg_data['path']['mt_answer'])

    FileUtils.mt_json2excel(cfg_data['path']['mt_answer'],
                            cfg_data['path']['mt_response'])
