"""
- Windows는 지원되지 않음.
- 파이썬에서만 사용 가능함.
- 전체 문서는 여기서 확인할 수 있음: https://github.com/AnswerDotAI/RAGatouille/blob/8183aad64a9a6ba805d4066dcab489d97615d316/README.md

- 설치하려면 다음 명령어를 실행

```bash
pip install -U ragatouille transformers
```
"""
from ragatouille import RAGPretrainedModel
import requests

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")


def get_wikipedia_page(title: str):
    """
    위키피디아 페이지의 전체 텍스트 내용을 가져옴.

    :param title: str - 위키피디아 페이지의 제목
    :return: str - 페이지의 전체 텍스트 내용을 raw 문자열로 반환
    """
    # 위키피디아 API 엔드포인트
    URL = "https://en.wikipedia.org/w/api.php"

    # API 요청을 위한 매개변수
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
    }

    # 위키피디아의 모범 사례를 준수하기 위한 사용자 정의 User-Agent 헤더
    headers = {"User-Agent": "RAGatouille_tutorial/0.0.1"}

    response = requests.get(URL, params=params, headers=headers)
    data = response.json()
    
    # 페이지 내용 추출
    page = next(iter(data["query"]["pages"].values()))
    return page["extract"] if "extract" in page else None


full_document = get_wikipedia_page("Hayao_Miyazaki")

# 인덱스 생성
RAG.index(
    collection=[full_document],
    index_name="Miyazaki-123",
    max_document_length=180,
    split_documents=True,
)

# 쿼리
results = RAG.search(query="What animation studio did Miyazaki found?", k=3)

print(results)

# 랭체인의 리트리버 사용
retriever = RAG.as_langchain_retriever(k=3)
retriever.invoke("What animation studio did Miyazaki found?")
