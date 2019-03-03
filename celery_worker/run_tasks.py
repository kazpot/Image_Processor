from .tasks import resize
import time

if __name__ == '__main__':
    images = ['test.png']
    for image_name in images:
        print('Task running!!!')
        resize.delay(image_name)
