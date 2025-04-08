from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client()

# 데이터셋 제작
examples = [
    ("어느 나라의 고객이 가장 많이 지출했나요? 그리고 얼마를 지출했나요?",
     "가장 많이 지출한 나라는 미국으로, 총 지출액은 $523.06입니다"),
    ("2013년에 가장 많이 구매된 트랙은 무엇인가요?",
     "2013년에 가장 많이 구매된 트랙은 Hot Girl입니다."),
    ("Led Zeppelin 아티스트는 몇 개의 앨범을 가지고 있나요?",
     "Led Zeppelin은 14개의 앨범을 가지고 있습니다"),
    ("'Big Ones' 앨범의 총 가격은 얼마인가요?",
     "'Big Ones' 앨범의 총 가격은 14.85입니다"),
    ("2009년에 어떤 영업 담당자가 가장 많은 매출을 올렸나요?",
     "Steve Johnson이 2009년에 가장 많은 매출을 올렸습니다"),
]

dataset_name = "sql-agent-response"
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name=dataset_name)
    inputs, outputs = zip(
        *[({"input": text}, {"output": label}) for text, label in examples]
    )
    client.create_examples(
        inputs=inputs, outputs=outputs, dataset_id=dataset.id)
