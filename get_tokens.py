import sqlalchemy as psql
import pandas as pd

from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

CV = CountVectorizer()
TT = TfidfTransformer()

conn = psql.create_engine(
    'postgresql://postgres:borda1603@localhost:5432/postgres'
).connect()

sql = 'select name from public.vacancies'
vacancies_name = pd.read_sql(sql, conn).name
sql = """
    select
        v.name,
        skill
    from
        public.skills s
        join public.vacancies v
            on v.id = s.vacancy
"""

skills = pd.read_sql(sql, conn)

conn.close()

cv = CountVectorizer(
        ngram_range=(2, 2),
        stop_words=['ведущий', 'главный', 'младший',
                    'эксперт', 'стажер', 'старший',
                    'middle', 'junior', 'senior'],
        min_df=0.001
)
word_vector = cv.fit_transform(vacancies_name)

idf = TT.fit(word_vector)

df_idf = pd.DataFrame(idf.idf_, index=cv.get_feature_names_out(), columns=['idf'])

pivot = pd.DataFrame(
            word_vector.toarray(),
            columns=cv.get_feature_names_out(),
            index=vacancies_name.values
)
