import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


def identify_and_process(file, header_row):
    df = pd.read_excel(file, header=header_row)  # קריאת הקבצים עם כותרות בשורה הנכונה
    return df


def process_files(file1, file2):
    df1 = identify_and_process(file1, 0)  # קריאת הקובץ הראשון עם כותרות בשורה הראשונה
    df2 = identify_and_process(file2, 4)  # קריאת הקובץ השני עם כותרות בשורה הרביעית
    return df1, df2


def save_to_db(df, table_name, db_url='sqlite:///my_database.db'):
    engine = create_engine(db_url)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Data saved to table {table_name} in {db_url}")


st.title("נתוני אשראי וחשבונות בנק")
st.write("העלה שני קבצים לניתוח")

uploaded_files = st.file_uploader("בחר שני קבצים", type=["csv", "xls", "xlsx"], accept_multiple_files=True)

if len(uploaded_files) == 2:
    file1 = uploaded_files[0]
    file2 = uploaded_files[1]

    df1_clean, df2_clean = process_files(file1, file2)

    # הצגת שמות העמודות של כל DataFrame
    st.write("Columns in file1:", df1_clean.columns)
    st.write("Columns in file2:", df2_clean.columns)

    # ניתוח שמות העמודות לפי מה שקיים בקבצים
    if 'תאריך רכישה' in df1_clean.columns:
        df1_clean['תאריך רכישה'] = pd.to_datetime(df1_clean['תאריך רכישה'], format='%d/%m/%Y', errors='coerce')
        df1_clean['סכום עסקה'] = pd.to_numeric(df1_clean['סכום עסקה'], errors='coerce')
        df1_clean = df1_clean.rename(columns={'תאריך רכישה': 'תאריך'})
    else:
        st.error("עמודת 'תאריך רכישה' אינה קיימת בקובץ הראשון.")

    if 'תאריך' in df2_clean.columns:
        df2_clean['תאריך'] = pd.to_datetime(df2_clean['תאריך'], format='%d/%m/%Y', errors='coerce')
        df2_clean['חובה'] = pd.to_numeric(df2_clean['חובה'], errors='coerce')
        df2_clean['זכות'] = pd.to_numeric(df2_clean['זכות'], errors='coerce')
    else:
        st.error("עמודת 'תאריך' אינה קיימת בקובץ השני.")

    # יצירת עמודות זהות בכל הקבצים
    df1_clean['סוג פעולה'] = 'עסקה'
    df1_clean['זכות'] = 0
    df1_clean['חובה'] = df1_clean['סכום עסקה']
    df1_clean = df1_clean[['תאריך', 'סוג פעולה', 'שם בית עסק', 'זכות', 'חובה']]

    df2_clean = df2_clean[['תאריך', 'סוג פעולה', 'תיאור', 'זכות', 'חובה']]
    df2_clean = df2_clean.rename(columns={'תיאור': 'שם בית עסק'})

    # איחוד הנתונים
    df_combined = pd.concat([df1_clean, df2_clean], ignore_index=True)

    # זיהוי והסרת כפילויות
    df_combined.drop_duplicates(subset=['תאריך', 'שם בית עסק', 'זכות', 'חובה'], inplace=True)

    # חישוב סך ההכנסות וההוצאות
    total_income = df_combined['זכות'].sum()
    total_expenses = df_combined['חובה'].sum()
    balance = total_income - total_expenses

    # יצירת DataFrame לתצוגה
    income_expense_data = {
        'סוג': ['הכנסות', 'הוצאות', 'יתרה'],
        'סכום': [total_income, total_expenses, balance]
    }
    income_expense_df = pd.DataFrame(income_expense_data)

    # יצירת הכותרות
    st.title('מאזן הוצאות והכנסות')
    st.header('מאזן הוצאות והכנסות לאחר הסרת כפילויות')

    # הצגת מאזן הוצאות והכנסות
    st.subheader('מאזן הוצאות והכנסות')
    st.table(income_expense_df.style.format({'סכום': '{:,.2f}'}))

    # פילוח הוצאות לפי קטגוריות של בתי העסק
    expense_by_category = df_combined[df_combined['חובה'] > 0].groupby('שם בית עסק')['חובה'].sum().reset_index()
    expense_by_category.columns = ['שם בית עסק', 'סכום הוצאה']
    st.subheader('פילוח הוצאות לפי קטגוריות של בתי העסק')
    st.table(expense_by_category.style.format({'סכום הוצאה': '{:,.2f}'}))

    # פילוח הכנסות לפי קטגוריות של בתי העסק
    income_by_category = df_combined[df_combined['זכות'] > 0].groupby('שם בית עסק')['זכות'].sum().reset_index()
    income_by_category.columns = ['שם בית עסק', 'סכום הכנסה']
    st.subheader('פילוח הכנסות לפי קטגוריות של בתי העסק')
    st.table(income_by_category.style.format({'סכום הכנסה': '{:,.2f}'}))

    # הוספת גרף הוצאות מול הכנסות לפי חודשים
    df_combined['חודש'] = df_combined['תאריך'].dt.to_period('M')
    monthly_expenses = df_combined.groupby('חודש')['חובה'].sum().reset_index()
    monthly_income = df_combined.groupby('חודש')['זכות'].sum().reset_index()

    st.subheader('גרף הוצאות מול הכנסות לפי חודשים')
    st.line_chart(
        data={'הוצאות': monthly_expenses.set_index('חודש')['חובה'], 'הכנסות': monthly_income.set_index('חודש')['זכות']})

    # שמירת הנתונים לבסיס נתונים
    save_to_db(df_combined, 'income_expense')
else:
    st.write("נא להעלות שני קבצים לניתוח.")
