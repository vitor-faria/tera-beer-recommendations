import numpy as np
import pandas as pd


raw_dataset = pd.read_excel('data/raw_dataset.xlsx')

rename_column_dict = {
    "Carimbo de data/hora": "Timestamp",
    "Qual a sua opinião sobre os alimentos abaixo? [Chocolate 70% cacau]": "Alimento Chocolate amargo",
    "Qual a sua opinião sobre os alimentos abaixo? [Beringela]": "Alimento Beringela",
    "Qual a sua opinião sobre os alimentos abaixo? [Rúcula/escarola/espinafre]": "Alimento Folhas escuras",
    "Qual a sua opinião sobre os alimentos abaixo? [Mel]": "Alimento Mel",
    "Qual a sua opinião sobre os alimentos abaixo? [Chocolate ao leite]": "Alimento Chocolate ao leite",
    "Qual a sua opinião sobre os alimentos abaixo? [Oreo/cookies n' cream]": "Alimento Oreo",
    "Qual a sua opinião sobre os alimentos abaixo? [Ruffles/salgadinho]": "Alimento Salgadinho",
    "Qual a sua opinião sobre os alimentos abaixo? [Tomate/ketchup]": "Alimento Tomate",
    "Qual a sua opinião sobre os alimentos abaixo? [Margherita]": "Alimento Margherita",
    "Qual a sua opinião sobre os alimentos abaixo? [Limonada/caipirinha]": "Alimento Limonada",
    "Qual a sua opinião sobre os alimentos abaixo? [Suco de laranja]": "Alimento Laranja",
    "Qual a sua opinião sobre os alimentos abaixo? [Suco de maracujá]": "Alimento Maracujá",
    "Qual a sua opinião sobre os alimentos abaixo? [Mexerica/tangerina]": "Alimento Tangerina",
    "Qual a sua opinião sobre os alimentos abaixo? [Pimentas/especiarias ]": "Alimento Pimentas",
    "Qual a sua opinião sobre os alimentos abaixo? [Cravo]": "Alimento Cravo",
    "Qual a sua opinião sobre os alimentos abaixo? [Banana]": "Alimento Banana",
    "Qual a sua opinião sobre os alimentos abaixo? [Gengibre]": "Alimento Gengibre",
    "Qual a sua opinião sobre os alimentos abaixo? [Canela]": "Alimento Canela",
    "Qual a sua opinião sobre os alimentos abaixo? [Bacon/lombo defumado]": "Alimento Bacon",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Pilsen/Lager]": "Cerveja Pilsen",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Golden Ale/Blonde Ale]": "Cerveja Blonde",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Trigo (Weiss)]": "Cerveja Trigo",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [American Pale Ale (APA)]": "Cerveja APA",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [India Pale Ale (IPA)]": "Cerveja IPA",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Session IPA]": "Cerveja Session IPA",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [New England IPA/Juicy IPA]": "Cerveja NEIPA",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Porter/Stout]": "Cerveja Porter",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Dunkel/Malzbier]": "Cerveja Malzbier",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Witbier]": "Cerveja Witbier",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Fruit Beer/Sour]": "Cerveja Sour",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Russian Imperial Stout/Pastry Stout]": "Cerveja RIS",
    "Você tem vontade de experimentar novos estilos de cerveja além dos que já conhece?": "Vontade experimentar",
    "Você experimentaria um novo estilo de cerveja que lhe fosse recomendado com base no seu paladar? ": "Experimentaria recomendação",
    "Como ficou sabendo deste questionário? (Opcional)": "Como ficou sabendo",
    "Deseja se identificar? Deixe seu e-mail. (Opcional)": "Email",
    "Qual a sua opinião sobre os alimentos abaixo? [Café sem açúcar]": "Alimento Café",
    "Qual a sua opinião sobre os seguintes estilos de cerveja? [Lambic]": "Cerveja Lambic",
}

df = raw_dataset.rename(columns=rename_column_dict).drop(index=[0, 1]).sort_index(axis=1)

df.drop(columns=[  # Remover colunas criadas sem querer ou removidas antes do disparo da pesquisa
    "Você gosta de cerveja?",
    "Por que você não gosta de cerveja?",
    "Qual a sua opinião sobre as comidas e bebidas abaixo? (DOCE, SALGADO, AZEDO, AMARGO, CONDIMENTOS) [Leite condensado]",
    "Qual a sua opinião sobre as comidas e bebidas abaixo? (DOCE, SALGADO, AZEDO, AMARGO, CONDIMENTOS) [Baunilha]",
    "Qual a sua opinião sobre as comidas e bebidas abaixo? (DOCE, SALGADO, AZEDO, AMARGO, CONDIMENTOS) [Abóbora]",
    "Unnamed: 43"
], inplace=True)

taste_columns = [column for column in df.columns if column.startswith('Alimento')]
beer_columns = [column for column in df.columns if column.startswith('Cerveja')]
df.dropna(subset=taste_columns + beer_columns, inplace=True)

preference_map = {
    "Gosto": 1,
    "Não gosto": 0,
    "Indiferente": 0.5,
    "Desconheço": np.nan
}

df.replace(preference_map, inplace=True)

# paladar_map = {
#     'Paladar Doce': [
#         'Alimento Banana',
#         'Alimento Chocolate ao leite',
#         'Alimento Mel',
#         'Alimento Oreo'
#     ],
#     'Paladar Amargo': [
#         'Alimento Beringela',
#         'Alimento Café',
#         'Alimento Folhas escuras',
#         'Alimento Chocolate amargo'
#     ],
#     'Paladar Salgado': [
#         'Alimento Bacon',
#         'Alimento Margherita',
#         'Alimento Salgadinho',
#         'Alimento Tomate'
#     ],
#     'Paladar Cítrico': [
#         'Alimento Laranja',
#         'Alimento Limonada',
#         'Alimento Maracujá',
#         'Alimento Tangerina'
#     ],
#     'Paladar Especiarias': [
#         'Alimento Canela',
#         'Alimento Cravo',
#         'Alimento Gengibre',
#         'Alimento Pimentas'
#     ]
# }
#
# for paladar, alimentos in paladar_map.items():
#     df[paladar] = df[alimentos].mean(axis=1)

df.to_csv('data/dataset.csv')
