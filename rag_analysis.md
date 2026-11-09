Part 4: System Design Reflection

Step 4.1: Cost Awareness

Several factors influence the cost and performance of our RAG system, including embedding size, chunk size, and top-k retrieval. Since Knit is designed to help college students discover activities and connect with others who share similar interests, we want to balance response quality with affordability and efficiency.

Embedding size:

An embedding is a numeric vector representation of text that captures semantic
meaning. Larger embedding models generally produce higher-dimensional vectors, which require more storage and can increase processing time. Smaller embedding models are generally faster and more resource-efficient, making them useful when handling a large number of user queries.

For Knit, a smaller embedding model could be sufficient for everyday activity recommendations, such as finding beginner-friendly hobbies, running clubs, or social events. A larger embedding model could potentially improve retrieval when users submit more complicated queries involving multiple interests or preferences. However, larger models do not automatically guarantee better results, so we would choose an embedding model based on its actual retrieval performance rather than its size alone.

Chunk Size:

Chunk size also affects system cost because it determines how much information needs to be embedded, stored, and retrieved. Smaller chunks can provide more specific information, but they may separate important details from their surrounding context. Larger chunks preserve more information but require additional storage and may introduce irrelevant information into the retrieved context. For Knit, we want to prioritize the chunks that contain the complete descriptions of each hobbies, reccomendations, and activities. This would help the system retrieve meaningful information and generate more relevant activity suggestions.

Top-k Retrieval:

This section will return the top-k closest matches before it gets passed to the generation model. However, this also increases the amount of text processed by the LLM. For Knit, retrieving three relevant chunks could be sufficient for straightforward activity recommendations. More complex questions may require additional context, so we would adjust the top-k value based on the type of request.

Additional Information:
FAISS is not needed to be replaced because it works for the recent prototype due to its purpose of finding the most similar embeddings from a collection of stored vectors. Later on, the system could eventually use a distributed or managed vector database.  

Step 4.2: RAG vs Alternatives

| Approach | When to Use | Application in Knit |
|---|---|---|
| RAG | When an application needs to retrieve specific information from an external knowledge base that may change over time. | Retrieve information about hobbies, activities, beginner advice, social events, and recommendations to generate personalized suggestions. |
| Fine-tuning | When a model needs to learn a particular response style, behavior, or specialized task through additional training. | Train the model to generate responses that follow Knit's conversational style and provide friendly, welcoming activity recommendations. |
| Pure Prompting | When the application needs general responses without retrieving information from an external knowledge base. | Answer general questions or provide simple suggestions using the model's existing knowledge and instructions. |

The best approach for Knit: RAG

The application relies on providing new and relevant information and changing preference depending on the users. When a user asks to recommend beginner-friendly activities, RAG can retrieve information on beginner-friendly activities instead of only relying on the existing model's knowledge. In the future, Fine-tuning may not be the most useful when it comes to updating new information. Pure prompting is simpler and cost less, however it would not be able to have control over the information AI uses.   

Step 4.3: System Design

How would Knit scale to 10K users/day?

To support 10,000 users per day, we would need to transition it into a cloud-based system that can be accessed by multiple users simultaneously. First, we would deploy the RAG pipeline to cloud infrastructure instead of relying on a local computer. We would also use multiple application servers and a load balancer to distribute incoming requests, allowing the system to handle more users without overwhelming a single server.

Additionally, the Qwen2.5-1.5B-Instruct generation model would need to be hosted as a shared service so that users could request recommendations without running the model themselves. We would also move our locally stored FAISS index to a persistent vector database, allowing different application servers to access the same knowledge base. Finally, we would connect the RAG system to Knit's activity database so that new hobbies, events, and user contributions could be incorporated into future recommendations. These changes would allow Knit to move beyond a small local experiment and become a system that can support a much larger user community.

How Would Knit Optimize:

1. Optimize embedding generation: Instead of generating embeddings every time someone submits a request, we would precompute and store embeddings for existing activities. We would only generate new embeddings when new activities or information are added.
2. Improve retrieval efficiency: Use appropriate chunk size and avoid sending irrelevant and unnecessary information to the model. Retrieving the three most relevant chunks could provide enough context for a simple activity recommendation without increasing processing time. 
3. Implement caching: We could temporarily store responses to frequently asked questions. If multiple users ask similar questions, Knit could reuse an existing response instead of processing the same request from the beginning.
4. Use a Scalable Vector Database: Our current implementation uses FAISS for similarity searches. For a larger application, we could consider a managed or distributed vector database that supports persistent storage, efficient searching, and scaling as the number of activities and users increases, as mentioned previously. 

A diagram of Knit's system design:

The diagram below illustrates how a user's request moves through Knit's RAG system and how the system retrieves information to generate personalized activity recommendations.

                  +---------------------------+
                  |       KNIT USERS          |
                  |      (10K Users/Day)      |
                  +-------------+-------------+
                                |
                                v
                  +---------------------------+
                  |     CLOUD INFRASTRUCTURE  |
                  +-------------+-------------+
                                |
                                v
                  +---------------------------+
                  |       LOAD BALANCER       |
                  +-------------+-------------+
                                |
                 +--------------+--------------+
                 |              |              |
                 v              v              v
           +-----------+  +-----------+  +-----------+
           | APP       |  | APP       |  | APP       |
           | SERVER 1  |  | SERVER 2  |  | SERVER 3  |
           +-----+-----+  +-----+-----+  +-----+-----+
                 |              |              |
                 +--------------+--------------+
                                |
                                v
                  +---------------------------+
                  |       RAG PIPELINE        |
                  +-------------+-------------+
                                |
                                v
                  +---------------------------+
                  |      QUERY PROCESSING     |
                  +-------------+-------------+
                                |
                                v
                  +---------------------------+
                  |       EMBEDDING MODEL    |
                  +-------------+-------------+
                                |
                                v
                  +---------------------------+
                  |      VECTOR DATABASE     |<------------------+
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |      SIMILARITY SEARCH    |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |    RETRIEVE TOP-K CHUNKS  |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |     RETRIEVED CONTEXT     |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |     PROMPT CONSTRUCTION   |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |  QWEN2.5-1.5B-INSTRUCT    |                   |
                  |       (GENERATION)        |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |     GENERATED RESPONSE    |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  |   DISPLAY RESPONSE IN     |                   |
                  |           KNIT            |                   |
                  +-------------+-------------+                   |
                                |                                  |
                                v                                  |
                  +---------------------------+                   |
                  | PERSONALIZED ACTIVITY     |                   |
                  |     RECOMMENDATIONS       |                   |
                  +---------------------------+                   |
                                                                   |
    +---------------------------+                                  |
    |   KNIT ACTIVITY DATABASE  |                                  |
    +-------------+-------------+                                  |
                  |                                                |
                  v                                                |
    +---------------------------+                                  |
    | NEW ACTIVITIES AND USER   |                                  |
    |       CONTRIBUTIONS       |                                  |
    +-------------+-------------+                                  |
                  |                                                |
                 