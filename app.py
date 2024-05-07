import os
import base64
from io import BytesIO
from googletrans import Translator# pip install googletrans==4.0.0-rc1
import pandas as pd # pip install pandas
from sklearn.cluster import KMeans # pip install scikit-learn
import streamlit as st # pip install streamlit
import requests # pip install requests

translator = Translator()

class Transaction:
    def __init__(self, date, description, amount, category):
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category

class Budget:
    def __init__(self, categories):
        self.categories = categories
        self.expenses = []

    def add_expense(self, transaction):
        self.expenses.append(transaction)

    def get_total_expenditure(self):
        total = 0
        for expense in self.expenses:
            total += expense.amount
        return total

    def get_category_expenditure(self, category):
        total = 0
        for expense in self.expenses:
            if expense.category == category.lower():
                total += expense.amount
        return total

    def get_expense_recommendations(self):
        expenses_dict = [vars(expense) for expense in self.expenses]
        data = pd.DataFrame(expenses_dict)
        if 'date' in data.columns:
            data = data.drop(columns=['date'])
        if 'description' in data.columns:
            data = data.drop(columns=['description'])
        data = pd.get_dummies(data, columns=['category'])
        n_clusters = min(3, len(data))
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(data)
        recommendations = {}
        for i, label in enumerate(kmeans.labels_):
            if label not in recommendations:
                recommendations[label] = []
            recommendations[label].append(self.expenses[i])
        return recommendations

def load_data(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)
    if not os.path.exists(file_path):
        return []
    data = pd.read_excel(file_path).to_dict(orient='records')
    return data

def save_data(file_name, data):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

def get_table_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, index=False)  
    towrite.seek(0)  
    b64 = base64.b64encode(towrite.read()).decode()  
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="expenses.xlsx">Download the expenses file</a>'
    return href

def convert_data_to_text(budget):
    categories_text = f"Categories: {', '.join(budget.categories)}\n"
    expenses_text = "Expenses:\n"
    for expense in budget.expenses:
        expenses_text += f"{expense.date} - {expense.description} - {expense.amount} - {expense.category}\n"
    return categories_text + expenses_text

def translate_text(translation_dict, language):
    for lang in translation_dict:
        for key in translation_dict[lang]:
            # Translate the text based on the selected language
            translated_text = translator.translate(translation_dict[lang][key], dest=language)
            # Update the text in the dictionary
            translation_dict[lang][key] = translated_text.text
    return translation_dict

def main():
    translation = {
        'english': {
            'Personal Finance Manager': 'Personal Finance Manager',
            'Choose an action': 'Choose an action',
            'add': 'add',
            'recommendations': 'recommendations',
            'Groceries': 'Groceries',
            'Entertainment': 'Entertainment',
            'Utilities': 'Utilities',
            'Investments': 'Investments',
            'Total Expenditure: ': 'Total Expenditure',
            'Expenditure': 'Expenditure',
            'Enter date (dd/mm/yyyy): ': 'Enter date (dd/mm/yyyy)',
            'Enter description: ': 'Enter description',
            'Enter amount: ': 'Enter amount',
            'Choose a category': 'Choose a category',
            'Add Expense': 'Add Expense',
            'Expense added successfully.': 'Expense added successfully.',
            'Download the expenses file': 'Download the expenses file',
            'Categories': 'Categories',
            'Expenses': 'Expenses'
        },
        'spanish': {
            'Personal Finance Manager': 'Administrador de Finanzas Personales',
            'Choose an action': 'Elige una acción',
            'add': 'añadir',
            'recommendations': 'recomendaciones',
            'Groceries': 'Comestibles',
            'Entertainment': 'Entretenimiento',
            'Utilities': 'Utilidades',
            'Investments': 'Inversiones',
            'Total Expenditure: ': 'Gasto total',
            'Expenditure': 'Gasto',
            'Enter date (dd/mm/yyyy): ': 'Introduce la fecha (dd/mm/yyyy)',
            'Enter description: ': 'Introduce la descripción',
            'Enter amount: ': 'Introduce la cantidad',
            'Choose a category': 'Elige una categoría',
            'Add Expense': 'Añadir gasto',
            'Expense added successfully.': 'Gasto añadido con éxito.',
            'Download the expenses file': 'Descargar el archivo de gastos',
            'Categories': 'Categorías',
            'Expenses': 'Gastos'
        },
        'french': {
            'Personal Finance Manager' : 'Responsable des finances personnelles',
            'Choose an action' : 'Choisir une action',
            'add': 'ajouter',
            'recommendations': 'recommandations',
            'Groceries': '« Épicerie »',
            'Entertainment': 'Divertissement',
            'Utilities': 'Utilitaires',
            'Investments': 'Investissements',
            'Total Expenditure: ' : '« Dépenses totales »',
            'Expenditure' : 'Dépense',
            'Enter date (dd/mm/yyyy): ' : 'Entrez la date (jj/mm/aaaa)',
            'Enter description: ' : 'Entrez la description',
            'Enter amount: ' : 'Entrer le montant',
            'Choose a category' : 'Choisir une catégorie',
            'Add Expense' : 'Ajouter une dépense',
            'Expense added successfully.': 'Dépense ajoutée avec succès.',
            'Download the expenses file' : 'Télécharger le dossier des dépenses',
            'Categories' : 'Catégories',
            'Expenses' : 'Dépenses'
        },
        'hindi': {
            'Personal Finance Manager': 'व्यक्तिगत वित्त प्रबंधक',
            'Choose an action': 'एक क्रिया चुनें',
            'add': 'जोड़ें',
            'recommendations': 'सिफारिशें',
            'Groceries': 'किराने का सामान',
            'Entertainment': 'मनोरंजन',
            'Utilities': 'उपयोगिताएँ',
            'Investments': 'निवेश',
            'Total Expenditure: ': 'कुल व्यय',
            'Expenditure': 'व्यय',
            'Enter date (dd/mm/yyyy): ': 'दिनांक दर्ज करें (दिनांक/माह/वर्ष)',
            'Enter description: ': 'विवरण दर्ज करें',
            'Enter the amount: ': 'राशि दर्ज करें',
            'Choose a category': 'एक श्रेणी चुनें',
            'Add Expense': 'व्यय जोड़ें',
            'Expense added successfully': 'व्यय सफलतापूर्वक जोड़ा गया।',
            'Download the expenses file': 'व्यय फ़ाइल डाउनलोड करें',
            'Categories': 'श्रेणियाँ',
            'Expenses': 'खर्च'
        },
        # Add more languages as needed
    }
    st.set_page_config(page_title="Personal Finance Manager", page_icon=":receipt:")
    st.markdown("<h1 style='text-align: center;'>Personal Finance Manager</h1>", unsafe_allow_html=True)
    language = st.sidebar.selectbox("Choose a language", ("English", "Spanish", "French", "Hindi")).lower()
    translation = translate_text(translation, language)
    options = ['add', 'recommendations']
    translated_options = [translation[language][option] for option in options]
    action = st.sidebar.selectbox(translation[language]['Choose an action'], translated_options)
    categories = ['Groceries', 'Entertainment', 'Utilities', 'Investments']
    translated_categories = [translation[language][category] for category in categories]
    budget = Budget(translated_categories)
    transactions = load_data("transactions.xlsx")
    for transaction in transactions:
        budget.add_expense(Transaction(**transaction))
    if action == (translation[language]['add']):
        st.write(translation[language]['Total Expenditure: '], budget.get_total_expenditure())
        for category in budget.categories:
            st.write(f"{category} {translation[language]['Expenditure']}:", budget.get_category_expenditure(category))
        date = st.text_input(translation[language]['Enter date (dd/mm/yyyy): '])
        description = st.text_input(translation[language]['Enter description: '])
        amount = st.number_input(translation[language]['Enter amount: '], value=0.0, step=0.01)
        cat_options = ('Groceries', 'Entertainment', 'Utilities', 'Investments')
        translated_cat_options = [translation[language].get(option, option) for option in cat_options]
        category = st.selectbox(translation[language].get('Choose a category', 'Choose a category'), translated_cat_options).lower()
        if st.button(translation[language]['Add Expense']):
            transaction = Transaction(date, description, amount, category)
            budget.add_expense(transaction)
            transactions.append(transaction.__dict__)
            st.success(translation[language]['Expense added successfully.'])
            df = pd.DataFrame(transactions)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)

    elif action == (translation[language]['recommendations']):
        data_text = convert_data_to_text(budget)

        api_key = "wr-BOVjokTARVmFBKmHcFk7Pt"
        url = 'https://api.webraft.in/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "gpt-4",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful expense management assistant."
                },
                {
                    "role": "user",
                    "content": data_text + "\n\nRecommendations:"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        try:
            response_data = response.json()
            bot_response = response_data['choices'][0]['message']['content']

            # Translate the bot's response to the user's language
            translator = Translator()
            translated_response = translator.translate(bot_response, dest=language).text

            st.write(translated_response)
        except requests.exceptions.JSONDecodeError as e:
            st.write("JSON Decode Error:", e)
            st.write("Response Content:", response.content)
            st.write(response.choices[0].text.strip())

if __name__ == "__main__":
    main() 