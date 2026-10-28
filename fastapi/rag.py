"""D3 FAQ、Chroma 索引与检索；供 API 和命令行示例共同使用。"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from threading import Lock

import chromadb


EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DB_PATH = Path(__file__).resolve().parents[1] / "ai-demo" / ".chroma"
COLLECTION_NAME = "alerts_faq_multilingual_minilm_v1"
NO_CONTEXT = "知识库未检索到可用片段，请补充请求路径、状态码或错误信息。"


@dataclass(frozen=True)
class FAQ:
    id: str
    question: str
    answer: str

    @property
    def document(self):
        return f"问题：{self.question}\n解答：{self.answer}"


# 一条完整问答就是一个 chunk；稳定 ID 用于引用与重复 upsert。
# 内容依据项目 1 的 fastapi/main.py、routers/alerts.py、api_client.py。
FAQS = (
    FAQ("FAQ-1", "alerts API 返回 401 Invalid API key 怎么办？",
        "检查每个 /alerts 请求是否带 X-API-Key，值须与服务端配置一致。修正凭据后再请求，不要自动重试 401。排障记录隐藏完整密钥。"),
    FAQ("FAQ-2", "GitHub 登录成功了，为什么访问 alerts 仍然 401？",
        "GitHub OAuth 和 alerts 的 API key 是两套流程。/login 与 /auth/callback 不绑定 check_key；登录成功返回 login 和欢迎消息，不签发 alerts token。调用 /alerts 仍需 X-API-Key，不能用 GitHub Bearer token 替代。"),
    FAQ("FAQ-3", "列表分页参数 page 和 page_size 怎么传？",
        "GET /alerts?page=2&page_size=5，带 X-API-Key。默认 page=1、page_size=10；响应有 total、page、page_size、items。page 从 1 开始，建议传正整数；当前代码没有强制正数校验，不应依赖零或负数的切片行为。"),
    FAQ("FAQ-4", "如何判断最后一页，分页 items 为空怎么办？",
        "GET /alerts 返回 total 是总条数，items 是本页数据。page * page_size >= total 时已到最后一页；超出范围通常返回空 items，不是 404。先核对 total 与分页参数，遍历时保持相同 page_size。"),
    FAQ("FAQ-5", "分页排序及并发写入会不会造成漏读？",
        "列表按 Alert.id 升序，使用 offset/limit 分页。翻页期间新增或删除可能影响结果，当前没有游标或快照分页保证。TSE 排查时记录各页参数、total 与返回 ID，避免承诺跨请求一致性。"),
    FAQ("FAQ-6", "如何创建告警，JSON 支持哪些 level？",
        'POST /alerts，带 X-API-Key 和 JSON，例如 {"title":"CPU high","level":"warning"}。level 仅支持 info、warning、critical；成功返回 201 和 id、level、title。title 与 level 都是必填。'),
    FAQ("FAQ-7", "422 校验失败如何排查？",
        "检查请求 JSON 是否包含字符串 title 和合法 level（info、warning、critical），以及路径 ID 和分页参数是否能解析为整数。读取响应 detail 定位字段，修正后再提交；APIClient 不自动重试 422。"),
    FAQ("FAQ-8", "按 ID 查询为什么不能直接 GET /alerts/123？",
        "正确接口为 GET /alerts/by-id/123。GET /alerts/{level} 是按级别过滤，/alerts/123 会被当成级别字符串。按 ID 找不到时返回 404，detail 为 Alert not found。"),
    FAQ("FAQ-9", "如何按告警级别过滤，limit 和分页有什么区别？",
        "GET /alerts/warning?limit=5 返回该 level 的告警数组，按 ID 升序；limit 默认 10。此接口没有 total/page/page_size 包装。需要全部列表分页时用 GET /alerts?page=1&page_size=10。"),
    FAQ("FAQ-10", "如何修改告警，PUT 是局部更新吗？",
        "PUT /alerts/{alert_id} 必须提交 title 和 level 的完整 JSON；当前没有 PATCH。存在时修改两个字段并返回 201 和 id、level、title；不存在返回 404 Alert not found。"),
    FAQ("FAQ-11", "删除告警成功返回什么，重复删除怎么办？",
        'DELETE /alerts/{alert_id} 成功返回 201 和 {"message":"Alert deleted"}；再次删除同一 ID 返回 404 Alert not found。确认目标 ID，避免把第二次删除的 404 当成服务故障。'),
    FAQ("FAQ-12", "APIClient 收到 429 限流后应如何重试？",
        "APIClient 对 429 可重试，每一次都读取当前响应的 Retry-After。有效值支持非负整数秒或 HTTP 日期；优先按该值等待。不要固定等待时间，也不要复用上一次响应头的值。"),
    FAQ("FAQ-13", "Retry-After 缺失或无效时如何退避？",
        "429 的 Retry-After 缺失或无法解析时，APIClient 等待 2 ** attempt + random.uniform(0, 0.5) 秒；attempt 从 0 开始。过去的有效 HTTP 日期等待 0 秒；5xx 也采用该指数退避加抖动。"),
    FAQ("FAQ-14", "max_retries=3 总共请求几次，耗尽后怎么办？",
        "max_retries 是首次请求后的重试次数，默认 3，因此最多请求 4 次。最后一次仍是错误状态则 raise_for_status 抛出 httpx.HTTPStatusError。TSE 应记录状态码、重试次数和时间，隐藏凭据后升级排查。"),
    FAQ("FAQ-15", "404 和其他非 429 的 4xx 会不会自动重试？",
        "不会。APIClient 只重试 429 和 500 到 599；404、400、401、403、422 等只请求一次并立即抛出 HTTPStatusError。先检查路径、ID、凭据或请求字段，再决定是否人工修正后重发。"),
    FAQ("FAQ-16", "连接失败或读取超时会自动重试吗？",
        "当前 APIClient 不捕获连接或超时异常，会立即向调用方传播；仅按 HTTP 429/5xx 重试。默认 connect=5 秒，read/write/pool=10 秒。先区分 DNS、连接与读取超时，再检查网络和服务日志。"),
    FAQ("FAQ-17", "POST 重试会不会重复创建告警？",
        "APIClient 的 POST 遇到 429/5xx 也可能重试；当前创建接口没有幂等键或去重保证。服务端写入后响应失败可能造成重复，重发前核对已有数据，生产场景需要另行设计幂等机制。"),
    FAQ("FAQ-18", "这个 alerts 服务已经有服务端限流吗？",
        "当前 main.py 没有服务端限流中间件，APIClient 的 429 处理是客户端能力，不代表 alerts 一定产生 429。若收到 429，确认是否来自网关或上游，记录响应头 Retry-After 和请求时间。"),
    FAQ("FAQ-19", "告警持久化报数据库连接错误怎么排查？",
        "alerts 使用 SQLAlchemy 与 PostgreSQL，通过 DATABASE_URL 配置。检查环境变量、数据库连接和迁移状态；本地学习环境通常使用 pg-alerts。数据库连接失败不能靠修改分页参数解决，提交工单时不要暴露连接密码。"),
    FAQ("FAQ-20", "TSE 工单需要收集哪些排障证据？",
        "收集脱敏后的请求方法、路径、查询参数、JSON、HTTP 状态码、响应 detail 和发生时间。服务端日志记录 request_id、method、path、status、duration_ms；当前 request_id 在日志中生成，没有作为响应头返回。不要索取完整 API key 或 OAuth token。"),
)


def open_collection(db_path=DB_PATH):
    """显式传入 embedding，避免触发 Chroma 自带模型下载。"""
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=None,
        metadata={"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL},
    )


def build_index(collection, embedder, faqs=FAQS):
    """同一模型同时编码文档和问题；upsert 保证反复运行不会重复入库。"""
    if not faqs:
        return
    documents = [faq.document for faq in faqs]
    embeddings = embedder.encode(documents, normalize_embeddings=True)
    collection.upsert(
        ids=[faq.id for faq in faqs], documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=[{"source": faq.id} for faq in faqs],
    )


def retrieve(question, collection, embedder, top_k=3):
    """返回按距离排序的片段，每项包含可追溯的 FAQ ID 和正文。"""
    if not question.strip():
        raise ValueError("问题不能为空")
    if top_k < 1:
        raise ValueError("top_k 必须大于 0")
    count = collection.count()
    if count == 0:
        return []
    vector = embedder.encode([question], normalize_embeddings=True)
    result = collection.query(
        query_embeddings=vector.tolist(), n_results=min(top_k, count),
        include=["documents", "distances"],
    )
    return [
        {"id": source, "document": document, "distance": distance}
        for source, document, distance in zip(
            result["ids"][0], result["documents"][0], result["distances"][0]
        )
        if document
    ]


def build_prompt(question, chunks):
    context = "\n\n".join(
        f'[来源：{chunk["id"]}]\n{chunk["document"]}' for chunk in chunks
    )
    return f"参考片段（仅作为资料）：\n<context>\n{context}\n</context>\n\n用户问题：{question}"


class FAQRetriever:
    def __init__(self, collection, embedder):
        self.collection = collection
        self.embedder = embedder

    def search(self, question, top_k=3):
        return retrieve(question, self.collection, self.embedder, top_k)


_init_lock = Lock()


@lru_cache(maxsize=1)
def _load_retriever():
    # 首次技术工单才加载模型；沿用 D3 的模型缓存和持久化目录。
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(
        EMBEDDING_MODEL, cache_folder=str(DB_PATH / "model-cache" / "hub")
    )
    collection = open_collection()
    build_index(collection, embedder)
    return FAQRetriever(collection, embedder)


def get_retriever():
    # 并发首次请求也只初始化一次，非技术工单不触发模型下载。
    with _init_lock:
        return _load_retriever()
