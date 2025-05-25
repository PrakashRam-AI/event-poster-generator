import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
import io

st.title("Event Poster Generator")

# User inputs
api_key = st.text_input("Enter your OpenAI API Key:", type='password')

event = st.text_input("Enter the event (e.g., Birthday party, Housewarming):")

tone = st.text_input("Enter the tone (e.g., formal, casual, enthusiastic):", value="friendly")

platform = st.selectbox("Select platform for poster", ["LinkedIn", "WhatsApp"])

# Generate button (outside input fields, so inputs never disappear)
generate = st.button("Generate Poster")

if api_key and generate:
    client = OpenAI(api_key=api_key)

    if not event.strip():
        st.error("Please enter an event.")
    else:
        try:
            # Generate poster text
            prompt = (
                f"Create a {tone} invitation text for a {event} poster tailored for {platform}. "
                "Keep it concise and error-free."
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
