# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from celery_worker.tasks import resize

import json
import logging
import traceback
import base64
import redis
import os

pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)

class Image(View):
    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            if not body['image_data'] or not body['image_name']:
                raise Exception('Invalid body')

            image_base64 = body['image_data']
            image_data = base64.b64decode(image_base64)

            image_id = 0
            if not r.exists('num'):
                r.set('num', 1)
                image_id = 1
            else:
                image_id = r.incr('num')

            image_name = body['image_name']
            image_path = 'storage/{}_{}.png'.format(image_name, image_id)

            r.hset(image_id, 'name', image_name)
            r.hset(image_id, 'status', 'processing')

            with open(image_path, 'wb') as f:
                f.write(image_data)

            resize.delay(image_id)

            return JsonResponse({'success': True, 'image_id': image_id, 'image_name': image_name})
        except Exception as e:
            logging.error("error: {}".format(traceback.format_exc()))
            return JsonResponse({'success': False}, status=500)

class GetImage(View):
    def get(self, request, image_id):
        try:
            if not r.hexists(image_id, 'name'):
                raise Exception("image id {} is not found".format(image_id))

            image_name = r.hget(image_id, 'name').decode('utf-8')
            image_path_resize = 'storage/{}_{}_resize.png'.format(image_name, image_id)

            image_status = r.hget(image_id, 'status').decode('utf-8')
            if image_status != 'done':
                raise Exception("{} is not resized yet".format(image_path_resize))

            if not os.path.exists(image_path_resize):
                raise Exception("{} is not found".format(image_path_resize))

            encoded_string = ''
            with open(image_path_resize, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            return JsonResponse({'success': True, 'resized_image': encoded_string})
        except Exception as e:
            logging.error("error: {}".format(traceback.format_exc()))
            return JsonResponse({'success': False}, status=500)

