# English Version

# Postmortem: Incorrect Data on the First Pagination Page

- **Symptoms**: GET /alerts returns the wrong paginated data (page 1 returns IDs 3 and 4 instead of 1 and 2).
- **Impact**: All paginated query results are shifted, and the last page of data is inaccessible. The status code is 200, making the issue hard for users to notice.
- **Investigation**: Reproduce with curl → check JSON logs to confirm the request parameters and 200 status → search the repository for page_size to locate the code → compare it with the correct implementation in responsedata.py.
- **Root cause**: In routers/alerts.py, start = page * page_size does not convert from 1-based page numbering to 0-based indexing (an off-by-one error).
- **Fix**: Change it to start = (page - 1) * page_size.
- **Regression testing**: Add a test that asserts the actual IDs returned (the existing tests only asserted the length and could not catch this bug).
- **Lessons learned**: Assertions should verify content as well as length. Keep multiple implementations of the same functionality consistent.

---

# Postmortem: 分页第一页数据错位
- **症状**：GET /alerts 分页返回错误数据（page 1 返回 id 3、4 而非 1、2）
- **影响**：所有分页查询结果错位，最后一页数据不可达；状态码 200，用户不易察觉
- **排查过程**：curl 复现 → 查 JSON 日志确认请求参数与 200 状态 → 全仓搜索 page_size 定位 → 对照 responsedata.py 的正确实现
- **根因**：routers/alerts.py 中 start = page * page_size，未做 1-based 到 0-based 的转换（off-by-one）
- **修复**：改为 start = (page - 1) * page_size
- **回归测试**：新增断言 id 内容的测试（原有测试只断言长度，抓不到此 bug）
- **经验教训**：断言要验内容不只验长度；同功能多处实现时保持一致
