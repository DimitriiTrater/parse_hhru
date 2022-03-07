import math
import ipywidgets as widget
import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy as psql

from IPython import display
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

conn = psql.create_engine(
    'postgresql://{Пользователь}:{Пароль}@{Сервер}:{Port}/{База данных}'
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

idf = TfidfTransformer().fit(word_vector)

df_idf = pd.DataFrame(idf.idf_, index=cv.get_feature_names_out(), columns=['idf'])

pivot = pd.DataFrame(
            word_vector.toarray(),
            columns=cv.get_feature_names_out(),
            index=vacancies_name.values
)


def click_back(b):
    """
       Метод, который вызывается при клике на кнопку "Назад".
       Метод скрывает информацию о перечне вакансий из левого сайдбара и
       диаграмму популярности навыков из правого сайдбара, а также отображает
       в центральной части шаблона облако токенов.
    """
    app_layout.left_sidebar = None
    app_layout.right_sidebar = None
    app_layout.center = out_words


def print_words(x):
    """
        Метод, который вызывается при изменении значения слайдера.
        Метод отрисовывает в формате html облако токенов

        Аргумент "x" принимает справочник, который содержит состояние слайдера.
        Используем x.new, чтобы получить новое состояние слайдера.
    """

    ds = df_idf.sort_values(by='idf', ascending=False)[x.new[0]: x.new[1]]

    mx = df_idf['idf'].max()
    mn = df_idf['idf'].min()

    tags = """<style>
    .tagword{
        border:1px solid #bee5eb;
        padding:1px 5px;
        display:block;
        border-radius:4px;
        color:#0c5460;
        background:#d1ecf1;
        line-height:normal;
        cursor:pointer}
    .tagword:hover{
        background:#c1dce1}
    .tag-wrapper{
        float:left;
        margin:0 5px 5px 0}
    </style>"""

    for r in ds.sort_index().itertuples():
        if mx > mn:
            fs = int((((r.idf - mn) / (mx - mn)) * -1 + 1) * 30 + 10)
            hd = math.ceil(fs / 10) * 10 + 8
        else:
            fs = 40
        tag_tmpl = """<div class="tag-wrapper" style="height:{height}px">
            <span onclick="tag_click(this)" class="tagword" style="font-size:{size}px">{name}</span>
        </div>"""
        tags += tag_tmpl.format(name=r.Index, size=fs, height=hd)

    click_back(None)
    out_words.clear_output(wait=True)
    with out_words:
        display.display_html(tags, raw=True)


def get_detail(w):
    """
        Метод отрисовывает детелизацию по токену, а именно перечень вакансий,
        содержащих переданный токен, и топ-20 самых
        востребованных навыков по этим вакансиям.
        Аргумент "w" принимает значение токена, по которому кликнули
    """

    out_details_vac.clear_output(wait=True)
    vacs = pivot[pivot[w] > 0].sort_index().index.unique()
    with out_details_vac:
        display.display_html(
            pd.DataFrame(data=vacs, columns=['Список вакансий:']).to_html(index=False), raw=True
        )

    out_details_skl.clear_output(wait=True)
    skill_pvt = skills \
        .query('name in @vacs') \
        .groupby(by='skill', as_index=False) \
        .agg({'name':'count'}) \
        .sort_values(by='name', ascending=False).head(20)
    fig_h = skill_pvt.shape[0] / 2.5

    with out_details_skl:
        skill_pvt.sort_values(by='name').plot.barh(
                        x='skill',
                        y='name',
                        figsize=(5, fig_h),
                        legend=None,
                        title='ТОП20 Навыков'
        )
        plt.show()

    app_layout.center = None
    app_layout.left_sidebar = out_details_vac
    app_layout.right_sidebar = out_details_skl


if __name__ == "__main__":
    out_header = widget.Output()
    out_words = widget.Output()
    out_details_vac = widget.Output()
    out_details_skl = widget.Output()

    app_layout = widget.AppLayout(
        header=None,
        left_sidebar=None,
        center=out_words,
        right_sidebar=None,
        footer=None,
        pane_heights=[1, 5, '60px']
    )

    sld = widget.IntRangeSlider(
        value=[0, 0],
        min=0,
        max=df_idf['idf'].count(),
        step=1,
        description='Частота:',
        layout={'width': '100%'}
    )

    sld.observe(print_words, names='value')

    bck_btn = widget.Button(
        description='Назад',
        button_style='info'
    )

    bck_btn.on_click(click_back)

    html = """
    <script>
        function tag_click(e){
            var kernel = Jupyter.notebook.kernel
            func = 'get_detail("' + e.innerText + '")'
            kernel.execute(func)
        }
    </script>"""

    with out_header:
        display.display(sld)
        display.display(bck_btn)

    display.display_html(html, raw=True)
    display.display(out_header)
    display.display(app_layout)

    sld.value = [sld.max - 30, sld.max]
