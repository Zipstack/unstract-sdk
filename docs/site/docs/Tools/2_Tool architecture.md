<img src="/img/page_content/tools-architecture.drawio.png" width="75%"></img>

## The building blocks of the Unstract platform

Tools are the building blocks of the Unstract platform. They take a single string input and produce a single string output. These tools can be chained together to create complex worflows that can be used to process unstructured data. Tools can produce output to be consumed by other tools in the worflow or they can produce output that can be sent to a structured/unstructured data sink using the Unstract SDK.

## Isolation and Sandbox

All tools are isolated from the rest of the system and run in a sandboxed/containerized environment. This means that the tools by default cannot access any resources outside of the sandbox. Only resources shared intentionally by the user are accessible. This is done to ensure that the tools are secure and cannot access any sensitive information. The tools are also run in a separate process from the rest of the system. This ensures that the tools cannot access any resources outside of the sandbox.

>Note that while developing a new tool, the SDK and the architecture allows you to run the tool in a non-sandboxed environment for convenience. This is useful for debugging and testing purposes. However, the tool will be run in a sandboxed environment when it is deployed to the platform.

### Access to unstructured data (PDF files, Text files, etc.)

The file sources configured in the platform automatically show up as folders in the sandboxed environment. The tools can access these folders to read and write files. The files written to these folders will be automatically uploaded to the configured file sink. The files will be available in `/mnt/unstract/fs_input/` and  `/mnt/unstract/fs_output/` folders in the sandboxed environment.

### Access to structured data (SQL databases, Warehouses, Datalakes etc.)

The database sources configured in the platform will be available as **SQLAlchemy** engines through the Unstract SDK. The tools can use these engines to read and write data to the configured database sinks. Note that the security and access control of the database sources and sinks are not managed by the platform. While setting up the database sources and sinks, the user will have to provide the necessary credentials and these credentials will have to take care of access control on the DB side. Also these credentials are not available to the tools. The tools can only access the database engines provided by the SDK.

### Access to Vector Databases

The vector databases configured in the platform will be available as [Llamaindex](https://www.llamaindex.ai/) `index` objects through the Unstract SDK. Refer to [LLamaindex documentaion](https://docs.llamaindex.ai/en/stable/core_modules/data_modules/index/root.html) for more details on Index objects. The tools can use these indexes to read and write data to the configured vector databases. Note that the security and access control of the vector database sources and sinks are not managed by the platform. While setting up the vector database sources and sinks, the user will have to provide the necessary credentials and these credentials will have to take care of access control on the vector DB side. Also these credentials are not available to the tools. The tools can only access the vector database indexes provided by the SDK. 

### Access to LLMs

The LLMs configured in the platform will be available as  [Llamaindex](https://www.llamaindex.ai/) `LLM` objects through the Unstract SDK. Refer to [LLamaindex documentaion](https://docs.llamaindex.ai/en/stable/core_modules/model_modules/llms/root.html) for more details on the LLM objects. The tools can use these LLM objects to perform various NLP tasks. 

## Concentrate on the business logic

The SDK and the platform abstracts away the complexities of the underlying components and allows the users to focus on the business logic of their Tools. The SDK provides a convenient interface to the platform to create your own tools. 

Typical steps to create a new tool:

1. Create a new tool scaffolding using the SDK's command line tool
2. Implement the business logic of the tool
3. Test the tool locally
4. Deploy the tool to the platform
