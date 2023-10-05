from bs4 import BeautifulSoup


def get_seo(response):
    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.find('h1')
    if h1:
        h1 = h1.text
    else:
        h1 = ''

    title = soup.find('title')
    if title:
        title = title.text
    else:
        title = ''

    meta_tag = soup.find('meta', {'name': 'description'})
    if meta_tag:
        description = meta_tag['content']
    else:
        description = ''

    return h1, title, description
