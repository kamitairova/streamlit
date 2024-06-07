import streamlit as st
import pandas as pd
import io
import plotly.express as px
import altair as alt

st.set_page_config(page_title='Movie Filter Application', page_icon='🍿')
st.title('🍿 Movie Filter Application')

df = pd.read_csv('f.csv')

if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = df.copy()

def filter_data(selected_years, selected_genres, selected_director, selected_actor, min_rating):
    filtered_df = st.session_state.filtered_df.copy()

    if selected_years:
        filtered_df = filtered_df[filtered_df['title_year'].notna()]  # Remove rows with NaN in 'title_year'
        filtered_df['title_year'] = filtered_df['title_year'].astype(int)  # Convert to int
        filtered_df = filtered_df[(filtered_df['title_year'] >= selected_years[0]) & (filtered_df['title_year'] <= selected_years[1])]

    if selected_genres:
        selected_genres = [genre.strip() for selected_genre in selected_genres for genre in selected_genre.split('|')]
        filtered_df = filtered_df[filtered_df['genres'].apply(lambda genres: any(genre in genres for genre in selected_genres))]

    if selected_director:
        filtered_df = filtered_df[filtered_df['director_name'] == selected_director]

    if selected_actor:
        filtered_df = filtered_df[filtered_df['actor_1_name'] == selected_actor]  

    if min_rating is not None:
        filtered_df = filtered_df[filtered_df['imdb_score'] >= min_rating]  

    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df

st.sidebar.header('Filters')

min_year, max_year = df['title_year'].dropna().astype(int).min(), df['title_year'].dropna().astype(int).max()
selected_years = st.sidebar.slider('Select Years', min_year, max_year, (min_year, max_year))

genres = df['genres'].str.split('|').explode().unique()
selected_genres = st.sidebar.multiselect('Select Genres', genres, default=genres)

directors = ['All'] + df['director_name'].unique().tolist()
selected_director = st.sidebar.selectbox('Select Director', directors)

if selected_director == 'All':
    selected_director = None

actors = ['All'] + df['actor_1_name'].unique().tolist()
selected_actor = st.sidebar.selectbox('Select Main Role', actors)

if selected_actor == 'All':
    selected_actor = None

min_rating = st.sidebar.slider('Select Minimum Rating', 0.0, 10.0, 8.0, 0.1)

st.session_state.filtered_df = filter_data(selected_years, selected_genres, selected_director, selected_actor, min_rating)

st.sidebar.header('Modify Data')

if st.sidebar.button("Remove Duplicates"):
    st.session_state.filtered_df = st.session_state.filtered_df.drop_duplicates()
    st.sidebar.write("Duplicates removed.")

if st.sidebar.button("Remove Empty Values"):
    st.session_state.filtered_df = st.session_state.filtered_df.dropna()
    st.sidebar.write("Empty values removed.")

value_to_replace = st.sidebar.text_input("Enter the value to replace empty cells with:")
if st.sidebar.button("Replace Empty Values"):
    if value_to_replace:
        st.session_state.filtered_df = st.session_state.filtered_df.fillna(value_to_replace)
        st.sidebar.write("Empty values replaced.")

st.dataframe(st.session_state.filtered_df)

if 'show_info' not in st.session_state:
    st.session_state.show_info = False
if 'show_description' not in st.session_state:
    st.session_state.show_description = False

col1, col2 = st.columns(2)

def toggle_info():
    st.session_state.show_info = not st.session_state.show_info

def toggle_description():
    st.session_state.show_description = not st.session_state.show_description

col1.button('Info', on_click=toggle_info)
col2.button('Description', on_click=toggle_description)

output_col1, output_col2 = st.columns(2)
if st.session_state.show_info:
    with output_col1:
        buffer = io.StringIO()
        st.session_state.filtered_df.info(buf=buffer)
        info = buffer.getvalue()
        st.text(info)

if st.session_state.show_description:
    with output_col2:
        st.write(st.session_state.filtered_df.describe())

movies_by_year = df['title_year'].value_counts().reset_index()
movies_by_year.columns = ['Year', 'Number of Movies']
movies_by_year = movies_by_year.sort_values('Year')

chart1 = alt.Chart(movies_by_year).mark_bar().encode(
    x=alt.X('Year:O', sort=None),
    y='Number of Movies'
).properties(
    title='Number of Movies by Year'
)

st.altair_chart(chart1, use_container_width=True)

director_popularity = df['director_name'].value_counts().reset_index()
director_popularity.columns = ['Director', 'Number of Movies']

chart2 = alt.Chart(director_popularity.head(10)).mark_bar().encode(
    x=alt.X('Director:O', sort=None),
    y='Number of Movies'
).properties(
    title='Top 10 Directors by Number of Movies'
)

st.altair_chart(chart2, use_container_width=True)
