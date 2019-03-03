from __future__ import absolute_import
from celery_worker.celery import app

from PIL import Image
import time
import redis
import os

pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)

@app.task(bind=True, default_retry_delay=10) 
def resize(self, image_id):
    try:
        print("image_id {} will be resized".format(image_id))
        
        if not r.hexists(image_id, 'name'):
            raise Exception("image id {} is not found".format(image_id))

        image_name = r.hget(image_id, 'name').decode('utf-8')
        image_path = 'storage/{}_{}.png'.format(image_name, image_id)

        if not os.path.exists(image_path):
            raise Exception("{} is not found".format(image_path))

        img = Image.open(image_path)
        img_resize = img.resize((100, 100))
        image_path_resize = 'storage/{}_{}_resize.png'.format(image_name, image_id)
        img_resize.save(image_path_resize)

        r.hset(image_id, 'status', 'done')

        print('image resizing finished')
    except Exception as exc:
        raise self.retry(exc=exc)