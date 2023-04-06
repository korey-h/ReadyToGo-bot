import requests

HOST = 'http://127.0.0.1:8000/api/v1'


def get_races():
    pass


def get_race_detail(race_id):
    data = None
    endpoint = f'/races/{race_id}/'
    url = HOST + endpoint
    r = requests.get(url=url)
    status = r.status_code
    if status == 200:
        data = r.json()
    return {'status': status, 'data': data}


def send_registration(data):
    endpoint = '/registration/'
    url = HOST + endpoint
    r = requests.post(url=url, data=data)
    status = r.status_code
    if status in (201, 400):
        data = r.json()
    return {'status': status, 'data': data}


def upd_registration(data):
    pass


def get_rec_detail(id):
    pass
