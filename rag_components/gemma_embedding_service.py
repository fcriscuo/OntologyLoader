
import google.generativeai as genai
import os

API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=API_KEY)

# Define function that accepts a string as a title and a string as an abstract and returns an embedding
def generate_embedding(title, abstract):
    if abstract is None or abstract == "" or title is None or title == "":
        return None
    model = 'models/embedding-001'
    """
    Generate an embedding for the specified title and abstract
    """

    # Create a new instance of the Embedding model

    # Generate the embedding for the title and abstract
    embedding = genai.embed_content(model=model,
                                content=abstract,
                                task_type="retrieval_document",
                                title=title)
    # Return the embedding
    return embedding['embedding']

def main():
    """
    Main function
    """
    title = "Presynaptic calcium stores and synaptic transmission."
    abstract = "Following the gradual recognition of the importance of intracellular calcium stores for somatodendritic signaling in the mammalian brain, recent reports have also indicated a significant role of presynaptic calcium stores. Ryanodine-sensitive stores generate local, random calcium signals that shape spontaneous transmitter release. They amplify spike-driven calcium signals in presynaptic terminals, and consequently enhance the efficacy of transmitter release. They appear to be recruited by an association with certain types of calcium-permeant ion channels, and they induce specific forms of synaptic plasticity. Recent research also indicates a role of inositoltrisphosphate-sensitive presynaptic calcium stores in synaptic plasticity."
   #test how large an abstract can be
    text=""
    for _ in range(12):
        text += abstract
        print (f"Generating embedding for {len(text)} characters")
        embedding = generate_embedding(title, text)



if __name__ == "__main__":
    main()