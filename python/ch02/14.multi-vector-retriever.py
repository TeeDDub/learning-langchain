from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
import uuid

connection = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'
collection_name = 'summaries'
embeddings_model = OpenAIEmbeddings()

# 문서 로드
loader = TextLoader('./test.txt', encoding='utf-8')
docs = loader.load()

print('length of loaded docs: ', len(docs[0].page_content))

# 문서 분할
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 나머지 코드는 동일하게 유지
prompt_text = '다음 문서의 요약을 생성하세요:\n\n{doc}'

prompt = ChatPromptTemplate.from_template(prompt_text)
llm = ChatOpenAI(temperature=0, model='gpt-4o-mini')
summarize_chain = {
    'doc': lambda x: x.page_content} | prompt | llm | StrOutputParser()

summaries = summarize_chain.batch(chunks, {'max_concurrency': 5})

# 벡터 저장소는 하위 청크를 인덱싱하는 데 사용
vectorstore = PGVector(
    embeddings=embeddings_model,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)
# 상위 문서를 위한 스토리지 레이어
store = InMemoryStore()
id_key = 'doc_id'

# 원본 문서를 문서 저장소에 보관하면서 벡터 저장소에 요약을 인덱싱
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    id_key=id_key,
)

# 문서와 동일한 길이가 필요하므로 summaries에서 chunks로 변경
doc_ids = [str(uuid.uuid4()) for _ in chunks]

# 각 요약은 doc_id를 통해 원본 문서와 연결
summary_docs = [
    Document(page_content=s, metadata={id_key: doc_ids[i]})
    for i, s in enumerate(summaries)
]

# 유사도 검색을 위해 벡터 저장소에 문서 요약을 추가
retriever.vectorstore.add_documents(summary_docs)

# doc_ids를 통해 요약과 연결된 원본 문서를 문서 저장소에 저장
# 이를 통해 먼저 요약을 효율적으로 검색한 다음, 필요할 때 전체 문서를 가져옴
retriever.docstore.mset(list(zip(doc_ids, chunks)))

# 벡터 저장소가 요약을 검색
sub_docs = retriever.vectorstore.similarity_search(
    'chapter on philosophy', k=2)

print('sub docs: ', sub_docs[0].page_content)

print('length of sub docs:\n', len(sub_docs[0].page_content))

# retriever는 더 큰 원본 문서 청크를 반환
retrieved_docs = retriever.invoke('chapter on philosophy')

print('length of retrieved docs: ', len(retrieved_docs[0].page_content))
