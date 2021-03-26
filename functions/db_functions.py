import pandas as pd
import sqlalchemy
from os import environ as env


def send_answers_to_db(email, recommendations, df_paladar, accept_beer_offers, allow_data_usage):
    db_url = env["DB_URL"]
    engine = sqlalchemy.create_engine(db_url)
    df = _build_record_df(email, recommendations, df_paladar, accept_beer_offers, allow_data_usage)
    df.to_sql(
        name='user_recommendations',
        con=engine,
        if_exists='append',
        index=False,
        dtype={
            'tastes': sqlalchemy.types.JSON,
            'beers': sqlalchemy.types.JSON,
            'recommendations': sqlalchemy.types.JSON
        }
    )


def _build_record_df(email, recommendations, df_paladar, accept_beer_offers, allow_data_usage):
    taste_columns = [column for column in df_paladar.columns if column.startswith('Alimento')]
    beer_columns = [column for column in df_paladar.columns if column.startswith('Cerveja')]

    tastes = {}
    for column in taste_columns:
        value = df_paladar.loc[-1, column]
        if value >= 0:
            tastes[column] = float(value)

    beers = {}
    for column in beer_columns:
        value = df_paladar.loc[-1, column]
        if value >= 0:
            beers[column] = float(value)

    recommendations.drop(columns=['index'], inplace=True)
    recommendations_dict = recommendations.astype({'score': float, "rank": int}).to_dict('records')
    print(recommendations_dict)

    df = pd.DataFrame({
        "email": [email],
        "tastes": [tastes],
        "beers": [beers],
        "origin": ["App"],
        "accept_beer_offers": [accept_beer_offers],
        "allow_data_usage": [allow_data_usage],
        "recommendations": [recommendations_dict],
        "created_at": ["NOW()"],
        "updated_at": ["NOW()"]
    })
    print(df)

    return df
