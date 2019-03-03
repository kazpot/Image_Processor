from django.test import TestCase

from celery_worker.tasks import resize

import json
import redis
import os
import base64

class ImageTestCase(TestCase):
    def setUp(self):
        pool = redis.ConnectionPool(host='redis', port=6379, db=0)
        self.r = redis.StrictRedis(connection_pool=pool)
        self.r.flushdb()

        self.image_name = 'testimage'
        self.image_data = 'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAABmdJREFUeJzt3WmIVWUcx/HvjNvoaK6ZW01i2qZZFolWlmVpZZlWQrQhkVDZIiRFVExRlG0kZYkttmkFLa+sIAjyVRQGvQgCpTdGRbZQaRpk9uI/QzqemTnnPM9znnPu+X3gQfDe8/yfM/d/7zn32S6IiIiIiIiIiIiIiIiIiIiIiIiISCNo6vj3bGAtMOmA/5PGtB/4FrgJ2NIEtAI7gOExWyWF+wWY0AxMQS9+HY0EJjcDfWK3RKLp07ebB/YCvxfZEgluGDAg6YHTsBuDA8tbxbVLCvIOh77OJzdHbZJEpwSoOSVAzSkBak4JUHNKgJoLkQD9gCGB6hbPfL1IM4B1wHbgb+APYA+wFWgHxnqKIwG4dAQNAzYlHN+17AHuRp8KMXnvCBoPfAZcleK5LcAjwNtAd93PEkHeBBgIfAgcm/G4K4A1OWNKAHkToB2YlvPYm4Fzcx4rnuVJgBHArY5x2x2PF0/yJMDl2CXAxVnAUY51iAd5EuBMT7F91SMO8iRAm6fYR3uqRxzkSQBfU8j0dbAE8iTAj55i/+CpHnGQJwG+8BT7c0/1iIM8CfAe1o3oYhvwlWMd4kGeBNgOvOsYd7Xj8TGMAO7CurPXARfEbY4/eQaDJmArS3obBEoqn1K9QaEzgJ849Fw+wBKjCrwOBn0HLAZ2ZzzuG2w84N+ccWOYBnwEHJ7w2IVYQg8rtEUeubwTtwBzsOt5Gpuxzp+dDjGLNgS75xncw3OmAhuKaU4YrgtDWoA7gK8T6vkH+AS41GN7i7SR9Je2FZHamFbiJQD8rgwaB8wFFgKzgMOcmhzXMrLd2+yl4w9aUokJ4Ls37vuOUnXHAc9mPGYA9g3hVGCX9xYFUrW78SK0YC/koBzHTsE22qgMJcChngJOcjj+OuBaT20JTglwsCXY1imungMme6gnOCXA/9qAlzzVNRi7jPT3VF8wSgDTF5ve7rND5xTgcY/1BaEEMA8CswPUextwSYB6vVECwDxskCeUDdjYSSnVPQFGA68T9u8wEutRLOVmXHVOgCbgNWBMAbHmAPcXECezOifAKmB+gfHuBc4pMF4qdU2AmcBDBcdsBt4ARhUct0d1TIChwJvYPgZFGw+8EiFut+qYAOuBiRHjXwysjBj/IGVJgCbgamzmzZfYzdmsAHGWA0sD1JvVo9ioYSnE3im0BXg/oQ37sYEZX0l6IvBXN3FilG3YjKOilHan0JeBy7p5bCX2ke1qINY377qo1adjsNnF0cX8BFiREDup3OAYZ33KODHKMsdzS6uQKWFZTMemUaX5I+0Gjs8ZZ2nKGLHKLmwGUmilugS0Yh/JiduXJxjU8fyWjHEm4ucSElIr9obLem5exEqAtWTfX2gadlOYVj/s+/7QjHFimA48GSt40ZeAaxLiZSlLUsZ5zDFOjLI45bnlUYp7gMnAnwnxspTf6H2TivnY6qPYL2jW8ivhts6Jfg/QH0usnlbZpNG5OWV3U9rHYB1JVfz5u+HYZauwzTOKTIDV2JayPszGZvF01TngMtpTnBhmAw8UGbCIS8DChBiuZR9wXpc49wSIE6MknZuraJeA8YRZPNmMzebpfLcX/s4JqOu5BQ0Uuv6NhBsDHwu8iq3R7+m+oIo6zy3ovUzoBLgP+13ikBZgI4i9fTOoogXAnSEDhEyAOVgCFKERX/xODwOnh6o8VAKUeiZsxfTDbsqD9GiGSoANlHgufAUFG9MIkQC3U/LVMBW1FLjRd6W+E2AG1gcvYawBTvBZoc8EGIxdq0q/IrbCvM9s8pkAz1ORNfEVNxV42ldlvhLgemyYV4qxHLjSR0U+EqBy++I0iBfw8JsLrgnQuTNWq2tDJLOh2D2XU/e3awI8Qbn3xmt0M7GewtxcEmAR5d8dsw5W4bBzed4EOBJb0CHxNWFDx7n2Ocj7m0GbqM426XXQudNJ5qHjPAnQjn7yrYzmYT/QnUnWBJiLTbuScsq821mWBBiFTbgsw4JSSda53+HwtAekfTGbsOlJ43I0SorVBryY9slpOxEuAo4AtuZpkRSuDTgf+Li3J6ZNgM0dRRqMruc1pwSoue4uAYuBn4tsiASXuB9RdwnQH5vZKw2uGVuHJvW0rwkby99Bhs4DaQg7gaP6YhswLQKeASZRzXX1kt5+7AfAb8E26RIRERERERERERERERERERERERGRBvAf2TGE3GmqfOAAAAAASUVORK5CYII='

    def test_post_success(self):
        post_data = {
            'image_name': self.image_name,
            'image_data': self.image_data,
        }
        response = self.client.post('/image/', json.dumps(post_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True, 'image_id': 1, 'image_name': 'testimage'}
        )
        
        image_id = self.r.get('num').decode('utf-8')
        image_name = self.r.hget(image_id, 'name').decode('utf-8')
        image_path = 'storage/{}_{}.png'.format(image_name, image_id)

        self.assertEqual(image_id, '1')
        self.assertEqual(image_path, 'storage/testimage_1.png')
        self.assertEqual(os.path.exists(image_path), True)

    def test_post_image_name_missing_error(self):
        post_data = {
            'image_name': '',
            'image_data': self.image_data,
        }
        response = self.client.post('/image/', json.dumps(post_data), content_type="application/json")
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': False}
        )

    def test_post_image_data_missing_error(self):
        post_data = {
            'image_name': self.image_name,
            'image_data': '',
        }
        response = self.client.post('/image/', json.dumps(post_data), content_type="application/json")
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': False}
        )

    def test_get_image_success(self):
        image_id = 99
        image_path = 'storage/{}_{}.png'.format(self.image_name, image_id)
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(self.image_data))

        self.r.hset(image_id, 'name', self.image_name)
        self.r.hset(image_id, 'status', 'done')

        resize(image_id)

        response = self.client.get('/image/99/thumbnail/')
        self.assertEqual(response.status_code, 200)

        image_path_resize = 'storage/{}_{}_resize.png'.format(self.image_name, image_id)
        self.assertEqual(os.path.exists(image_path_resize), True)

        encoded_string = ''
        with open(image_path_resize, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True, 'resized_image': encoded_string}
        )

    def test_get_image_missing_error(self):
        response = self.client.get('/image/1/thumbnail/')
        self.assertEqual(response.status_code, 500)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': False}
        )
