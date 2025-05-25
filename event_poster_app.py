import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
import io

st.title("🎨 Event Poster Generator")

# User inputs
api_key = st.text_input("🔑 Enter your OpenAI API Key:", type='password')
event = st.text_input("📌 Event (e.g., Birthday party, Housewarming):")
date = st.text_input("📅 Date of Event (e.g., June 15, 2025):")
time = st.text_input("⏰ Time of Event (e.g., 6:00 PM):")
venue = st.text_input("📍 Venue / Address:")
tone = st.selectbox("🎭 Choose the tone:", ["Friendly", "Formal", "Casual", "Enthusiastic"])
platform = st.selectbox("📱 Select platform for poster:", ["LinkedIn", "WhatsApp"])
generate = st.button("🚀 Generate Poster")

if api_key and generate:
    client = OpenAI(api_key=api_key)

    if not event.strip():
        st.error("Event is required.")
    else:
        try:
            # Generate poster text
            prompt = (
                f"Write a {tone.lower()} and clear event poster message for a {event} happening on {date} at {time} in {venue}. "
                f"The poster is meant for {platform}. Keep the text professional, polished, and typo-free."
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a creative poster copywriter."},
                    {"role": "user", "content": prompt},
                ],
            )
            poster_text = response.choices[0].message.content.strip()

            st.subheader("📝 Generated Poster Text:")
            st.write(poster_text)

            # Generate poster image
            image_prompt = f"An elegant, high-quality background image for a {event} invitation poster"
            image_response = client.images.generate(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response.data[0].url

            # Download and display the image
            image_data = requests.get(image_url).content
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption="🎨 Poster Background", use_container_width=True)

            # Download button
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            st.download_button(
                label="⬇️ Download Background Image",
                data=buf.getvalue(),
                file_name=f"{event.lower().replace(' ', '_')}_poster.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"❌ Error generating poster: {e}")

elif not api_key:
    st.info("🔐 Please enter your OpenAI API key to get started.")
