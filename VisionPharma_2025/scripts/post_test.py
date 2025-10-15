import requests

url = 'http://127.0.0.1:5000/'
file_path = 'sample_data/IMG_20251010_2051272.jpg'

with open(file_path, 'rb') as fh:
    files = {'file': ('IMG_20251010_2051272.jpg', fh, 'image/jpeg')}
    r = requests.post(url, files=files, timeout=20)
    print('STATUS', r.status_code)
    print('CONTENT-TYPE', r.headers.get('content-type'))
    print('LENGTH', len(r.content))
    print('\n--- RESPONSE START (first 2000 chars) ---')
    print(r.text[:2000])
    print('\n--- RESPONSE END ---')
