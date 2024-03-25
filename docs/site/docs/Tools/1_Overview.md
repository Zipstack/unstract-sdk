![tools overview](/img/page_content/tools-overview.drawio.png)

The diagram shows how tools fit into the worflows enabled by the Unstract platform. The sources and sinks are configured in the workflow setup in the UI.

> Note: The worflow can have any number of tools chained together. The example shows 3 tools chained together. And in most real world use cases a worflow might not sink data to both unstrucured and structured sinks

Please note that:

- A "Tool" with respect to the Unstract platform is a generic concept and can be used to perform any kind of processing. It could do anything from parsing a PDF file to performing complex NLP tasks. It could even be used to just clean up data before passing it to the next tool in the worflow.
- Tools are run sequentially in the order they are chained in the worflow
- If the previous tool generates multiple outputs (array), all the tools after it is run for each of the outputs
- Tools need not use LLMs and Vector DBs. They can be used to perform any kind of processing. However, the platform provides a convenient interface to use LLMs and Vector DBs. The tools can use these interfaces to perform complex NLP tasks and to store and retrieve data from Vector DBs.

### Examples of tools which can be created with the SDK

>All the builtin tools in the platform are built using the same SDK provided.

- **Directory readers** These tools can read a directory and create an array of file paths. This array can be used as input to the next tool in the worflow. This is useful when the worflow needs to process multiple files in a directory. *Most* workflows will have atleast one of these tools as the starting point. The setting for these tools can include file filters, mazimum number of files to read, etc.
- **Indexers** These tools can be used to index (embeddings) documents supplied by directory readers. The builtin indexer tool is fully functional but if you need a more complex of powerful indexer, you can build your own complex indexing tool using the SDK. The generated index can be used to power RAG (Q&A) based applications.
- **Traditional IDP** These tools can be used to perform traditional IDP tasks like OCR, etc. 
- **LLM based document processing** These tools can be used to perform IDP, NLP, Table extraction, Information extraction, Classification tasks using LLMs. 
- **Unstructured to Unstructured** For example, a tool that can take a PDF and extract PII information from it and also generate a redacted PDF.
- **Unstructured to Structured** For example, a tool that can take a PDF and extract financial information and store it in a database. Another simple use case would be extracting candidate information from a resume and store it in a database or spreadsheet.
