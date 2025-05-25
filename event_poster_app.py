import streamlit as st
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import datetime

st.title("🎉 Event Poster Generator")

# User inputs
api_key = st.text_input("Enter your OpenAI API Key:", type='password')

event_options = [
    "Birthday Party", "Housewarming", "Wedding", "Baby Shower",
    "Retirement Party", "Graduation Celebration", "Farewell Party"
]
event = st.selectbox("Select your Event Type:", event_options)

event_date = st.date_input("Select the Event Date:", datetime.date.today())

tone = st.text_input("Enter the tone (e.g., formal, casual, enthusiastic):", value="friendly")

platform = st.selectbox("Select platform for poster", ["LinkedIn", "WhatsApp"])

generate = st.button("Generate Poster")

if api_key and generate:
    client = OpenAI(api_key=api_key)

    try:
        # Step 1: Generate Poster Text
        prompt = (
            f"Create a {tone} invitation text for a {event} poster on {platform}. "
            f"Include the date: {event_date.strftime('%B %d, %Y')}. Keep it short and typo-free."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative event designer."},
                {"role": "user", "content": prompt},
            ],
        )
        poster_text = response.choices[0].message.content.strip()

        # Step 2: Generate Poster Background
        image_response = client.images.generate(
            prompt=f"An elegant poster background for a {event}, suitable for {platform}",
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url
        image_data = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # Step 3: Add text overlay
        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Font setup - fallback if Arial not found
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()

        # Wrap text
        lines = []
        words = poster_text.split()
        line = ""
        for word in words:
            if draw.textlength(line + word + " ", font=font) < image.width - 80:
                line += word + " "
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        y = 60
        for line in lines:
            draw.text((50, y), line.strip(), font=font, fill=(0, 0, 0, 255))
            y += 50

        final_image = Image.alpha_composite(image, txt_layer)

        st.image(final_image, caption="🎨 Your Custom Event Poster", use_container_width=True)

        # Save for download
        buf = io.BytesIO()
        final_image.convert("RGB").save(buf, format='PNG')
        st.download_button(
            label="📥 Download Poster",
            data=buf.getvalue(),
            file_name=f"{event.lower().replace(' ', '_')}_poster.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"❌ Error generating poster: {e}")

elif not api_key:
    st.info("🔐 Please enter your OpenAI API key to use the generator.")
