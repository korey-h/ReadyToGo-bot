import models as md


def test_race_detail(race_id):
    status = 200
    data = {
        "id": 0,
        "name": "Большая гонка",
        "date": "30.01.2023",
        "cup": {
          "id": 0,
          "name": "Кубок ХС"
        },
        "town": "Дефолтсити",
        "description": "string",
        "is_active": True,
        "categories": [
          {
            "id": 0,
            "name": "Любители"
          }
        ]
    }
    return {'status': status, 'data': data}


def test_reg_send(data):
    status = 200
    data = data
    data['reg_code'] = 'bl-101'
    if data['number'] <= 0:
        status = 400
        data = {
            'number': 'номер должен быть натуральным числом.',
            'name': 'повторите ввод имени.'}
    return {'status': status, 'data': data}


scena = [
    '1',
    'sRaser',
    None,
    'Big',
    None,
    'Wheel',
    'year',
    '2000',
    'City',
    'Self',
    '{"category_id": 0}',
    '-1',
    '2',
    'Racer',
]

registrator = md.RegistrProces()
registrator.race_detail_getter = test_race_detail
registrator.reg_sender = test_reg_send

message = registrator.exec('race_id')
for data in scena:
    print(str(message) + '-> ' + str(data))
    if data is None:
        message = registrator.pass_step()
    else:
        message = registrator.exec(data)
    if not registrator.is_active:
        print(str(message))
        break
