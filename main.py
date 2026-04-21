import pandas as pd
import numpy as np
from upload import save_table
from report_table import report_table

# =========================
# 1. Загружаем данные 
# =========================
prol = pd.read_csv('prolongations.csv')
fin = pd.read_csv('financial_data.csv')


# =========================
# 2. Очищаем финансовые данные (убираем дублирующие поля)
# =========================
fin = fin.drop(columns=['Причина дубля', 'Account'])

for col in fin.columns[1:]:
    fin[col] = (
        fin[col].astype(str)
        .str.replace(r'\s+', '', regex=True) # удаляем пробелы
        .str.replace(',', '.', regex=True)   # заменяем запетые на точки
    )
    fin[col] = pd.to_numeric(fin[col], errors='coerce')

fin = fin.groupby('id', as_index=False).sum()


# =========================
# 3. Преобразуем в длинный формат
# =========================
fin = fin.melt(id_vars='id', var_name='month', value_name='revenue')


# =========================
# 4. Преобразуем месяцы и даты
# =========================
months_map = {
    'Январь': '01',
    'Февраль': '02',
    'Март': '03',
    'Апрель': '04',
    'Май': '05',
    'Июнь': '06',
    'Июль': '07',
    'Август': '08',
    'Сентябрь': '09',
    'Октябрь': '10',
    'Ноябрь': '11',
    'Декабрь': '12'
}

# функция конвертации дат в формат datatime
def convert(m):
    name, year = m.split()
    name = name.strip().capitalize()
    return pd.to_datetime(f"{year}-{months_map[name]}-01")

fin['month'] = fin['month'].apply(convert)


# =========================
# 5. Объединение с пролонгациями
# =========================
prol = prol.drop_duplicates('id')

df = fin.merge(prol, on='id', how='left')
df = df.rename(columns={'month_x': 'revenue_month', 'month_y': 'end_month'})

df = df.dropna(subset=['end_month'])
df['end_month'] = df['end_month'].apply(convert)


# =========================
# 6. Фильтруем данные, исключая нулевые и невалидные
# =========================
df = df[df['revenue'] > 0]


# =========================
# 7. Формируем события
# =========================
events = df.groupby(['id', 'revenue_month'], as_index=False)['revenue'].sum()


# =========================
# 8. Сама логика пролонгации
# =========================
event_set = set(zip(events['id'], events['revenue_month']))

def check_prolong(row, offset):
    return (row['id'], row['revenue_month'] + pd.DateOffset(months=offset)) in event_set

events['is_prolong_1'] = events.apply(lambda x: check_prolong(x, 1), axis=1)
events['is_prolong_2'] = events.apply(lambda x: check_prolong(x, 2), axis=1)


# =========================
# 9. Агрегация по проекту
# =========================
project_df = events.groupby('id').agg({
    'is_prolong_1': 'max',
    'is_prolong_2': 'max'
}).reset_index()

project_df = project_df.merge(
    df[['id', 'end_month', 'AM']].drop_duplicates(),
    on='id',
    how='left'
)


# =========================
# 10. Последний месяц проекта
# =========================
last_rev = df[df['revenue_month'] == df['end_month']] \
    .groupby('id', as_index=False)['revenue'].sum()

last_rev = last_rev.rename(columns={'revenue': 'last_month_revenue'})

project_df = project_df.merge(last_rev, on='id', how='left')
project_df['last_month_revenue'] = project_df['last_month_revenue'].fillna(0)


# =========================
# 11. Формирование продлений
# =========================
project_df['revenue_prolong_1'] = np.where(
    project_df['is_prolong_1'],
    project_df['last_month_revenue'],
    0
)

project_df['revenue_prolong_2'] = np.where(
    (project_df['is_prolong_1'] == False) & (project_df['is_prolong_2']),
    project_df['last_month_revenue'],
    0
)


# =========================
# 12. Расчёт коэффициентов
# =========================

# coef_1
agg1 = project_df.groupby(['end_month', 'AM']).agg({
    'last_month_revenue': 'sum',
    'revenue_prolong_1': 'sum'
}).reset_index()

agg1['coef_1'] = np.where(
    agg1['last_month_revenue'] > 0,
    agg1['revenue_prolong_1'] / agg1['last_month_revenue'],
    0
)


# coef_2 (Только не продлевается в первый месяц)
second_base = project_df[project_df['is_prolong_1'] == False]

agg2 = second_base.groupby(['end_month', 'AM']).agg({
    'last_month_revenue': 'sum',
    'revenue_prolong_2': 'sum'
}).reset_index()

agg2['coef_2'] = np.where(
    agg2['last_month_revenue'] > 0,
    agg2['revenue_prolong_2'] / agg2['last_month_revenue'],
    0
)


# =========================
# 13. Финальный отчёт
# =========================
final = agg1.merge(
    agg2[['end_month', 'AM', 'coef_2']],
    on=['end_month', 'AM'],
    how='left'
)


# =========================
# 14. Проверка Результата
# =========================
print(final.head(20))
print(final.describe())


# ========================
# 15 - создаем таблицы
# ========================
try:
    month, manager, coef1, coef2 = report_table(project_df)
    print('Таблицы сформированы.')

except Exception as err:
    print(f'Произошла ошибка: {err}')


# =========================
# 15 - выгрузка в Эксель
# =========================
try:
    save_table(month, manager, coef1, coef2)
    print('final')
except Exception as err:
    print(f'Произошла ошибка: {err}')
