# English Version

Ticket #2001: The user says, "I included an API key, but the request still returns 401. Is your authentication broken?" The header in the request they shared is X-Api-Key: dev-secret-key (pay attention to capitalization and spelling).

- **Priority**: P3
- **Reproduction steps**: Unable to reproduce.
  1. Check the logs: Was there actually a 401 during the reported time window? If so, match the request path and timestamp to confirm that the request reached the server.
  2. Ask the user for the exact request: Ask them to copy the actual request directly from their tool (a curl command or a Postman screenshot), rather than describe it. Focus on the key value:
     - A typo in the value (dev-secret-kye).
     - Leading or trailing spaces.
     - A key from the wrong environment (using a production key against a test server).
     - The tool did not send the header at all (some clients require a checkbox to enable it).
- **Root cause hypothesis**: The key value is most likely incorrect; the header name is unlikely to be the cause.
- **Decision**: Neither close nor escalate yet. First ask the user for the exact request and check the logs; classify the issue once evidence is available.

Ticket #2002: The user says, "POST /alerts keeps returning 422, but my JSON format is clearly correct." Their request body is {"title": "Server down", "level": "HIGH"}.

- **Priority**: P3. One user is affected, and changing a value resolves the issue.
- **Reproduction steps**:

```powershell
curl.exe -X POST -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" --% -d "{\"title\": \"Server down\", \"level\": \"HIGH\"}" http://127.0.0.1:8000/alerts
```

- **Root cause hypothesis**: The user supplied HIGH, which is outside the allowed enum values. The API rejects it as designed: 422 is the correct behavior, not a bug (the value is invalid).
- **Decision**: Close the ticket and reply with the three allowed values. Suggest a documentation improvement: make the enum values more prominent.

Ticket #2003: The user says, "All three alerts I created yesterday are gone today! Did you lose my data?" An operations colleague adds that the service restarted last night.

(The data is temporarily stored in memory, so last night's restart cleared it.)

- **Priority**: P2
- **Reproduction steps**: -
- **Root cause hypothesis**: -
- **Decision**: Escalate to the engineering/product team with the title "Data is not persisted and is lost on restart; database storage is needed."

Template:

## Ticket #2001

- **Priority**: P? — One-sentence justification (who is affected and how severe it is).
- **Reproduction steps**: 1. ... 2. ... (Actually send the request described by the user and record what you sent and what response you received.)
- **Root cause hypothesis**: An evidence-based hypothesis (what the logs show and how the code is written).
- **Decision**: Escalate / Close — Explain why (is it a product bug or a user issue? What should the user do next?).

Assess priority across three dimensions:

| Priority | Criteria | Example |
| --- | --- | --- |
| P1 | Complete system outage / data loss / all users affected | Service-wide 500 errors; database lost |
| P2 | Core functionality broken / a group of users affected / no workaround | A feature fails for everyone |
| P3 | A single user's issue / a workaround exists | Configuration or usage errors that can be resolved with guidance |
| P4 | Questions, unclear documentation, or user mistakes | "What does this parameter mean?" |

Rule of thumb: scope of impact × severity × availability of a workaround. The wider the impact and the fewer the workarounds, the higher the priority.

---






单#2001：用户说"我带了 API Key，请求还是 401。你们的鉴权是不是坏了？"——他贴出的请求里 header 写的是 X-Api-Key: dev-secret-key（注意大小写和拼写）。

- **分级**：P3
- **复现步骤**：复现不出来. 1. 查日志：在他报障的时间段，日志里有没有真的 401？有的话，那次请求的 path、时间能对上号——证明他确实打到了服务器
                2.让用户提供原样请求：不要他转述，要他从工具里原样复制他实际发的那条（curl命令或 Postman 截图）。重点盯 key 的值：
                    值打错一位（dev-secret-kye）
                    值首尾多了空格
                    用错环境的 key（拿生产的 key 打测试服）
                    工具根本没把 header 发出去（有些客户端要勾选才生效）
- **根因假设**：大概率是 key 值本身有误，而非 header 名
- **判定**：不关闭、不升级——先回用户索取原样请求 + 查日志确认，拿到证据再定性

单#2002：用户说"POST /alerts 一直 422，我的 JSON 格式明明没问题。"他发来的 body 是 {"title": "Server down", "level": "HIGH"}。

- **分级**：P3 单个用户、改个值就能用
- **复现步骤**：curl.exe -X POST -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" --% -d "{\"title\": \"Server down\", \"level\": \"HIGH\"}" http://127.0.0.1:8000/alerts

- **根因假设**：用户传了枚举外的值 HIGH，API 按设计拒绝——422 是正确行为，不是 bug（取值错）
- **判定**：关闭 + 回复用户三个合法值；一条文档改进建议（在文档里把枚举值写显眼点）

单#2003：用户说"昨天我创建的 3 条告警，今天全不见了！你们是不是把数据弄丢了？"——运维同事补充：昨晚服务重启过一次。
(数据暂存在内存，昨晚服务重启所以清空)
- **分级**：P2
- **复现步骤**：-
- **根因假设**：-
- **判定**：升级 给工程/产品团队，标题"数据无持久化，重启即丢失，需引入数据库存储"。



temp:
## 工单#2001
- **分级**：P? —— 一句话理由（影响谁、多严重）
- **复现步骤**：1. ... 2. ... （照着用户描述实际打一遍请求，写下你打了什么、回了什么）
- **根因假设**：基于证据的推测（日志里看到什么、代码里怎么写的）
- **判定**：升级 / 关闭 —— 理由（是产品 bug 还是用户问题？用户下一步该做什么？）

分级看三个维度
级别	标准	例子
P1	系统全挂 / 数据丢失 / 所有用户受影响	服务 500 全线、数据库没了
P2	核心功能坏了 / 一批用户受影响 / 没绕法	某功能对所有人报错
P3	单个用户的问题 / 有 workaround	配置错、用法错，能指导解决
P4	咨询、文档不清、用户误操作	"这个参数什么意思"
判断口诀：影响范围 × 严重程度 × 有没有绕法。范围越大、越没绕法，级别越高。