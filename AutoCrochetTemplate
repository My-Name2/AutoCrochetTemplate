import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math
import io

def create_pixel_art_template(img, pixel_width, pixel_height, scale_factor=5):
    """Creates a pixel art template from a PIL Image."""
    
    img_small = img.resize((pixel_width, pixel_height), resample=Image.BILINEAR)

    img_scaled = img_small.resize(
        (img_small.width * scale_factor, img_small.height * scale_factor),
        resample=Image.NEAREST
    )

    try:
        font_size = int(scale_factor * 1.5)
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Initialize a dummy image and draw object for text size calculations
    dummy_img = Image.new('RGB', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # Calculate padding sizes using font.getbbox
    max_num_width = max([
        dummy_draw.textbbox((0, 0), str(i + 1), font=font)[2] - dummy_draw.textbbox((0, 0), str(i + 1), font=font)[0]
        for i in range(pixel_height)
    ])
    padding_left = max_num_width + 10  # Add extra space

    max_num_height = max([
        dummy_draw.textbbox((0, 0), str(i + 1), font=font)[3] - dummy_draw.textbbox((0, 0), str(i + 1), font=font)[1]
        for i in range(pixel_width)
    ])
    padding_top = max_num_height + 10  # Add extra space

    # Create new image with padding
    new_width = img_scaled.width + padding_left
    new_height = img_scaled.height + padding_top
    img_result = Image.new('RGB', (new_width, new_height), 'white')
    img_result.paste(img_scaled, (padding_left, padding_top))

    draw = ImageDraw.Draw(img_result)

    # --- Adding Grid Lines ---
    for x in range(0, img_scaled.width + 1, scale_factor):
        draw.line(
            [(x + padding_left, padding_top), (x + padding_left, img_result.height)],
            fill='gray'
        )

    for y in range(0, img_scaled.height + 1, scale_factor):
        draw.line(
            [(padding_left, y + padding_top), (img_result.width, y + padding_top)],
            fill='gray'
        )

    # --- Adding Numbers Along the Sides ---
    # Left side numbers
    for i in range(pixel_height):
        text = str(i + 1)
        text_width = dummy_draw.textbbox((0, 0), text, font=font)[2] - dummy_draw.textbbox((0, 0), text, font=font)[0]
        text_height = dummy_draw.textbbox((0, 0), text, font=font)[3] - dummy_draw.textbbox((0, 0), text, font=font)[1]
        y = i * scale_factor + padding_top + (scale_factor - text_height) // 2
        x = padding_left - text_width - 5  # Adjust for spacing
        draw.text((x, y), text, fill='black', font=font)

    # Top side numbers
    for i in range(pixel_width):
        text = str(i + 1)
        text_width = dummy_draw.textbbox((0, 0), text, font=font)[2] - dummy_draw.textbbox((0, 0), text, font=font)[0]
        text_height = dummy_draw.textbbox((0, 0), text, font=font)[3] - dummy_draw.textbbox((0, 0), text, font=font)[1]
        x = i * scale_factor + padding_left + (scale_factor - text_width) // 2
        y = padding_top - text_height - 5  # Adjust for spacing
        draw.text((x, y), text, fill='black', font=font)
    return img_result

st.title("Pixel Art Template Generator")

uploaded_file = st.file_uploader("Upload an image from your phone", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width = 300)

        dimensions_input = st.text_input(
            "Enter the desired pixel dimensions (width height, e.g., 20 50). Width goes first",
            value="20 50",  # Provide a default value
        )

        if dimensions_input:  # Ensure input is not empty
            try:
                pixel_width, pixel_height = map(int, dimensions_input.split())
                if pixel_width <= 0 or pixel_height <= 0:
                    st.error("Please enter positive numbers for width and height.")
                else:
                    template_img = create_pixel_art_template(image, pixel_width, pixel_height)
                    st.image(template_img, caption="Pixel Art Template", use_column_width=True)

                    # Download Button (Using Bytes)
                    buf = io.BytesIO()
                    template_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()

                    st.download_button(
                        label="Download Image",
                        data = byte_im,
                        file_name = "pixel_art_template.png",
                        mime="image/png"
                        )
            except ValueError:
                st.error("Invalid input. Please enter integers for pixel width and height.")

    except Exception as e:
        st.error(f"Error processing image: {e}")
else:
    st.info("Please upload an image to begin.")
