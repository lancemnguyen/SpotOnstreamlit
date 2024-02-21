import streamlit as st
from streamlit_folium import st_folium
from utils import search_places, get_reviews_from_api, generate_prompt, create_folium_map

st.set_page_config(page_title="SpotOnST")
st.title('📍 SpotOn')

st.sidebar.info(
    """
    Info: SpotOn is a web application that integrates Google Places API for searching places and ChatGPT API for generating answers based on the selected place reviews.
    """
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'selected_place' not in st.session_state:
    st.session_state.selected_place = {'name': '', 'place_id': '', 'address': ''}

with st.sidebar:
    query = st.text_input('Enter a place to search:', '')
    if query:
        st.session_state.results = search_places(query)

    if st.button('Search'):
        st.session_state.results = search_places(query)

# Directly update the selected_place based on the selection
st.session_state.selected_place = st.selectbox(
    'First, search a place in the sidebar, then select a place from the dropdown menu below:',
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

        st.subheader("Selected Place Details:")
        st.write(f"Name: {place_name}")
        st.write(f"Address: {place_address}")

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

# Map
st.write('Interactive Map to Display Places')

# Display the interactive map using st_folium
if st.session_state.results:
    st_folium_map = st_folium(create_folium_map(st.session_state.results), width=600, height=300)
else:
    st.warning("No search results to display on the map.")

# Chatbot section
st.header("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask a question about the reviews of the selected place."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Check for user input
if prompt := st.chat_input():
    # Append and display the user's input to the messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Generate, append, and display the chatbot's response using the selected place and user's input
    response = generate_prompt(selected_place, prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
