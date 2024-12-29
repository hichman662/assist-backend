def handle_image_upload(image_file):
    """
    Handles the logic for image upload.

    :param image_file: The uploaded image file
    :return: Tuple containing the response message and HTTP status code
    """
    if not image_file:
        return {"error": "No image file provided"}, 400  # Tuple with error response and status code

    # Log the filename for debugging
    print(f"Received image: {image_file.filename}")

    # Return a success message and status code
    return {"message": f"Image '{image_file.filename}' received successfully!"}, 200
