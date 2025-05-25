import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
import io

st.title("Event Poster Generator")

# User inputs
api_key = st.text_input("Enter your OpenAI API Key:", type='password')

# Event dropdown options
event_options = [
    "Birthday Party",
    "Housewarming Ceremony",
    "Wedding",
    "Corporate Event",
    "Baby Shower",
    "Anniversary",
    "Graduation Party"
]
event = st.selectbox("Select the event:", event_options)

# Tone dropdown options
tone_options = ["Friendly", "Formal", "Casual", "Enthusiastic", "Professional"]
tone = st.selectbox("Select the tone for the invitation:", tone_options)

# Date picker
event_date = st.date_input("Select the event date:")

# Venue input
venue = st.text_input("Enter the venue:")

# Platform selection
platform = st.selectbox("Select platform for poster:", ["LinkedIn", "WhatsApp"])

# Generate button
generate = st.button("Generate Poster")

if api_key and generate:
    client = OpenAI(api_key=api_key)

    if not event.strip():
        st.error("Please select an event.")
    elif not venue.strip():
        st.error("Please enter the venue.")
    else:
        try:
            # Compose prompt for poster text
            prompt = (
                f"Create a {tone.lower()} invitation text for a {event} on {event_date.strftime('%B %d, %Y')} "
                f"at {venue}, tailored for {platform}. Keep it concise, clear, and error-free."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative design assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            poster_text = response.choices[0].message.content.strip()

            st.subheader("Generated Poster Text:")
            st.write(poster_text)

            # Generate poster image
            image_response = client.images.generate(
                prompt=f"An artistic, elegant poster background for a {event}",
                n=1,
                size="1024x1024"
            )
            image_url = image_response.data[0].url

            # Download and display the image
            image_data = requests.get(image_url).content
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption=f"Poster background for {event}", use_container_width=True)

            # Download button
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            st.download_button(
                label="Download Poster Background Image",
                data=buf.getvalue(),
                file_name=f"{event.lower().replace(' ', '_')}_poster.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Error generating poster: {e}")

elif not api_key:
    st.info("Please enter your OpenAI API key to use the generator.")
