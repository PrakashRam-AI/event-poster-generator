import streamlit as st
import openai
from PIL import Image
import io
import os

st.title("Event Poster Generator with Text Cleanup")

# Get OpenAI API key securely from environment or input
api_key = st.text_input("Enter your OpenAI API Key:", type='password') or os.getenv("OPENAI_API_KEY")

if api_key:
    openai.api_key = api_key

    # Inputs
    event = st.text_input("Enter the event type (e.g. Birthday party, Housewarming):")
    tone = st.text_input("Enter the tone for the text (e.g. formal, casual, cheerful):")
    user_text = st.text_area("Enter the text/content for the poster:")

    if st.button("Generate Poster"):
        if not event or not tone or not user_text:
            st.error("Please enter all fields: event, tone, and text.")
        else:
            try:
                # Step 1: Clean up user text via GPT
                cleanup_prompt = (
                    f"Please correct any grammar and spelling errors, and rewrite the following text "
                    f"in a clear and {tone} style suitable for an event poster:\n\n\"{user_text}\""
                )
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that fixes text for event posters."},
                        {"role": "user", "content": cleanup_prompt},
                    ],
                    temperature=0.3,
                )
                cleaned_text = response.choices[0].message.content.strip()

                st.subheader("Preview of cleaned text:")
                st.write(cleaned_text)

                # Step 2: Generate image prompt
                image_prompt = (
                    f"Create a professional, clean, and visually appealing poster for a {event} event. "
                    f"The poster should have clear, readable typography with the following text prominently displayed: "
                    f"'{cleaned_text}'. Use a style suitable for LinkedIn and WhatsApp sharing, with good contrast and no text distortion."
                )

                # Step 3: Generate image
                image_response = openai.Image.create(
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = image_response['data'][0]['url']

                # Download the image data
                image_data = openai.util.get_image(image_url)
                image = Image.open(io.BytesIO(image_data))

                # Show the image
                st.image(image, caption=f"Poster for {event}", use_container_width=True)

                # Prepare image for download
                buf = io.BytesIO()
                image.save(buf, format='PNG')
                byte_data = buf.getvalue()

                st.download_button(
                    label="Download Poster Image",
                    data=byte_data,
                    file_name=f"poster_{event.replace(' ', '_').lower()}.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Error generating poster: {e}")

else:
    st.info("Please enter your OpenAI API key to use the app.")
