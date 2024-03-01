
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

API_KEY="AIzaSyCDLgrmfvMD7aZf-tgToH-9qjb3eICTiVY"
genai.configure(api_key=API_KEY)


model_name = "gte-large"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


#model_id = "thenlper/gte-large"
#model_path = hf_hub_download(repo_id=model_id, filename="gte-large", cache_dir="/Volumes/SSD870/Models")  # Replace '<model_file>' if needed
embedding_model = SentenceTransformer('"thenlper/gte-large"')
# Define function that accepts a string as a title and a string as an abstract and returns an embedding
def generate_embedding(text):
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []

    """
    Generate an embedding for the specified text
    """

    # Create a new instance of the Embedding model

    # Generate the embedding for the title and abstract
    embedding = tokenizer.encode(text, return_tensors="pt")
    #embedding = embedding_model.encode(text)
    # Return the embedding
    return embedding.tolist()

def main():
    """
    Main function
    """
    abstract = "Following the gradual recognition of the importance of intracellular calcium stores for somatodendritic signaling in the mammalian brain, recent reports have also indicated a significant role of presynaptic calcium stores. Ryanodine-sensitive stores generate local, random calcium signals that shape spontaneous transmitter release. They amplify spike-driven calcium signals in presynaptic terminals, and consequently enhance the efficacy of transmitter release. They appear to be recruited by an association with certain types of calcium-permeant ion channels, and they induce specific forms of synaptic plasticity. Recent research also indicates a role of inositoltrisphosphate-sensitive presynaptic calcium stores in synaptic plasticity."
    text=""
    for _ in range(20):
        text += abstract
        print (f"Generating embedding for {len(text)} characters")
        embedding = generate_embedding(text)
    # print the embedding
   # print(embedding)


if __name__ == "__main__":
    main()