# License
Please read this project license: https://github.com/pyautoml/machine_learning/blob/main/RAG_with_agents/License.md

# Project
This project shows ste-by-step how to build and use RAG using the following technologies:
- Qdrant vectorstore (open-souece vector database),
- MsSQL (local, commercial version),
- Transfrormers from Huggingface,
- open-source models like Mistral, Vicuna, Falcon, and many more,
- commercial, paid models like GPT-4 from OpenAI.
- agetns, semi-independent tools that are able to decide which function should be run next.

# Step by step
This project aims to:
- download and prepare data,
- load data to a relational database (MsSQL),
- prepare embeddings based on the data stored in the relational database and store them in Qdrant,
- create a small toolset to wrangle and manage data, including: selects, inserts, updates, and deleteion from both vector and relational databases,
- connecting agents and specify their goals,
- create and maintain metrics and other data on the performance of tested models,
- prepare a simple GUI i Streamlit to mimic a chat window allowing users to use RAG in real-time,
- add seaborn / matplotlib visualisations.
