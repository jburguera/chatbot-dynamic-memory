# Architecture Documentation

## System Overview

The Chatbot Dynamic Memory System implements a **hybrid memory architecture** that combines the strengths of both short-term and long-term memory approaches to optimize chatbot context management.

## Design Philosophy

Traditional chatbot memory solutions fall into two extremes:

1. **Stateless Approach**: No memory between turns (cheap but loses context)
2. **Full History Approach**: Keep everything (expensive, hits token limits)

Our system implements a **middle path** that intelligently balances:
- Recent context (what was just discussed)
- Relevant history (what matters from the past)
- Token efficiency (staying within model limits)

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                            │
│                   (Gradio Interface)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│                                                              │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │   app.py     │────────▶│ Agent Executor  │              │
│  │  (Main Entry)│         │  (Pydantic AI)  │              │
│  └──────────────┘         └────────┬────────┘              │
│                                    │                        │
└────────────────────────────────────┼────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      CORE LAYER                              │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Memory Manager Service                       │  │
│  │                                                         │  │
│  │  ┌──────────────────┐    ┌─────────────────────────┐ │  │
│  │  │ Context Builder  │    │  Token Budget Manager   │ │  │
│  │  └──────────────────┘    └─────────────────────────┘ │  │
│  │                                                         │  │
│  │  ┌──────────────────┐    ┌─────────────────────────┐ │  │
│  │  │ Relevance Scorer │    │  Synthesis Engine       │ │  │
│  │  └──────────────────┘    └─────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────┬──────────────────────┬────────────────────┘
                   │                      │
                   ▼                      ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│  INFRASTRUCTURE LAYER      │  │  INFRASTRUCTURE LAYER    │
│                            │  │                          │
│  ┌──────────────────────┐  │  │  ┌────────────────────┐ │
│  │ Window Memory        │  │  │  │ Vector Store       │ │
│  │ Provider (Redis)     │  │  │  │ Repository         │ │
│  │                      │  │  │  │ (Qdrant)           │ │
│  │ - Last N messages   │  │  │  │                    │ │
│  │ - User isolated     │  │  │  │ - Embeddings       │ │
│  │ - Fast access       │  │  │  │ - Semantic search  │ │
│  └──────────────────────┘  │  │  │ - User filtered    │ │
│                            │  │  └────────────────────┘ │
└────────────────────────────┘  └──────────────────────────┘
                   │                      │
                   ▼                      ▼
           ┌──────────────┐      ┌──────────────────┐
           │    Redis     │      │   Qdrant Cloud   │
           │   Database   │      │  Vector Database │
           └──────────────┘      └──────────────────┘
                                         │
                                         ▼
                                 ┌──────────────────┐
                                 │  OpenAI API      │
                                 │  (Embeddings)    │
                                 └──────────────────┘
```

## Component Details

### 1. Window Memory Provider (Redis)

**Purpose**: Store and retrieve recent conversation history efficiently.

**Implementation**:
- Uses Redis Lists for ordered message storage
- Implements automatic LRU eviction with `LTRIM`
- Provides O(1) access to recent messages
- Ensures user isolation with key prefixing: `memory:{user_id}`

**Data Structure**:
```python
# Redis Key Pattern
key = f"memory:{user_id}"

# Redis List Structure (newest first)
[
    {"role": "assistant", "content": "...", "timestamp": "..."},
    {"role": "user", "content": "...", "timestamp": "..."},
    ...
]
```

**Operations**:
- `add_turn()`: Push new message and trim to window size
- `get_window()`: Retrieve last N messages
- `clear()`: Delete user's conversation history

### 2. Vector Store Repository (Qdrant)

**Purpose**: Enable semantic search over historical conversations.

**Implementation**:
- Stores conversation embeddings in Qdrant collections
- Each document contains: `user_id`, `message`, `embedding`, `metadata`
- Uses OpenAI's `text-embedding-3-small` (1536 dimensions)
- Implements cosine similarity for relevance scoring

**Collection Schema**:
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "user_id": {"type": "keyword", "indexed": true},
    "message": {"type": "text"},
    "role": {"type": "keyword"},
    "timestamp": {"type": "integer"},
    "session_id": {"type": "keyword"}
  }
}
```

**Search Flow**:
1. Generate embedding for current query
2. Search with user_id filter
3. Return top K results above relevance threshold
4. Sort by similarity score

### 3. Memory Manager Service

**Purpose**: Orchestrate memory components and synthesize context.

**Key Responsibilities**:

#### 3.1 Context Retrieval
```python
async def get_context(query: str, user_id: UUID) -> list[Message]:
    # 1. Get recent window from Redis
    window_messages = await window_provider.get_window(user_id)
    
    # 2. Get relevant history from Qdrant
    relevant_messages = await vector_store.search(
        query=query,
        user_id=user_id,
        limit=RETRIEVAL_LIMIT,
        threshold=RELEVANCE_THRESHOLD
    )
    
    # 3. Synthesize unified context
    context = synthesize(window_messages, relevant_messages)
    
    # 4. Apply token budget
    return trim_to_budget(context, MAX_TOKENS)
```

#### 3.2 Context Synthesis Strategy

**Deduplication**: Remove duplicates between window and retrieved messages
**Chronological Ordering**: Maintain conversation flow
**Relevance Weighting**: Prioritize high-relevance retrieved messages
**Recency Bias**: Always include recent window messages

#### 3.3 Token Budget Management

```python
def trim_to_budget(messages: list[Message], max_tokens: int) -> list[Message]:
    """
    Intelligent trimming strategy:
    1. Always keep most recent message (user query)
    2. Include window messages if they fit
    3. Add retrieved messages in order of relevance
    4. Stop when budget is reached
    """
    # Implementation details...
```

### 4. Embedding Provider (OpenAI)

**Purpose**: Generate semantic embeddings for messages.

**Configuration**:
- Model: `text-embedding-3-small`
- Dimensions: 1536
- Cost: ~$0.02 per 1M tokens

**Usage**:
```python
async def generate_embedding(text: str) -> list[float]:
    response = await openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

## Data Flow

### Message Processing Flow

```
1. User sends message
   │
   ├─▶ 2a. Generate embedding for semantic search
   │
   ├─▶ 2b. Retrieve window messages from Redis
   │       (Last N messages)
   │
   ├─▶ 2c. Search Qdrant for relevant history
   │       (Top K by cosine similarity, filtered by user_id)
   │
   └─▶ 3. Synthesize context
       │
       ├─▶ Deduplicate messages
       ├─▶ Order chronologically
       ├─▶ Apply token budget
       │
       └─▶ 4. Send to LLM with synthesized context
           │
           └─▶ 5. Store turn in Redis + Qdrant
               │
               ├─▶ Redis: Add to window (LPUSH + LTRIM)
               └─▶ Qdrant: Store with embedding
```

### Memory Storage Flow

```
After LLM Response:
│
├─▶ 1. Store in Window Memory (Redis)
│   └─▶ LPUSH memory:{user_id} {turn_data}
│   └─▶ LTRIM memory:{user_id} 0 {window_size-1}
│
└─▶ 2. Store in Vector Memory (Qdrant)
    └─▶ Generate embedding
    └─▶ Upsert point with user_id payload
```

## Configuration Parameters

### Memory Configuration

| Parameter | Default | Description | Tuning Guide |
|-----------|---------|-------------|--------------|
| `WINDOW_SIZE` | 10 | Recent messages to keep | Increase for longer short-term context |
| `MEMORY_RETRIEVAL_LIMIT` | 5 | Max historical messages | Balance between context and latency |
| `MEMORY_RELEVANCE_THRESHOLD` | 0.7 | Min similarity score (0-1) | Lower = more inclusive retrieval |
| `MAX_CONTEXT_TOKENS` | 3000 | Token budget for context | Based on model's context window |

### Performance Tuning

**Latency Optimization**:
- Redis window access: <10ms
- Qdrant search: 50-200ms (depends on collection size)
- OpenAI embedding: 100-300ms
- **Total p95**: <500ms

**Cost Optimization**:
- Embeddings are cached in Qdrant
- Only new messages generate embeddings
- Window memory uses no embeddings

**Accuracy Optimization**:
- Adjust `RELEVANCE_THRESHOLD` based on use case
- Higher threshold = more precise, fewer results
- Lower threshold = more recall, potential noise

## User Isolation

**Security Model**: Strict user-level isolation at every layer.

### Redis Isolation
```python
# Key pattern ensures separation
key = f"memory:{user_id}"

# No cross-user access possible
```

### Qdrant Isolation
```python
# Search with mandatory user_id filter
query_filter = Filter(
    must=[
        FieldCondition(
            key="user_id",
            match=MatchValue(value=str(user_id))
        )
    ]
)
```

**Benefits**:
- Complete privacy between users
- No data leakage risk
- Efficient multi-tenancy

## Scalability Considerations

### Horizontal Scaling

**Stateless Design**: Application layer can scale horizontally
**Shared State**: Redis and Qdrant handle concurrent access
**Load Balancing**: Standard load balancer works (no sticky sessions needed)

### Database Scaling

**Redis**:
- Use Redis Cluster for horizontal scaling
- Partition by user_id hash slot
- Typical: 10K-100K users per node

**Qdrant**:
- Use Qdrant Cloud with auto-scaling
- Or self-host with horizontal sharding
- Collections can handle millions of vectors

### Cost Scaling

**Storage Costs**:
- Redis: ~$0.10/GB/month (managed)
- Qdrant: ~$0.50/GB/month (depends on provider)
- Embeddings: ~$0.02 per 1M tokens

**Expected Costs** (per 1000 active users):
- Redis: ~$10/month (assuming 1MB per user)
- Qdrant: ~$50/month (assuming 5MB per user)
- Embeddings: ~$5/month (assuming 100 messages/user/month)
- **Total**: ~$65/month + LLM inference costs

## Design Decisions & Trade-offs

### Why Redis for Window Memory?

**Chosen**: Redis Lists
**Alternatives Considered**: In-memory Python dict, PostgreSQL

**Reasoning**:
✅ Persistence across restarts
✅ Fast access (O(1) operations)
✅ Battle-tested for high concurrency
✅ Native support for LRU eviction
❌ Slightly higher latency than in-memory (acceptable trade-off)

### Why Qdrant for Vector Store?

**Chosen**: Qdrant Cloud
**Alternatives Considered**: MongoDB Atlas Vector Search, Pinecone, Weaviate

**Reasoning**:
✅ Purpose-built for vector search (optimized performance)
✅ Excellent filtering capabilities (user_id isolation)
✅ Competitive pricing
✅ Easy self-hosting option
❌ Newer than alternatives (but proven in production)

### Why Not LangGraph for Orchestration?

**Decision**: Removed LangGraph in favor of functional service

**Original Plan**: Use LangGraph for memory decision logic
**Pivot Reason**: Overhead not justified for simple conditional logic

**Current Approach**:
```python
# Simple, testable function
async def get_context(...):
    window = await get_window()
    relevant = await search_vector()
    return synthesize(window, relevant)
```

**Benefits**:
✅ Simpler codebase
✅ Easier to test and debug
✅ No state graph complexity
✅ Faster execution

## Future Enhancements

### Phase 1: Core Improvements
- [ ] Conversation summarization for ultra-long contexts
- [ ] Memory decay/forgetting mechanisms
- [ ] Multi-modal memory (images, files, audio)

### Phase 2: Intelligence
- [ ] Automatic topic extraction from history
- [ ] User preference learning
- [ ] Proactive context suggestion

### Phase 3: Enterprise
- [ ] Organization-level shared memory
- [ ] Compliance and retention policies
- [ ] Advanced analytics dashboard

## Testing Strategy

### Unit Tests
- Memory provider operations (CRUD)
- Embedding generation
- Context synthesis logic
- Token budget enforcement

### Integration Tests
- End-to-end message flow
- User isolation verification
- Performance benchmarks
- Edge cases (empty history, large contexts)

### Load Tests
- Concurrent user simulation
- Database connection pooling
- Memory leak detection
- Latency under load

## Monitoring & Observability

### Key Metrics

**Performance**:
- Memory retrieval latency (p50, p95, p99)
- Embedding generation time
- Context synthesis time

**Quality**:
- Relevance score distribution
- Context hit rate (found relevant history)
- Token utilization (avg context size)

**Reliability**:
- Redis connection health
- Qdrant search errors
- OpenAI API errors

### Logging Strategy

```python
# Structured logging for observability
logger.info(
    "memory_retrieval",
    user_id=user_id,
    window_size=len(window_messages),
    retrieved_count=len(relevant_messages),
    total_tokens=token_count,
    latency_ms=elapsed_time
)
```

## Conclusion

This architecture provides a robust, scalable foundation for chatbot memory management. The hybrid approach balances the trade-offs between:
- Context quality and token efficiency
- Latency and accuracy
- Simplicity and capability

The modular design allows for easy experimentation and iteration on individual components without affecting the whole system.
