from data.build_dataset import preference_map
from functions.db_functions import send_answers_to_db
from functions.email_functions import send_mail
from model.create_recommender import get_beer_columns, melt_user_item_matrix
import pandas as pd
import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from time import sleep
from turicreate import load_model, SFrame


pd.options.mode.chained_assignment = None
st.set_page_config(layout="wide")


def main():
    state = _get_state()
    pages = {
        "Pesquisa": display_pesquisa,
        "Sugestões": display_sugestoes,
    }

    st.sidebar.title("TeraBeer Recommendations :beer:")
    st.sidebar.markdown("Recomendações de cerveja artesanal brasileiras baseadas no seu paladar e com uso de IA.")
    page = st.sidebar.selectbox(
        "Preencha a pesquisa e veja as cervejas recomendadas na aba Sugestões",
        tuple(pages.keys())
    )

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


@st.cache
def get_beer_list():
    return pd.read_csv('data/beer_list.csv', sep=';')


def display_pesquisa(state):

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.markdown(
        '<style>div[role="radiogroup"] >  :first-child{display: none !important;}</style>',
        unsafe_allow_html=True
    )

    st.title(':pencil: Pesquisa')
    st.markdown('Responda as perguntas a seguir a respeito do seu paladar e preferências de cerveja.')

    options = ['', 'Gosto', 'Não gosto', 'Indiferente', 'Desconheço']

    st.text("")
    st.markdown(
        '''
        ### Parte 1: Qual a sua opinião sobre os alimentos abaixo?

        Para opções com mais de um alimento, caso goste de pelo menos um, escolha a opção "Gosto".
        '''
    )

    taste_questions = {  # Key must match column names used in training, value is displayed in forms
        'Alimento Chocolate amargo': 'Chocolate 70% cacau',
        'Alimento Beringela': 'Beringela',
        'Alimento Folhas escuras': 'Rúcula/escarola/espinafre',
        'Alimento Mel': 'Mel',
        'Alimento Chocolate ao leite': 'Chocolate ao leite',
        'Alimento Oreo': 'Oreo/cookies',
        'Alimento Salgadinho': 'Ruffles/salgadinho',
        'Alimento Tomate': 'Tomate/ketchup',
        'Alimento Margherita': 'Margherita',
        'Alimento Limonada': 'Limonada',
        'Alimento Laranja': 'Suco de laranja',
        'Alimento Maracujá': 'Suco de maracujá',
        'Alimento Tangerina': 'Mexerica/tangerina',
        'Alimento Pimentas': 'Pimentas/especiarias',
        'Alimento Cravo': 'Cravo',
        'Alimento Banana': 'Banana',
        'Alimento Gengibre': 'Gengibre',
        'Alimento Canela': 'Canela',
        'Alimento Bacon': 'Bacon/lombo defumado',
        'Alimento Café': 'Café sem açúcar'
    }

    feat_paladar = {}
    for feature_name, question in taste_questions.items():
        feat_paladar[feature_name] = st.radio(question, options, index=1)
        st.text("")

    st.markdown('### Parte 2: Qual a sua opinião sobre os seguintes estilos de cerveja?')

    beer_questions = {
        'Cerveja Pilsen': 'Pilsen/Lager',
        'Cerveja Blonde': 'Golden Ale/Blonde Ale',
        'Cerveja Trigo': 'Trigo (Weiss)',
        'Cerveja APA': 'American Pale Ale (APA)',
        'Cerveja IPA': 'India Pale Ale (IPA)',
        'Cerveja Session IPA': 'Session IPA',
        'Cerveja NEIPA': 'New England IPA/Juice IPA',
        'Cerveja Porter': 'Porter/Stout',
        'Cerveja Malzbier': 'Dunkel/Malzbier',
        'Cerveja Witbier': 'Witbier',
        'Cerveja Sour': 'Fruit Beer/Sour',
        'Cerveja RIS': 'Russian Imperial Stout/Pastry Stout',
        'Cerveja Lambic': 'Lambic'
    }

    for feature_name, question in beer_questions.items():
        feat_paladar[feature_name] = st.radio(question, options, index=4)
        st.text("")

    exclude_known = st.checkbox('Desejo receber recomendações somente de estilos que eu não conheço', True)

    df_paladar = pd.DataFrame([feat_paladar], index=[-1])
    df_paladar.replace(preference_map, inplace=True)
    new_observation_data = melt_user_item_matrix(df_paladar)
    # st.dataframe(new_observation_data)
    recommendable_beers = get_beer_columns(df_paladar)
    recommendable_beers.remove('Cerveja Pilsen')

    if st.button('Gerar recomendações'):
        model = load_model('model/recommending_system')
        recommendations = model.recommend(
            users=[-1],
            k=3,
            items=recommendable_beers,
            new_observation_data=SFrame(new_observation_data),
            exclude_known=exclude_known,
        ).to_dataframe()

        st.dataframe(recommendations)
        st.success('Pronto! Confira a página Sugestões do menu à esquerda')
        sleep(3)
        state.recommendations, state.paladar = recommendations, df_paladar


def display_sugestoes(state):

    st.title(':beer: Sugestões')

    recommendations, df_paladar = state.recommendations, state.paladar

    # st.dataframe(df_paladar)
    # st.dataframe(recommendations)

    rename_beer_styles = {
        'Cerveja Blonde': 'Blonde Ale',
        'Cerveja Trigo': 'Trigo - Weissbier',
        'Cerveja APA': 'American Pale Ale',
        'Cerveja IPA': 'India Pale Ale',
        'Cerveja Session IPA': 'Session IPA',
        'Cerveja NEIPA': 'New England IPA',
        'Cerveja Porter': 'Porter/Stout',
        'Cerveja Malzbier': 'Malzbier',
        'Cerveja Witbier': 'Witbier',
        'Cerveja Sour': 'Sour/Fruit',
        'Cerveja RIS': 'Russian Imperial Stout',
        'Cerveja Lambic': 'Lambic'
    }

    recommendations.replace({'product': rename_beer_styles}, inplace=True)

    df_cervejas = get_beer_list()
    recommended_labels = pd.merge(recommendations, df_cervejas, left_on='product', right_on='estilo')
    recommended_labels.sort_values(by=['score', 'media'], ascending=[False, False])
    # st.dataframe(recommended_labels)

    df_style_1 = recommended_labels[recommended_labels['rank'] == 1]
    df_style_2 = recommended_labels[recommended_labels['rank'] == 2]
    df_style_3 = recommended_labels[recommended_labels['rank'] == 3]

    markdown_list = []
    image_list = []
    for df_style in [df_style_1, df_style_2, df_style_3]:
        if not df_style.empty:
            df_style.reset_index(drop=True, inplace=True)
            style_name = df_style['estilo'][0]
            style_rank = df_style['rank'][0]
            style_score = df_style['score'][0]
            style_description = df_style['descricao'][0]

            style_markdown = f"""
            <div>
                <br>
                <h2>
                    Estilo {style_rank}: <b>{style_name}</b> ({style_score:.1%} recomendado para você)
                </h2>
                <br>
                <p>
                    {style_description}
                </p>
                <br>
            </div>
            """
            st.markdown(style_markdown, unsafe_allow_html=True)
            markdown_list.append(style_markdown)

            for index, row in df_style.iterrows():
                beer = row['cerveja']
                brewery = row['cervejaria']
                abv = row['abv']
                ibu = row['ibu']
                avg_rating = row['media']
                count_ratings = int(row['ratings'])
                figure = row['figura ']

                column1, column2 = st.beta_columns((1, 4))

                with column1:
                    try:
                        st.image(f'fig/{figure}', use_column_width=True)
                        image_list.append(f'fig/{figure}')
                        markdown_list.append(
                            f"""
                            <br>
                            <div>
                                <img
                                    src="cid:image{len(image_list)}"
                                    alt="Logo"
                                    style="width:200px;height:200px;">
                            </div>
                            """
                        )

                    except FileNotFoundError:
                        st.image('fig/placeholder-image.jpg', use_column_width=True)
                        image_list.append('fig/placeholder-image.jpg')
                        markdown_list.append(
                            f"""
                            <br>
                            <div>
                                <img
                                    src="cid:image{len(image_list)}"
                                    alt="Logo"
                                    style="width:200px;height:200px;">
                            </div>
                            """
                        )

                with column2:
                    beer_markdown = f"""
                    <div>
                        <h3>{beer} - {brewery}</h3>
                        <p>
                            <b>Nota média</b>: {avg_rating:.3} ({count_ratings} avaliações) <br>
                            <b>ABV</b>: {abv}% álcool <br>
                            <b>IBU</b>: {ibu} unidades de amargor
                        </p>
                    </div>
                    """
                    st.markdown(beer_markdown, unsafe_allow_html=True)
                    markdown_list.append(beer_markdown)

    email = st.text_input('Para receber as sugestões, deixe seu email e aperte Enter:')
    if email:
        accept_beer_offers = st.checkbox(
            'Aceito receber por e-mail ofertas especiais de cervejas com base nas minhas respostas',
            True
        )
        allow_data_usage = st.checkbox(
            'Permito que utilizem minhas respostas para melhorar recomendações futuras',
            True
        )

        if st.button('Enviar recomendações por email'):
            send_mail(email, markdown_list, image_list)
            st.success('Pronto! Confira no seu inbox e, se não encontrar, dá uma olhada na caixa de spam.')

            if accept_beer_offers or allow_data_usage:
                send_answers_to_db(
                    email=email,
                    recommendations=recommendations,
                    df_paladar=df_paladar,
                    accept_beer_offers=accept_beer_offers,
                    allow_data_usage=allow_data_usage,
                )


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()
