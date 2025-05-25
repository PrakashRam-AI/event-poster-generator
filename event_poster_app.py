import streamlit as st
import openai
import requests
from PIL import Image
import io

st.title("🎉 Event Poster Generator")

# User inputs their OpenAI API key securely
api_key = st.text_input("Enter your OpenAI API Key:", type='password')

if api_key:
    client = openai.OpenAI(api_key=api_key)

    event_type = st.selectbox("Choose Event Type", ["Birthday Party", "Housewarming Ceremony", "Graduation", "Anniversary", "Custom"])
    custom_event = st.text_input("Enter custom event type (if selected above):") if event_type == "Custom" else event_type

    name = st.text_input("Host or Person's Name:")
    date = st.date_input("Event Date")
    location = st.text_input("Location (optional):")
    message = st.text_area("Custom Message (optional):")

    platform = st.selectbox("Choose Output Format", ["LinkedIn", "WhatsApp"])

    tone = st.selectbox("Select Poster Tone", ["Elegant", "Playful", "Traditional", "Modern", "Professional", "Custom"])
    custom_tone = st.text_input("Enter custom tone (if selected above):") if tone == "Custom" else tone

    if st.button("Generate Poster"):
        if not name:
            st.error("Please enter the name.")
        else:
            try:
                prompt = (
                    f"A {custom_tone.lower()} digital poster for a {custom_event}, hosted by {name}, "
                    f"on {date.strftime('%B %d, %Y')}. "
                    f"{'Location: ' + location + '.' if location else ''} "
                    f"{message if message else ''} "
                    f"Styled for sharing on {platform}. Typography-focused, clean layout, visually appealing."
                )

                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )

                image_url = response.data[0].url

                img_data = requests.get(image_url).content
                image = Image.open(io.BytesIO(img_data))

                st.image(image, caption=f"{custom_event} Poster", use_container_width=True)

                buf = io.BytesIO()
                image.save(buf, format='PNG')
                st.download_button(
                    label="Download Poster",
                    data=buf.getvalue(),
                    file_name=f"{custom_event.replace(' ', '_')}_poster.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Failed to generate poster: {e}")

else:
    st.info("Enter your API key to get started.")
