# Use the official TensorFlow Serving image as the base image
FROM tensorflow/serving:latest

# Create a directory to store your model
WORKDIR /models

# Copy your saved model (in HDF5 format) into the container
COPY /saved_model /models/arithmeticOCR_model/1/

# Expose the gRPC and REST API ports (default ports used by TensorFlow Serving)
EXPOSE 8501
EXPOSE 8500

# Define the command to start TensorFlow Serving with your model
CMD ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_name=arithmeticOCR_model", "--model_base_path=/models/arithmeticOCR_model/"]
