# End points
* POST /image
    * Submit the image in base64 encoded format for resizing to 100px x 100px thumbnail

Request
```
curl http://localhost:8000/image/ -X POST -d '{"image_name":"sample1", "image_data": base64_encoded_string}' -H "Content-Type: application/json"
```

Response
```
{'success': True, 'image_id': image_id, 'image_name': image_name}
```

* GET /image/${imageId}/thumbnail
    * Retrieving resized image in base64 encoded format. 

Response
```
{'success': True, 'resized_image': base64_encoded_string}
```

# Build images
```
docker build -t celery -f dockerfile_celery .
docker build -t web -f dockerfile_web .
```

# Run services
```
docker-compose up -d
```


# Test
```
docker build -t test -f dockerfile_test .
docker-compose -f docker-compose-test.yml run --rm test
```