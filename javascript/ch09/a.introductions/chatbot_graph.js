import { DuckDuckGoSearch } from '@langchain/community/tools/duckduckgo_search';
import { Calculator } from '@langchain/community/tools/calculator';
import { ChatOpenAI } from '@langchain/openai';
import { OpenAIEmbeddings } from '@langchain/openai';
import { Document } from '@langchain/core/documents';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import {
  StateGraph,
  Annotation,
  messagesStateReducer,
  START,
} from '@langchain/langgraph';
import { ToolNode, toolsCondition } from '@langchain/langgraph/prebuilt';

async function createGraph() {
  const search = new DuckDuckGoSearch();
  const calculator = new Calculator();
  const tools = [search, calculator];

  const embeddings = new OpenAIEmbeddings();
  const model = new ChatOpenAI({ temperature: 0.1 });

  // 벡터 저장소와 검색기 생성
  const toolsStore = await MemoryVectorStore.fromDocuments(
    tools.map(
      (tool) =>
        new Document({
          pageContent: tool.description,
          metadata: { name: tool.constructor.name },
        })
    ),
    embeddings
  );
  const toolsRetriever = toolsStore.asRetriever();

  const annotation = Annotation.Root({
    messages: Annotation({ reducer: messagesStateReducer, default: () => [] }),
    selected_tools: Annotation(),
  });

  async function modelNode(state) {
    const selectedTools = tools.filter((tool) =>
      state.selected_tools.includes(tool.constructor.name)
    );
    const res = await model.bindTools(selectedTools).invoke(state.messages);
    return { messages: res };
  }

  async function selectTools(state) {
    const query = state.messages[state.messages.length - 1].content;
    const toolDocs = await toolsRetriever.invoke(query);
    return {
      selected_tools: toolDocs.map((doc) => doc.metadata.name),
    };
  }

  const builder = new StateGraph(annotation)
    .addNode('select_tools', selectTools)
    .addNode('model', modelNode)
    .addNode('tools', new ToolNode(tools))
    .addEdge(START, 'select_tools')
    .addEdge('select_tools', 'model')
    .addConditionalEdges('model', toolsCondition)
    .addEdge('tools', 'model');

  return builder.compile().withConfig({
    runName: 'ChatbotGraph',
  });
}

export const graph = await createGraph();
