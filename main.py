import streamlit as st
from streamlit_folium import st_folium
from utils import search_places, get_reviews_from_api, convert_price_to_dollars, create_folium_map, generate_prompt

st.set_page_config(page_title="SpotOn", layout='wide')
st.title('📍 SpotOn')

st.sidebar.write('[My Portfolio](https://lancen.streamlit.app/)')
st.sidebar.caption("Made by [Lance Nguyen](https://www.linkedin.com/in/lancedin/)")

st.sidebar.info(
    """
    Info: SpotOn integrates OpenAI API with Google Places API, resulting in a question-answering platform about place reviews.
    Start by entering a place to search below in the sidebar.
    """
)

with st.sidebar.expander('**My Other Apps**'):
    st.caption('[LLM Optimization with RAG](https://lcrags.streamlit.app/)')
    st.caption('[Qdoc](https://qdocst.streamlit.app/)')
    st.caption('[CooPA](https://coopas.streamlit.app/)')

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'selected_place' not in st.session_state:
    st.session_state.selected_place = {'name': '', 'place_id': '', 'address': ''}

with st.sidebar:
    query = st.text_input('Enter a place to search:', '')
    st.sidebar.caption('Note: Best to include city name with place (e.g. disneyland anaheim).')
    if query:
        st.session_state.results = search_places(query)

    if st.button('Search'):
        st.session_state.results = search_places(query)

col1, col2 = st.columns(2)
with col1:
    # Directly update the selected_place based on the selection
    st.session_state.selected_place = st.selectbox(
        'Search a place in the sidebar, then select a place from the dropdown menu below:',
        st.session_state.results,
        format_func=lambda result: f"{st.session_state.results.index(result) + 1}. {result['name']} - {result.get('address', 'N/A')}",
        key='selectbox'
    )

# Access the selected place from session state
selected_place = st.session_state.selected_place

# Display details of the selected place
with st.sidebar:
    if selected_place:
        place_id = selected_place['place_id']
        place_name = selected_place['name']
        place_address = selected_place.get('address', 'N/A')
        business_status = selected_place.get('business_status', 'N/A')
        price_level = selected_place.get('price_level', 'N/A')
        rating = selected_place.get('rating', 'N/A')
        user_ratings_total = selected_place.get('user_ratings_total', 'N/A')

        st.subheader("Selected Place Details:")
        st.write(f"Name: {place_name}")
        st.write(f"Address: {place_address}")
        st.write(f"Status: {business_status}")
        st.write(f"Price Level: {convert_price_to_dollars(price_level)}")
        st.write(f"Rating: {rating}")
        st.write(f"Total Ratings: {user_ratings_total}")

        # Get and display reviews
        reviews = get_reviews_from_api(place_id)
        if reviews:
            with st.expander("Reviews:"):
                for review in reviews:
                    st.write(f"Author: {review.get('author_name', 'N/A')}")
                    st.write(f"Rating: {review.get('rating', 'N/A')}")
                    st.write(f"Text: {review.get('text', 'N/A')}")
                    st.write("---")
            st.caption("Note: Limited to 5 reviews due to Google's API.")
        else:
            st.write("No reviews available for this place.")

with col2:
    # Map
    st.write('**Interactive Map**')
    
    # Display the interactive map using st_folium
    if st.session_state.results:
        st_folium_map = st_folium(create_folium_map(st.session_state.results), width=400, height=300)
    else:
        st.warning("No search results to display on the map.")

# Chatbot section
st.header("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about the reviews of the selected place."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Check for user input
if prompt := st.chat_input():
    # Append and display the user's input to the messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Generate, append, and display the chatbot's response using the selected place and user's input
    if selected_place is not None:
        response = generate_prompt(selected_place, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
    else:
        st.warning("Please select a place first.")

if st.button("Refresh Conversation"):
    st.session_state.messages = [{"role": "assistant", "content": "Ask me anything about the reviews of the selected place."}]
    st.success("Conversation has been refreshed.")
