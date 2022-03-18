import logging


def getlogger():
    # 初始化
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(message)s')
    # 生成日志句柄
    logger = logging.getLogger("logger")
    return logger
