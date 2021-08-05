from logger import get_custom_logger

l = get_custom_logger('this')

import time

for i in range(10):
    l.info('this should be flushed')
    time.sleep(1)
