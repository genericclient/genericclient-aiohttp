import re


def parse_header_links(value):
    """Return a list of parsed link headers proxies.
    i.e. Link: <http:/.../front.jpeg>; rel=front; type="image/jpeg",<http://.../back.jpeg>; rel=back;type="image/jpeg"
    :rtype: list
    """

    links = []

    replace_chars = ' \'"'

    value = value.strip(replace_chars)
    if not value:
        return links

    for val in re.split(', *<', value):
        try:
            url, params = val.split(';', 1)
        except ValueError:
            url, params = val, ''

        link = {'url': url.strip('<> \'"')}

        for param in params.split(';'):
            try:
                key, value = param.split('=')
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return links


def parse_response_links(response):
    """Returns the parsed header links of the response, if any."""

    header = response.headers.get('link')

    l = {}

    if header:
        links = parse_header_links(header)

        for link in links:
            key = link.get('rel') or link.get('url')
            l[key] = link

    return l
