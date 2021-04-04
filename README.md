# TeraBeer Recommendations

Esse é um projeto desenvolvido ao longo do Bootcamp de Ciência de Dados e Machine Learning da [Tera](https://somostera.com/). Trata-se de 
uma aplicação Python/Streamlit que gera listas de recomendação de cervejas artesanais brasileiras com base no paladar do usuário, e utilizando um sistema 
de recomendação do tipo `ItemSimilarityRecommender` da biblioteca [Turi Create](https://apple.github.io/turicreate/docs/api/index.html).

## Ambiente de desenvolvimento

Para criar o ambiente de desenvolvimento, é recomendado utilizar o [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

Utilize os comandos a seguir para deixar o ambiente pronto para desenvolver

```
conda create -n ENVIRONMENT_NAME python=3.6
conda activate ENVIRONMENT_NAME
pip install -r requirements.txt
```

Será necessário configurar as seguintes variáveis de ambiente:
```
export FROM_EMAIL=[EMAIL]
export EMAIL_PASSWORD=[PASSWORD]
export DB_URL=[DB_URL]
```

Para ter acesso ao banco de dados (`DB_URL`), solicite acesso à Equipe TeraBeer.

> Importante: para usar contas do Gmail no envio de e-mails, é necessário autorizar 
> o uso de apps menos seguros nas configurações da Conta Google.

### Recriação do modelo

Para recriar/retreinar o sistema de recomendação com novos dados, execute o script

```
python data/create_recommender.py
```

Esse script executará uma consulta no banco de dados da aplicação e usará os dados para 
recriar o sistema de recomendação, que será salvo em 4 arquivos na pasta `data/recommending_system`.

### Execução local

Para executar a aplicação streamlit em servidor local, utilize o comando

```
streamlit run app.py
```

## URL da Aplicação

Produção: https://terabeer-recomendacoes.herokuapp.com/

A aplicação possui os arquivos `setup.sh` e `Procfile` para facilitar o deploy de uma branch no Heroku pela GUI.

> Importante: para que a aplicação funcione adequadamente em produção, as mesmas variáveis de ambiente 
> precisam ser devidamente configuradas.
