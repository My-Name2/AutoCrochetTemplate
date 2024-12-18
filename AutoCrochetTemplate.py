import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math
import io
from PIL import ExifTags

def correct_image_orientation(img):
    """Corrects image orientation based on EXIF data."""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif:
            exif = dict(exif.items())
            if orientation in exif:
                orientation_value = exif[orientation]
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        return img
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return img

def create_pixel_art_template(img, pixel_width, pixel_height, scale_factor=5):
    """Creates a pixel art template from a Image."""
    
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

st.title("Pixel Template Generator")

uploaded_file = st.file_uploader("Upload an image from your phone I might be looking :P (am not) ", type=["jpg", "jpeg", "png"])

unit_type = st.radio(
    "Select Units",
    ["Metric (cm)", "American (inches)"],
    index = 0 # default is Metric
)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        image = correct_image_orientation(image)  # Correct orientation before processing
        
        original_width, original_height = image.size
        st.image(image, caption="Uploaded Image", width = 300)

        preserve_aspect = st.checkbox("Preserve Original Resolution?")

        if preserve_aspect:
           # use scale_factor to scale up or down the image
           scale_factor_choice = st.number_input("Scaling Factor", value = 1.0, step=0.1)

           if scale_factor_choice > 0:

                pixel_width = int(original_width / scale_factor_choice)
                pixel_height = int(original_height / scale_factor_choice)

           else:
                pixel_width = 20
                pixel_height = 50
                st.warning("enter a positive number for the scale factor.")
        else:
           dimensions_input = st.text_input(
            "Enter the desired pixel dimensions (width height, e.g., 20 50). Width goes first",
            value="20 50",  # Provide a default value
            )

        if unit_type == "Metric (cm)":
            stitch_size = st.number_input(
            "Enter the approximate size of your stitch (in centimeters, e.g., 0.5 for 1/2cm)",
            value = 0.5,  # Provide a default value
            step = 0.1 # the amount to add each step
            )
        elif unit_type == "American (inches)":
            stitch_size = st.number_input(
            "Enter the approximate size of your stitch (in inches, e.g., 0.2 for 1/5in)",
            value = 0.2,  # Provide a default value
            step = 0.1 # the amount to add each step
            )

        if preserve_aspect:
            if scale_factor_choice > 0:
                template_img = create_pixel_art_template(image, pixel_width, pixel_height)
                st.image(template_img, caption="Pixel Template", use_container_width=True)

                estimated_width = pixel_width * stitch_size
                estimated_height = pixel_height * stitch_size
                    
                st.write(f"**Estimated Size:**")
                
                if unit_type == "Metric (cm)":
                    st.write(f"- Width: {estimated_width:.2f} cm")
                    st.write(f"- Height: {estimated_height:.2f} cm")
                elif unit_type == "American (inches)":
                    st.write(f"- Width: {estimated_width:.2f} inches")
                    st.write(f"- Height: {estimated_height:.2f} inches")

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
        elif dimensions_input:  # Ensure input is not empty
            try:
                pixel_width, pixel_height = map(int, dimensions_input.split())
                if pixel_width <= 0 or pixel_height <= 0:
                    st.error("Enter positive numbers for width and height.")
                else:
                    template_img = create_pixel_art_template(image, pixel_width, pixel_height)
                    st.image(template_img, caption="Pixel Art Template", use_container_width=True) # Changed here

                    # Calculate Estimated Size
                    estimated_width = pixel_width * stitch_size
                    estimated_height = pixel_height * stitch_size
                    
                    st.write(f"**Estimated Size:**")
                    
                    if unit_type == "Metric (cm)":
                         st.write(f"- Width: {estimated_width:.2f} cm")
                         st.write(f"- Height: {estimated_height:.2f} cm")
                    elif unit_type == "American (inches)":
                        st.write(f"- Width: {estimated_width:.2f} inches")
                        st.write(f"- Height: {estimated_height:.2f} inches")
                    
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
    st.info("Please upload an image to begin. or else")

st.header("Calculate Pixel Dimensions from Desired Size")

# Initialize variables with default values
desired_width = 10.0
desired_height = 10.0
stitch_size_calc = 0.5

if unit_type == "Metric (cm)":
    desired_width = st.number_input("Desired Width (cm)", value = 10.0, step = 1.0)
    desired_height = st.number_input("Desired Height (cm)", value = 10.0, step = 1.0)
    stitch_size_calc = st.number_input("Stitch Size (cm/pixel)", value = 0.5, step = 0.1)
elif unit_type == "American (inches)":
    desired_width = st.number_input("Desired Width (inches)", value = 4.0, step = 1.0)
    desired_height = st.number_input("Desired Height (inches)", value = 4.0, step = 1.0)
    stitch_size_calc = st.number_input("Stitch Size (in/pixel)", value = 0.2, step = 0.1)
    
    
if desired_width and desired_height and stitch_size_calc:
    
    if unit_type == "Metric (cm)":
        calculated_width_pixels = desired_width / stitch_size_calc
        calculated_height_pixels = desired_height / stitch_size_calc
    elif unit_type == "American (inches)":
        calculated_width_pixels = desired_width / stitch_size_calc
        calculated_height_pixels = desired_height / stitch_size_calc
    
    st.write(f"**Approximate pixel dimensions:**")
    st.write(f"Width: {calculated_width_pixels:.0f} pixels")
    st.write(f"Height: {calculated_height_pixels:.0f} pixels")
