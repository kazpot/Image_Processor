from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import Image
from .views import GetImage

urlpatterns = [
    path('image/', csrf_exempt(Image.as_view()), name='image'),
    path('image/<int:image_id>/thumbnail/', csrf_exempt(GetImage.as_view()), name='getimage'),
]
