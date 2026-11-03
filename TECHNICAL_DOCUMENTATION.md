# DentalVision AI – Technical Documentation

## 1. System purpose

This project is a dental disease image classification system. It accepts an uploaded dental image, validates that it is a tooth-related image, then passes it into a deep learning model that produces a disease class label such as gingivitis, caries, or hypodontia. The system is designed as a demonstration of end-to-end machine learning and web development work.

## 2. Technology stack

### Python

Python is the main language for:

- backend logic,
- ML preprocessing,
- model loading and inference,
- notebook experimentation.

### Flask

Flask is used as the web framework to serve the UI and respond to image upload requests.

### TensorFlow / Keras

TensorFlow is used for model ingestion and prediction.

### OpenCV

OpenCV is used for image loading and resizing in both the application and the notebook.

### NumPy

NumPy is used for array conversion and probability tensor handling.

### Groq API

Groq is used by `another.py` to send images to an external multimodal model for a simple validation check.

### Jinja2

The Flask app uses Jinja2 templates to render the HTML page.

### JavaScript

JavaScript on the frontend handles `fetch()` requests and updates the UI after prediction.

## 3. Frontend design

The frontend is a single HTML file:

- `templates/index.html`

The page contains:

- a file input element,
- a form configured with `enctype="multipart/form-data"`,
- a button labeled “Predict”,
- a result section with prediction text, confidence text, and image preview.

### JavaScript behavior

The browser intercepts form submission with `addEventListener('submit', ...)`.

It then:

1. gathers the form data,
2. posts it to the Flask back end,
3. parses the JSON response,
4. updates the DOM with the model result or validation message,
5. displays the uploaded image using the returned `image_url`.

## 4. Backend design

The Flask app is defined in `app.py`.

### Key endpoints

#### `/`

Returns the main HTML page using `render_template('index.html')`.

#### `/predict`

This is the main inference endpoint.

It does the following:

1. checks if a file was provided,
2. ensures an upload folder exists,
3. saves the given file to `static/uploads/`,
4. calls `analyze_image(file_path)`,
5. checks `is_teeth` from the returned JSON,
6. preprocesses the image when validation passes,
7. loads the model and predicts the class,
8. computes confidence and entropy,
9. returns JSON metadata including prediction and score.

## 5. How image validation works

The validation step lives in `another.py`.

### Function flow

- `image_to_base64(image_path)` reads the image bytes and converts them to base64.
- `analyze_image(image_path)` then builds a multimodal prompt with:
  - a text instruction: “is this a teeth image? Respond with a JSON object containing a 'is_teeth' boolean field”
  - the image as a data URL
- It sends the request using the Groq client.
- It expects a JSON response.
- The response is parsed with `json.loads()`.

The validation call is not a local image classifier in the project. Instead, it depends on cloud LLM inference.

## 6. Dataset loading and preprocessing

The notebook `Source code.ipynb` contains the dataset pipeline.

### Loading logic

It scans directories under `path` and loads any subdirectories containing image files.

Key steps:

- `os.listdir(path)` identifies folders
- `load_images_for_class(classDir, classIndex)` iterates image files
- images are read using OpenCV
- each image is resized to `(128, 128)`
- class labels are assigned by folder index
- arrays of images and labels are accumulated

### Dataset structure

The project observed the following classes in the dataset root:

- Calculus
- Data caries
- Gingivitis
- hypodontia
- ulcer original dataset

These are class-folder names inside `Data set/`.

### Normalization

The notebook normalizes images by dividing by `255.0`:

```python
images = images / 255.0
```

### Train/test/validation split

The notebook uses `StratifiedShuffleSplit` to split data into train, validation, and test sets. This is important because it preserves class balance across subsets.

## 7. How the model is trained

The notebook defines multiple model families:

- a custom CNN
- ResNet50 transfer learning
- MobileNet transfer learning
- EfficientNetB0 transfer learning

### Data augmentation

The notebook uses `ImageDataGenerator` with:

- rotation
- width shift
- height shift
- shear
- zoom
- horizontal flip

This helps reduce overfitting by artificially increasing data variety.

### Model architecture examples

The custom CNN stack includes:

- convolutional blocks
- max pooling
- batch normalization
- flattening
- dense layers
- dropout
- final dense output layer with `softmax`

The transfer learning models are built by:

- using a pretrained ImageNet backbone without the top layer,
- adding a global average pooling layer,
- adding a dense classification head,
- freezing the base model layers initially,
- compiling with `sparse_categorical_crossentropy` and `accuracy`.

### Training loop

Each model is trained with:

- `model.fit(...)`
- `EarlyStopping(monitor='val_loss', patience=3)`
- `epochs=20`

Then each model is evaluated on the test set and saved as `.h5` files.

## 8. Prediction generation in the app

The live app uses `model.predict(image)[0]` after preprocessing.

### Prediction steps

1. The uploaded image is read with OpenCV.
2. It is resized to `(128, 128)`.
3. It is normalized.
4. A batch dimension is added: `np.expand_dims(..., axis=0)`.
5. The model predicts a probability vector.
6. `np.argmax(pred_probs)` picks the most likely class.

### Model output and confidence

The application sets:

```python
predicted_index = np.argmax(pred_probs)
confidence = pred_probs[predicted_index]
```

This means the top class probability is treated as the model confidence value.

## 9. How prediction confidence is calculated

The `calculate_entropy` helper computes Shannon entropy:

```python
return -np.sum(probs * np.log(probs + 1e-10))
```

This measures how spread out the class probabilities are.

### Threshold logic

The application applies these rules:

- `confidence_threshold = 0.9`
- `entropy_threshold = 1.2`
- `second_highest_prob = np.sort(pred_probs)[-2]`

Then it accepts a prediction only if:

- confidence is at least 0.9,
- entropy is below 1.2,
- the gap between the top and second-highest class is greater than 0.2.

Otherwise it returns:

```json
{ "prediction": "Not the proper data" }
```

This logic is a custom rejection mechanism that tries to filter uncertain predictions.

## 10. External APIs used

The project uses one major external service:

### Groq API

`another.py` calls the Groq chat completions API using a multimodal request and the model:

```python
meta-llama/llama-4-maverick-17b-128e-instruct
```

This is used for image validation, not for the main disease classification task.

### Important note

The API key must be present in the environment as `GROQ_API_KEY`. There is no `.env` file committed to the repository.

## 11. Dependency requirements

The project dependency list is in `requirements.txt`:

- `flask`
- `tensorflow`
- `opencv-python`
- `numpy`
- `groq`
- `python-dotenv`
- `Pillow`

These are enough to run the current prototype in a Python environment with machine-learning support. However, a production-grade ML project would typically also include:

- proper version pinning,
- environments and lock files,
- test dependencies,
- linting and formatting tools,
- CI/CD tools,
- Docker configuration,
- monitoring and logging libraries.

## 12. Important implementation risk areas

### 1. Missing model artifact

The app tries to load a model file from a hardcoded Windows path:

```python
r"C:\Users\exter\OneDrive\Desktop\project\MobileNet_Model (1).h5"
```

This path is not part of the repository and is unlikely to exist in another machine or environment.

### 2. Label mismatch

The backend class list contains six labels:

- Calculus
- Dental Caries
- Gingivitis
- Hypodontia
- Mouth Ulcer
- Tooth Discoloration

The dataset folders include a different set of names, and the dataset classes are not aligned with the hardcoded list. This makes the model output and the app labels inconsistent with the actual training data.

### 3. Cloud dependency

The validation step depends on Groq’s remote API, which means inference may fail when there is no network or valid key.

### 4. No persistence or database

The project does not have a database or persistent user history. It is just a single-file upload/use-case demo.

### 5. No production deployment configuration

There is no Dockerfile, `docker-compose`, Kubernetes config, or deployment script.

## 13. Summary

This project is a full-stack machine learning prototype for dental disease classification. It combines a simple web interface, a Flask backend, image validation via Groq, and a TensorFlow image classifier trained in a notebook. The code demonstrates the core idea effectively, but the current implementation is not yet robust enough for production or professional portfolio-grade deployment due to missing model artifacts, hardcoded paths, class mismatches, and minimal architecture modularization.
