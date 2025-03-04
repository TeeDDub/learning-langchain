from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    messages: Annotated[list, add_messages]


builder = StateGraph(State)

model = ChatOpenAI(model='gpt-4o-mini')


def chatbot(state: State):
    answer = model.invoke(state['messages'])
    return {'messages': [answer]}


builder.add_node('chatbot', chatbot)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)

# MemorySaver로 영속성 추가
graph = builder.compile(checkpointer=MemorySaver())

# 스레드 설정
thread1 = {'configurable': {'thread_id': '1'}}

# 영속성 추가 후 그래프 실행
result_1 = graph.invoke({'messages': [HumanMessage('안녕하세요, 저는 민혁입니다!')]}, thread1)
result_2 = graph.invoke({'messages': [HumanMessage('제 이름이 뭐죠?')]}, thread1)

# 상태 확인
print(graph.get_state(thread1))

#상태 업데이트
graph.update_state(thread1, {'messages': [HumanMessage('저는 LLM이 좋아요!')]})