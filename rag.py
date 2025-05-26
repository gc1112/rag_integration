class Rag():
    import langchain
    langchain.verbose = False #do not touch setting, dont work without it
    langchain.debug = False
    langchain.llm_cache = False
    from langchain_ollama import OllamaEmbeddings
    from langchain_community.document_loaders import CSVLoader
    from langchain_community.vectorstores import FAISS #using cpu version, chang to gpu on server
    import re
    import os
    import pandas as pd

    def __init__(self,db,OLLAMA_SERVER_URL, model):
        """
        db: name of local db to create\n
        url: url of ollama server to connect to\n
        model: name of the model to connect at url
        """
        self.db = db
        self.__set_o_embed(OLLAMA_SERVER_URL,model) # OllamaEmbeddings cannot run in init, had to use this bypass , otherwise cannot pass model, url to o_embed
    
    o_embed = None 
    def __set_o_embed(self,url,model):
        self.o_embed=self.OllamaEmbeddings( 
            model=model,
            base_url=url)

    def add_vector_store(self,f_path):
        """
        append to created vector store from file path\n
        if not found, creates vector store
        """
        print("load started")
        loader = self.CSVLoader(file_path=f_path, encoding="UTF-8")
        documents = loader.load()
        data = self.pd.read_csv(f_path)

        

        if not self.os.path.exists(self.db): #couldnt get create empty db to work, had to use this 
            ov = self.FAISS.from_documents(
                documents=documents,
                embedding=self.o_embed)   
            data.to_csv('data.csv')
            print("created db")  
        else:
            print("using existing db")
            ov=self.FAISS.load_local(self.db,self.o_embed, allow_dangerous_deserialization=True)
            ov.add_documents(
            documents=documents, 
            embedding=self.o_embed)
            old_data = self.pd.read_csv('data.csv')
            self.pd.concat([data,old_data]).drop_duplicates(keep=False)
        ov.save_local(self.db)     
        print("load ended")         
    
    def submit_query(self,query):#regular rag retrieve
        o_vectstore = self.FAISS.load_local(self.db,self.o_embed, allow_dangerous_deserialization=True)
        retriever = o_vectstore.as_retriever()
        page_content_retrieved = ""
        try:
            docs_retrieved = retriever.invoke(query)
            for doc in docs_retrieved:
                page_content_retrieved += f"{doc.page_content}\n"
            return page_content_retrieved
        except FileNotFoundError:
            return "embedding file not found, check if it is created and name is correct"
    

    def query_parser(self,query, keywords = ["vector", "cause", "asset", "consequence"]):
        """
        parse query from user, produce prompt that can be sent to ollama\n
        check if keyword exists and match anything after it until the next keyword\n
        if no other keywords exist, match till end of string\n
        key words can be anything, defaults are "vector", "cause", "asset", "consequence"
        """
        query = query.replace('<br>', '\n').replace('\r\n', '\n')
        query = ' '.join(query.split()) 
        seperator = '|'.join(keywords)+'|$'
        prompt = ""
        for i in keywords:
            if i in query:
                pattern = f'{i}(.*?)({seperator})'
                result = self.re.search(pattern, query, self.re.DOTALL | self.re.IGNORECASE)
                prompt += f"{i} is {result.group(1).strip()}," #TODO test prompt format to seperate value pairs
        print(prompt)
        return prompt
    
    def get_data(self):
        data = self.pd.read_csv("data.csv")