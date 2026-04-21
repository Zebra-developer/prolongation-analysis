import pandas as pd
import numpy as np


# =================
# функция создания таблиц
# =================
def report_table(project_df):

    # =========================
    # 1. ПО МЕСЯЦАМ
    # =========================
    report_month = project_df.groupby('end_month', as_index=False).agg(
        base_1=('last_month_revenue', 'sum'),
        prolong_1=('revenue_prolong_1', 'sum'),
        base_2=('last_month_revenue', 'sum'),
        prolong_2=('revenue_prolong_2', 'sum')
    )

    report_month['coef_1'] = np.where(
        report_month['base_1'] > 0,
        report_month['prolong_1'] / report_month['base_1'],
        0
    )

    report_month['coef_2'] = np.where(
        report_month['base_2'] > 0,
        report_month['prolong_2'] / report_month['base_2'],
        0
    )


    # =========================
    # 2. ПО МЕНЕДЖЕРАМ
    # =========================
    report_manager = project_df.groupby('AM', as_index=False).agg(
        base_1=('last_month_revenue', 'sum'),
        prolong_1=('revenue_prolong_1', 'sum'),
        base_2=('last_month_revenue', 'sum'),
        prolong_2=('revenue_prolong_2', 'sum')
    )

    report_manager['coef_1'] = np.where(
        report_manager['base_1'] > 0,
        report_manager['prolong_1'] / report_manager['base_1'],
        0
    )

    report_manager['coef_2'] = np.where(
        report_manager['base_2'] > 0,
        report_manager['prolong_2'] / report_manager['base_2'],
        0
    )


    # =========================
    # 3. ДАШБОРД (pivot)
    # =========================
    base = project_df.pivot_table(
        index='AM',
        columns='end_month',
        values='last_month_revenue',
        aggfunc='sum',
        fill_value=0
    )

    p1 = project_df.pivot_table(
        index='AM',
        columns='end_month',
        values='revenue_prolong_1',
        aggfunc='sum',
        fill_value=0
    )

    p2 = project_df.pivot_table(
        index='AM',
        columns='end_month',
        values='revenue_prolong_2',
        aggfunc='sum',
        fill_value=0
    )

    coef1 = p1 / base
    coef2 = p2 / base

    return report_month, report_manager, coef1, coef2