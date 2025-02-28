import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { RunnableLambda } from '@langchain/core/runnables';

const template = ChatPromptTemplate.fromMessages([
  ['system', '당신은 친절한 어시스턴트입니다.'],
  ['human', '{question}'],
]);

const model = new ChatOpenAI({
  model: 'gpt-3.5-turbo',
});

const chatbot = RunnableLambda.from(async function* (values) {
  const prompt = await template.invoke(values);
  for await (const token of await model.stream(prompt)) {
    yield token;
  }
});

for await (const token of await chatbot.stream({
  question: '거대 언어 모델은 어디서 제공하나요?',
})) {
  console.log(token);
}
