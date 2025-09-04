from vertexai.language_models import TextEmbeddingModel
import vertexai

# Initialize Vertex AI
vertexai.init(project="tucsfe-ai-integration-project", location="us-central1")

# Load model and get embeddings
model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
embeddings = model.get_embeddings(["Test sentence for embedding."])

# Print embedding values
print(embeddings[0].values)
