import pandas as pd


# функция для загрузки данных в Exel формат
def save_table(month, manager, coef1, coef2):

    with pd.ExcelWriter("final_report.xlsx", engine="xlsxwriter") as writer:

        # =====================
        # Таблица 1 (по месяцам)
        # =====================
        month.to_excel(writer, sheet_name="Monthly_Report", index=False)

        # =====================
        # Таблица 2 (по менеджерам)
        # =====================
        manager.to_excel(writer, sheet_name="Manager_Report", index=False)

        # =====================
        # Таблица 3 (дашборд)
        # =====================
        coef1.to_excel(writer, sheet_name="Coef_1_Dashboard")
        coef2.to_excel(writer, sheet_name="Coef_2_Dashboard")


def save_csv(month, manager, coef1, coef2):

    month.to_csv("01_month_report.csv", index=False, encoding="utf-8-sig")
    manager.to_csv("02_manager_report.csv", index=False, encoding="utf-8-sig")
    coef1.to_csv("03_coef1_dashboard.csv", encoding="utf-8-sig")
    coef2.to_csv("04_coef2_dashboard.csv", encoding="utf-8-sig")

    print("CSV отчёты созданы")
