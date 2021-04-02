from data.db_functions import DBFunctions
from functions.email_functions import send_mail
from data.create_recommender import get_beer_columns, melt_user_item_matrix
import numpy as np
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
        "Recomendações": display_sugestoes,
    }

    st.sidebar.title(":bookmark_tabs: MENU")
    page = st.sidebar.selectbox(
        "",
        tuple(pages.keys())
    )

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


@st.cache
def get_beer_list():
    db = DBFunctions()
    return db.get_df_from_query('beer_list')


def display_pesquisa(state):
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.markdown(
        '<style>div[role="radiogroup"] >  :first-child{display: none !important;}</style>',
        unsafe_allow_html=True
    )
    st.image('fig/terabeer_banner.jpeg')

    # st.title(':beer: TERABEER')
    st.markdown('''
    ## Olá, que bom que você veio!
    
    O TeraBeer é um sistema de recomendação de cervejas artesanais brasileiras baseado no seu paladar, 
    que utiliza Inteligência Artificial.
    
    Antes de mais nada, confirme que você tem mais de 18 anos:
    ''')

    if st.checkbox('Sim, tenho mais de 18 anos, internet!', False):
        st.text("")
        st.markdown("![Sei...](https://media.giphy.com/media/VhLc1Mb9HlPo2Jo2ZG/giphy.gif)")
        st.text("")
        st.markdown('''
        ## :pencil: **PESQUISA**
        
        Agora responda as duas perguntas a seguir para gerar as suas recomendações.
        ''')

        options = ['', 'Gosto', 'Não gosto', 'Indiferente', 'Desconheço']

        st.markdown('''
            ### QUAL A SUA OPINIÃO SOBRE OS **ALIMENTOS E BEBIDAS** ABAIXO?
        ''')
        st.text("")

        taste_questions = {  # Key must match column names used in training, value is displayed in forms
            'Alimento Chocolate amargo': 'Chocolate 70% cacau',
            'Alimento Beringela': 'Beringela',
            'Alimento Folhas escuras': 'Folhas escuras',
            'Alimento Mel': 'Mel',
            'Alimento Chocolate ao leite': 'Chocolate ao leite',
            'Alimento Oreo': "Cookies & Cream",
            'Alimento Salgadinho': 'Batata chips',
            'Alimento Tomate': 'Tomate',
            'Alimento Margherita': 'Margarita',
            'Alimento Limonada': 'Limonada',
            'Alimento Laranja': 'Laranja',
            'Alimento Maracujá': 'Maracujá',
            'Alimento Tangerina': 'Mexerica/tangerina',
            'Alimento Pimentas': 'Pimenta',
            'Alimento Cravo': 'Cravo',
            'Alimento Banana': 'Banana',
            'Alimento Gengibre': 'Gengibre',
            'Alimento Canela': 'Canela',
            'Alimento Bacon': 'Bacon',
            'Alimento Café': 'Café sem açúcar'
        }

        feat_paladar = {}
        for feature_name, question in taste_questions.items():
            feat_paladar[feature_name] = st.radio(question, options, index=1)
            st.text("")

        st.markdown('### QUAL A SUA OPINIÃO SOBRE OS SEGUINTES **ESTILOS DE CERVEJA**?')
        st.text("")

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

        st.text("")
        exclude_known = st.checkbox('Desejo receber recomendações somente de estilos que eu não conheço', True)

        preference_map = {
            "Gosto": 1,
            "Não gosto": 0,
            "Indiferente": 0.5,
            "Desconheço": np.nan
        }
        df_paladar = pd.DataFrame([feat_paladar], index=[-1])
        df_paladar.replace(preference_map, inplace=True)
        melt_df = melt_user_item_matrix(df_paladar)
        new_observation_data = melt_df
        # st.dataframe(new_observation_data)
        recommendable_beers = get_beer_columns(df_paladar)
        recommendable_beers.remove('Cerveja Pilsen')
        if not exclude_known:  # Exclude beers user already don't like
            dislike_beers = melt_df[melt_df['rating'] < 1]['product'].to_list()
            for dislike_beer in dislike_beers:
                if dislike_beer in recommendable_beers:
                    recommendable_beers.remove(dislike_beer)

        st.text("")
        st.text("")
        st.text("")
        if st.button('Gerar recomendações'):
            model = load_model('data/recommending_system')
            if len(recommendable_beers) == 0:
                st.error('Não temos nenhuma cerveja para te recomendar :/')
            else:
                with st.spinner(text='Aguarde um instante enquanto analisamos as suas respostas...'):
                    sleep(4)
                    recommendations = model.recommend(
                        users=[-1],
                        k=3,
                        items=recommendable_beers,
                        new_observation_data=SFrame(new_observation_data),
                        exclude_known=exclude_known,
                    ).to_dataframe()

                # st.dataframe(recommendations)
                if recommendations.empty and exclude_known:
                    st.error('Você conhece muitas cervejas ein?! Que tal desmarcar a caixa acima?')
                else:
                    st.success('Pronto! Selecione no menu à esquerda a página Recomendações.')
                    sleep(3)
                    state.recommendations, state.paladar = recommendations, df_paladar


def display_sugestoes(state):

    st.title(':beers: CERVEJAS RECOMENDADAS')
    st.markdown('''
    Estas são as cervejas artesanais brasileiras **mais recomendadas para você**. 
    Ao final, você poderá enviar a lista de cervejas para o seu e-mail.
    ''')

    recommendations, df_paladar = state.recommendations, state.paladar

    # st.dataframe(df_paladar)
    # st.dataframe(recommendations)

    rename_beer_styles = {
        'Cerveja Blonde': 'Blonde Ale',
        'Cerveja Trigo': 'Weiss (Trigo)',
        'Cerveja APA': 'American Pale Ale',
        'Cerveja IPA': 'India Pale Ale',
        'Cerveja Session IPA': 'Session IPA',
        'Cerveja NEIPA': 'New England IPA',
        'Cerveja Porter': 'Porter/Stout',
        'Cerveja Malzbier': 'Dunkel/Malzbier',
        'Cerveja Witbier': 'Witbier',
        'Cerveja Sour': 'Sour/Fruit',
        'Cerveja RIS': 'Russian Imperial Stout',
        'Cerveja Lambic': 'Lambic'
    }

    if not isinstance(recommendations, pd.DataFrame):
        st.error('Sua sessão expirou, responda novamente o formulário para ver as suas recomendações.')

    else:
        recommendations.replace({'product': rename_beer_styles}, inplace=True)

        df_cervejas = get_beer_list()
        recommended_labels = pd.merge(recommendations, df_cervejas, left_on='product', right_on='terabeer_style')
        recommended_labels.sort_values(by=['score', 'ratings_avg'], ascending=[False, False])
        # st.dataframe(recommended_labels)
        origins = recommended_labels['origin_state'].unique().tolist()
        origin_filter = st.multiselect("Filtrar por estado:", origins, default=origins)
        filtered_labels = recommended_labels[recommended_labels['origin_state'].isin(origin_filter)]

        df_style_1 = filtered_labels[filtered_labels['rank'] == 1]
        df_style_2 = filtered_labels[filtered_labels['rank'] == 2]
        df_style_3 = filtered_labels[filtered_labels['rank'] == 3]

        markdown_list = []
        image_list = []
        for df_style in [df_style_1, df_style_2, df_style_3]:
            if not df_style.empty:
                df_style.reset_index(drop=True, inplace=True)
                style_name = df_style['terabeer_style'][0]
                style_rank = df_style['rank'][0]
                style_score = df_style['score'][0]
                style_description = df_style['style_description'][0]
                style_harmonization = df_style['harmonization'][0]
                if style_harmonization:
                    harmonization_line = f'<br><br> <b>Harmoniza bem com</b>: {style_harmonization}'
                else:
                    harmonization_line = ''

                style_markdown = f"""
                <div>
                    <br>
                    <h2>
                        Estilo {style_rank}: <b>{style_name}</b> ({style_score:.1%} recomendado para você)
                    </h2>
                    <br>
                    <p>
                        <b>Descrição</b>: {style_description} {harmonization_line}
                    </p>
                    <br>
                </div>
                """
                st.markdown(style_markdown, unsafe_allow_html=True)
                markdown_list.append(style_markdown)

                for index, row in df_style.iterrows():
                    beer = row['name']
                    brewery = row['brand']
                    abv = row['abv']
                    ibu = row['ibu']
                    avg_rating = row['ratings_avg']
                    count_ratings = int(row['ratings_count'])
                    figure = row['figure']
                    ratings_source = row['ratings_source']
                    ratings_url = row['ratings_url']
                    origin_state = row['origin_state']
                    offer_url = row['offer_url']

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
                        ratings_source_url = f'<a href="{ratings_url}" target="_blank">{ratings_source}</a>'
                        ratings_line = f'{avg_rating:.3} ({count_ratings} avaliações no {ratings_source_url})'
                        ibu_line = f'{int(ibu)} unidades de amargor' if ibu > 0 else 'Indisponível'
                        offer_line = f'<b><a href="{offer_url}" target="_blank">Quero!</a></b>'
                        beer_markdown = f"""
                        <div>
                            <h3>{beer} - {brewery}</h3>
                            <p>
                                <b>Origem</b>: {origin_state}<br>
                                <b>Nota média</b>: {ratings_line}<br>
                                <b>ABV</b>: {abv}% álcool <br>
                                <b>IBU</b>: {ibu_line} <br>
                                {offer_line}
                            </p>
                        </div>
                        """
                        st.markdown(beer_markdown, unsafe_allow_html=True)
                        markdown_list.append(beer_markdown)

        st.text("")
        st.text("")
        st.markdown("### :mailbox: Para receber a lista acima no seu e-mail, digite-o abaixo e aperte enter:")
        email = st.text_input('')
        if email:
            st.markdown("### Qual seu nome?")
            name = st.text_input(' ')
            accept_beer_offers = st.checkbox(
                'Aceito receber novidades do TeraBeer.',
                True
            )
            allow_data_usage = st.checkbox(
                'Permito que utilizem minhas respostas para melhorar recomendações futuras.',
                True
            )
            st.text("")

            if st.button('Enviar recomendações por email'):
                with st.spinner(text='Enviando...'):
                    send_mail(email, name, markdown_list, image_list)

                st.success('Enviado! Confira sua caixa de entrada e lixo eletrônico.')

                if accept_beer_offers or allow_data_usage:
                    db = DBFunctions()
                    try:
                        db.send_answers_to_db(
                            email=email,
                            name=name,
                            recommendations=recommendations,
                            df_paladar=df_paladar,
                            accept_beer_offers=accept_beer_offers,
                            allow_data_usage=allow_data_usage,
                        )
                    except KeyError:
                        pass


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
