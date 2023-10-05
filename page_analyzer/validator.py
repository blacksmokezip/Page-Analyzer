def validate(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return 'Некорректный URL'
    if len(url) > 255:
        return 'URL превышает 255 символов'


def normalize_url(url):
    return f'{url.scheme}://{url.netloc}'
