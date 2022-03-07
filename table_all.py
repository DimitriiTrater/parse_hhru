import pandas as pd
import os
import json

from sqlalchemy import engine as psql
from IPython import display


class DB:
    def __init__(self) -> None:
        pass

    def create(self):
        IDs = []
        names = []
        descriptions = []
        skills_vac = []
        skills_name = []
        cnt_docs = len(os.listdir('./docs/vacancies'))
        i = 0

        for fl in os.listdir('./docs/vacancies'):
            f = open(f'./docs/vacancies/{fl}', encoding='utf8')
            json_text = f.read()
            f.close()

            json_object = json.loads(json_text)

            IDs.append(json_object['name'])
            names.append(json_object['name'])
            descriptions.append(json_object['description'])

            for skl in json_object['key_skills']:
                skills_vac.append(json_object['id'])
                skills_name.append(skl['name'])

            i += 1
            display.clear_output(wait=True)
            display.display(f'Готово {i} из {cnt_docs}')

        eng = psql.create_engine(
            'postgresql://{Пользователь}:{Пароль}@{Сервер}:{Port}/{База данных}'
        )
        conn = eng.connect()

        df = pd.DataFrame({
                'id': IDs,
                'name': names,
                'description': descriptions
            })

        df.to_sql(
                'vacancies',
                conn,
                schema='public',
                if_exists='append',
                index=False
            )

        df = pd.DataFrame({
                'vacancy': skills_vac,
                'skill': skills_name
            })

        df.to_sql(
                'skills',
                conn,
                schema='public',
                if_exists='append',
                index=False
            )
        conn.close()

        display.clear_output(wait=True)
        display.display('Вакансии загружены в БД')


if __name__ == '__main__':
    db = DB()
    db.create()
