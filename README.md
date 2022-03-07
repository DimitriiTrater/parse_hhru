# parse_hhru
Это простой парсер вакансий, который работает с API hh.ru<br/>
Он достаёт вакансии с сайтов, а потом и информацию из самих вакансий.<br/>
### Последовательность запуска программ. ###
1. parse_search.py
2. get_tokens.py
3. table_all.py
4. build_report.ipunb
### База данных. ###
Стоит обратить внимание на то, что здесь используется PostgreSQL.<br/>
Вы можете использовать любую другую БД, но для этого измените код.<br/>
База данных должна иметь следующую структуру: <br/>
>/Tables<br/>
>>/skills<br/>
>>>/vacancy<br/>
>>>/skill<br/>
>
>>/vacancies<br/>
>>>/id<br/>
>>>/name<br/>
>>>/description<br/>
<br/>
### Зависимости. ###
Все модули указаны в файле requirements.txt
Но их слишком много, по факту понадобиться только:
- requests
- sqlalchemy
- pandas
- scikit-learn
- IPython
- matloptlib
- ipywidgets
### Результат ###
