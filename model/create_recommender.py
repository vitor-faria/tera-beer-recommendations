import pandas as pd
from turicreate import SFrame, item_similarity_recommender


def get_dataset():
    return pd.read_csv('data/dataset.csv')


def get_taste_columns(df):
    return [column for column in df.columns if column.startswith('Alimento')]


def get_beer_columns(df):
    return [column for column in df.columns if column.startswith('Cerveja')]


def melt_user_item_matrix(df):
    taste_columns = get_taste_columns(df)
    beer_columns = get_beer_columns(df)

    melted_df = pd.melt(
        df[taste_columns+beer_columns].reset_index(),
        id_vars=['index'],
        value_vars=taste_columns+beer_columns,
        var_name='product',
        value_name='rating'
    ).dropna()

    return melted_df


def create_recommender_system(melted_df):

    sf_ratings = SFrame(melted_df)

    recommending_system = item_similarity_recommender.create(
        sf_ratings,
        user_id='index',
        item_id='product',
        target='rating',
        similarity_type='pearson'
    )

    recommending_system.save('model/recommending_system')
    print("[INFO] Model was saved in folder 'model/recommending_system/' and it's ready to recommend!")


def main():
    print("[INFO] Loading the data...")
    df = get_dataset()
    print("[INFO] Melting user-item matrix...")
    melted_df = melt_user_item_matrix(df)
    print("[INFO] Creating recommending system...")
    create_recommender_system(melted_df)


if __name__ == "__main__":
    main()
