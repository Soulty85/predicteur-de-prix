import streamlit as st
import pickle
import pandas as pd
# Chargement du modele
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

# chargement du scaler
with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)
    
# Fonction pour predire les prix
def predict_price(features):
    prediction = model.predict([features])
    return prediction[0]

# Fonction pour extraire les valeurs de stockage
def extract_storage(memory_str, storage_type):
    total = 0
    for option in memory_str:
        if storage_type in option:
            total += int(option.split(storage_type)[0].split('+')[-1].replace('GB', '').replace('TB', '000'))
    return total

storage_options = ['128GB SSD', '256GB SSD', '512GB SSD', '1TB SSD', '128GB HDD', '256GB HDD', '512GB HDD', '1TB HDD', '128GB Flash Storage', '256GB Flash Storage', '512GB Flash Storage', '1TB Flash Storage', 'Hybrid Storage (SSD + HDD)']

# Interface Streamlit
st.title("Prédiction des Prix des Ordinateurs Portables 💻")
st.write("Remplissez les caractéristiques de l'ordinateur pour prédire son prix.")

# Entrees utilisateur
company = st.selectbox('Marque', ['Razer', 'LG', 'MSI', 'Google', 'Microsoft', 'Apple', 'Huawei', 'Samsung', 'Toshiba', 'Dell', 'Xiaomi', 'Asus', 'Lenovo', 'HP', 'Fujitsu', 'Acer', 'Chuwi', 'Mediacom', 'Vero'])
typename = st.selectbox('Type', ['Ultrabook', 'Notebook', 'Gaming', '2 in 1 Convertible', 'Workstation', 'Netbook'])
screen_resolution = st.selectbox('Résolution d\'écran', ["2560x1600", "1440x900", "1920x1080", "2880x1800", "1366x768", "2304x1440", "3200x1800", "1920x1200", "2256x1504", "3840x2160", "2160x1440", "2560x1440", "2736x1824", "2400x1600", "1600x900"])
ram = st.selectbox('Mémoire RAM (GB)', [4, 8, 16, 32, 64])
memory = st.multiselect('Sélectionne les options de stockage', storage_options, default=['256GB SSD', '1TB HDD'])
cpu = st.selectbox('Processeur', ['Intel', 'AMD', 'Samsung'])
gpu = st.selectbox('Carte Graphique', ['Intel', 'AMD', 'Nvidia', 'ARM'])
os = st.selectbox('Système d\'exploitation', ['Windows', 'MacOS', 'Linux', 'No OS', 'Chrome OS'])
weight = st.number_input('Poids (en kg)', min_value=0.5, max_value=5.0, value=2.0)

# Preparation des donneees
# Resolution de l'ecran
screen_width = int(screen_resolution.split('x')[0])
screen_height = int(screen_resolution.split('x')[1])

# Extraction des types de stockage
ssd = extract_storage(memory, 'SSD')
hdd = extract_storage(memory, 'HDD')
flash_storage = extract_storage(memory, 'Flash Storage')
hybrid = extract_storage(memory, 'Hybrid')

# Encodage label pour Cpu et Gpu
cpu_labels = ['Intel', 'AMD', 'Samsung']
gpu_labels = ['Intel', 'AMD', 'Nvidia', 'ARM']

cpu_encoded = cpu_labels.index(cpu)
gpu_encoded = gpu_labels.index(gpu)

# Encodage One-Hot pour les variables catégoriques
data = {
    'Weight': weight,
    'Ram': ram,
    'screen_width': screen_width,
    'screen_height': screen_height,
    'SSD': ssd,
    'HDD': hdd,
    'Flash Storage': flash_storage,
    'Hybrid': hybrid,
    'cpu': cpu_encoded,
    'gpu': gpu_encoded,
}

user_inputs = {
    'company': company,
    'typename': typename,
    'cpu': cpu,
    'gpu': gpu,
    'opsys': os
}

# One-hot encoding pour Company, TypeName, OpSys
categories = {
    'Company': ['Razer', 'LG', 'MSI', 'Google', 'Microsoft', 'Apple', 'Huawei', 'Samsung', 'Toshiba','Dell', 'Xiaomi', 'Asus', 'Lenovo', 'HP', 'Fujitsu', 'Acer', 'Chuwi', 'Mediacom', 'Vero'],
    'TypeName': ['Ultrabook', 'Notebook', 'Gaming', '2 in 1 Convertible', 'Workstation', 'Netbook'],
    'OpSys': ['Windows', 'MacOS', 'Linux', 'No OS', 'Chrome OS']
}

# Ajout des colonnes One-Hot
for col, options in categories.items():
    for option in options:
        data[f"{option}"] = 1 if user_inputs[col.lower()] == option else 0

# Conversion des données au bon format
input_features = []
for feature in model.feature_names_in_:
    input_features.append(data.get(feature, 0))
    

features_numeriques = ['Ram', 'Weight', 'screen_width', 'screen_height']


# Convertir les données en DataFrame avec les mêmes noms de colonnes
data_df = pd.DataFrame([data], columns=features_numeriques)

# Appliquer la transformation
data_scaled = scaler.transform(data_df)

# Mettre à jour les valeurs dans le dictionnaire original
for i, feature in enumerate(features_numeriques):
    data[feature] = data_scaled[0][i]

# Bouton de prediction  
if st.button('Prédire le Prix'):
    price = predict_price(input_features)
    st.success(f"Prix prédit : {price:.2f} Franc CFA")
