import requests

from config import REG_MESSAGE

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


def race_detail_handler(race_id, data_getter=get_race_detail) -> dict:
    detail = data_getter(race_id)
    if detail['status'] == 404:
        return {'data': None,
                'error': REG_MESSAGE['race_not_found']}
    elif detail['status'] != 200:
        return {'data': None,
                'error': REG_MESSAGE['conection_error']}
    return {'data': detail['data'],
            'error': None}
