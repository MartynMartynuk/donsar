def album_handle(album):
    with open('file.txt', 'wb+') as destination:
        for chunk in album.chunks():
            destination.write(chunk)
