import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go


np.random.seed(42)
количество_заявок = 300
даты = pd.date_range('2025-01-01', '2026-02-01', periods=количество_заявок)

статусы = np.random.choice(
    ['Черновик', 'Новая', 'На согласовании', 'Ожидание предоплаты',
     'В перевозке', 'Закрыта', 'Аннулирована'],
    количество_заявок,
    p=[0.02, 0.05, 0.08, 0.20, 0.25, 0.30, 0.10]
)

суммы = np.random.uniform(10000, 500000, количество_заявок).round(2)
есть_предоплата = np.random.choice([True, False], количество_заявок, p=[0.65, 0.35])

срок_оплаты = [д + timedelta(days=1) for д in даты]

даты_оплаты = []
for i, д in enumerate(даты):
    if есть_предоплата[i]:
        if np.random.random() > 0.3:
            даты_оплаты.append(д + timedelta(hours=np.random.uniform(2, 48)))
        else:
            даты_оплаты.append(None)
    else:
        даты_оплаты.append(None)

клиенты = np.random.randint(1, 60, количество_заявок)
менеджеры = np.random.choice(['Анна', 'Ольга', 'Иван', 'Дмитрий'], количество_заявок)

дни_недели_рус = []
for д in даты:
    if д.dayofweek == 0: дни_недели_рус.append('Понедельник')
    elif д.dayofweek == 1: дни_недели_рус.append('Вторник')
    elif д.dayofweek == 2: дни_недели_рус.append('Среда')
    elif д.dayofweek == 3: дни_недели_рус.append('Четверг')
    elif д.dayofweek == 4: дни_недели_рус.append('Пятница')
    elif д.dayofweek == 5: дни_недели_рус.append('Суббота')
    elif д.dayofweek == 6: дни_недели_рус.append('Воскресенье')

данные = pd.DataFrame({
    'номер_заявки': range(1, количество_заявок+1),
    'дата_создания': даты,
    'статус': статусы,
    'сумма': суммы,
    'предоплата': есть_предоплата,
    'клиент': клиенты,
    'менеджер': менеджеры,
    'срок_оплаты': срок_оплаты,
    'дата_оплаты': даты_оплаты,
    'день_недели': дни_недели_рус
})

данные['просрочка'] = (
    данные['предоплата'] &
    данные['дата_оплаты'].isna() &
    (данные['срок_оплаты'] < datetime(2026, 2, 1))
)

данные['месяц'] = данные['дата_создания'].dt.to_period('M').astype(str)

всего_заявок = len(данные)
выручка = данные[данные['статус'] == 'Закрыта']['сумма'].sum()
количество_просрочек = данные['просрочка'].sum()
сумма_просрочек = данные[данные['просрочка']]['сумма'].sum()
конверсия = len(данные[данные['статус'].isin(['В перевозке', 'Закрыта'])]) / len(данные) * 100


print("РЕЗУЛЬТАТЫ АНАЛИЗА ЗАЯВОК НА ПЕРЕВОЗКУ")
print(f"Всего заявок:           {всего_заявок}")
print(f"Выручка (закрытые):     {выручка:,.0f} руб.")
print(f"Просрочек предоплаты:   {количество_просрочек}")
print(f"Сумма просрочек:        {сумма_просрочек:,.0f} руб.")
print(f"Конверсия в рейс:       {конверсия:.1f}%")
print("=" * 50)

воронка = данные.groupby('статус').size().reset_index(name='количество')
порядок_статусов = ['Черновик', 'Новая', 'На согласовании', 'Ожидание предоплаты', 'В перевозке', 'Закрыта', 'Аннулирована']
воронка['статус'] = pd.Categorical(воронка['статус'], categories=порядок_статусов, ordered=True)
воронка = воронка.sort_values('статус')

fig1 = go.Figure(go.Funnel(
    y=воронка['статус'],
    x=воронка['количество'],
    textinfo="value+percent initial",
    marker=dict(color="steelblue", line=dict(color="black", width=1)),
    textfont=dict(size=12, color="black")
))
fig1.update_layout(
    title="Воронка заявок на перевозку",
    xaxis_title="Количество заявок",
    yaxis_title="Статус",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="black", size=12),
    xaxis=dict(showgrid=True, gridcolor="lightgray", showline=True, linecolor="black"),
    yaxis=dict(showgrid=True, gridcolor="lightgray", showline=True, linecolor="black")
)
fig1.show()

просрочки_по_месяцам = данные[данные['просрочка']].groupby('месяц').agg(
    количество=('номер_заявки', 'count'),
    сумма=('сумма', 'sum')
).reset_index()

if len(просрочки_по_месяцам) > 0:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=просрочки_по_месяцам['месяц'],
        y=просрочки_по_месяцам['количество'],
        name='Количество просрочек',
        marker=dict(color='crimson', line=dict(color='black', width=1)),
        yaxis='y'
    ))
    fig2.add_trace(go.Scatter(
        x=просрочки_по_месяцам['месяц'],
        y=просрочки_по_месяцам['сумма'],
        name='Сумма просрочек (руб)',
        mode='lines+markers',
        line=dict(color='navy', width=3),
        marker=dict(size=8, color='navy', line=dict(color='black', width=1)),
        yaxis='y2'
    ))
    fig2.update_layout(
        title="Просроченная предоплата по месяцам",
        xaxis=dict(title="Месяц", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black", tickangle=45),
        yaxis=dict(title="Количество заявок", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black", side="left"),
        yaxis2=dict(title="Сумма (руб)", showgrid=False, showline=True, linecolor="black", overlaying="y", side="right"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black", size=12),
        legend=dict(x=0.02, y=0.98)
    )
    fig2.show()

по_дням = данные.groupby('день_недели').size().reset_index(name='количество')
порядок_дней = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
по_дням['день_недели'] = pd.Categorical(по_дням['день_недели'], categories=порядок_дней, ordered=True)
по_дням = по_дням.sort_values('день_недели')

fig3 = go.Figure(go.Bar(
    x=по_дням['день_недели'],
    y=по_дням['количество'],
    text=по_дням['количество'],
    textposition='outside',
    marker=dict(color='royalblue', line=dict(color='black', width=1))
))
fig3.update_layout(
    title="Загрузка по дням недели",
    xaxis=dict(title="День недели", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black"),
    yaxis=dict(title="Количество заявок", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="black", size=12)
)
fig3.show()

по_менеджерам = данные.groupby('менеджер').agg(
    количество=('номер_заявки', 'count'),
    выручка=('сумма', lambda x: x[данные.loc[x.index, 'статус'] == 'Закрыта'].sum())
).reset_index()

fig4 = go.Figure(go.Bar(
    x=по_менеджерам['менеджер'],
    y=по_менеджерам['количество'],
    text=по_менеджерам['выручка'],
    texttemplate='%{text:,.0f} руб.',
    textposition='outside',
    marker=dict(color='forestgreen', line=dict(color='black', width=1))
))
fig4.update_layout(
    title="Загрузка менеджеров",
    xaxis=dict(title="Менеджер", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black"),
    yaxis=dict(title="Количество заявок", showgrid=True, gridcolor="lightgray", showline=True, linecolor="black"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="black", size=12)
)
fig4.show()

print("\nДашборд сформирован. Все графики должны открыться в браузере.")