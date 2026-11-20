# 02 · Plan（方案设计）

> **阶段任务**：读取澄清文档与相关源码，对 01-clarify §六 的待裁决项做出技术裁决，设计原生 `GET /welcome` 路由、接口契约测试、启动与回滚方案，记录具体文件与命令。**本阶段仅产出方案文档**，不改源码、不跑开发测试、不提交。
> **任务目标（用户授权）**：在当前仓库「现有 Web 服务」中增加原生 `GET /welcome` HTTP 路由，返回 JSON `message=welcome`。
> **分支/工作区**：`feature/wally-experience-7247d256`（平台创建、仓库独立副本；Git 提交由平台收尾）。
> **前序产物**：`00-overview.md`（进度）、`01-clarify.md`（澄清结论与待裁决项）。01 已实地核对：本仓库是 `octop-harness` **库**、无 `app.py`/无既有路由/无 Web 框架、`AGENTS.md:52,191,311` 禁止在库中加入 HTTP server —— 「在现有服务上扩展路由」的前提不成立，并把「落点 / 原生承载技术 / 与库约束取舍 / 是否公共 API」列为进入编码前必须裁决的前置依赖（01 §六、§八）。

---

## 一、结论（先行）

1. **本阶段的核心产出是「裁决 + 可执行方案」**：01 §六 的四项待裁决全部在本阶段定案（§二），前置依赖解除；方案可直接交由 03 Implement + UT + Docs 执行。
2. **裁决要点**：仓库无既有 Web 服务可挂载，因此**新建**一个独立、零新增运行依赖、仅用 Python 标准库 `http.server` 的顶层可运行脚本 `app.py`，承载原生 `GET /welcome`；该脚本**置于发布包 `src/octop_harness` 之外**，使库本身仍不含 HTTP server；`AGENTS.md` 对 HTTP server 的禁止由「用户授权」显式覆盖，并在 `CHANGELOG.md` 与 MR 中记录取舍。
3. **方案已通过只读可行性探针验证**（§三.14）：标准库 `ThreadingHTTPServer` + `BaseHTTPRequestHandler` 在本机解释器上实测 `GET /welcome → 200 / application/json / {"message": "welcome"}`、`GET /other → 404`，零新增依赖即可满足接口契约。
4. **功能验收条件明确且可判定**（§六），与 01 §五 对齐；测试、启动、回滚命令均已具体化（§五、§七）。
5. **阶段边界**：仅复核对源码/配置与写入本文件；未创建 `app.py`/`tests/test_welcome.py`、未改动任何源码、未运行实现/测试命令、未执行 Git 提交。未遇到读取/工具层面的阻塞，不触发「停止并记失败」。

---

## 二、对 01-clarify §六 待裁决项的裁决（本阶段决策）

| # | 01 §六 待裁决项 | 本阶段裁决 | 理由 / 依据 |
|---|------------------|-----------|-------------|
| 1 | 「现有 Web 服务」与仓库不符：是新建最小服务，还是应在宿主？ | **在本仓库新建**一个最小 HTTP 服务（顶层 `app.py`），不迁移到宿主 | 任务明确限定「当前仓库内读写/run」，且用户授权在独立分支落地；01 §八 已把它列为实现前置依赖，交由后续阶段裁决，Plan 即该阶段。仓库内无任何服务可「扩展」，`git ls-files` 无 `app.py`/`routes.py`/`wsgi.py`/`asgi.py`（§三.2–4） |
| 2 | 「原生」的承载技术 | **Python 标准库 `http.server`**（`ThreadingHTTPServer` + `BaseHTTPRequestHandler`），零新增运行依赖 | `pyproject.toml:32-54` 核心依赖无 Web 框架（`httpx` 是客户端，`aiohttp`/`starlette`/`uvicorn` 仅 `uv.lock` 间接依赖、源码未导入）；契合 `AGENTS.md` §7「零依赖优先」与任务「原生」字义；新增运行依赖须先说明理由（`AGENTS.md` 技术约束），本方案无需 |
| 3 | 与 `AGENTS.md:52,191,311`（禁止库内 HTTP server）的取舍 | 以「**放在发布包之外**」把库与 server 解耦，残留的「仓库内出现 HTTP server」由**用户授权覆盖**，并在 `CHANGELOG.md` `## [Unreleased]` 与 MR 显式记录 | hatch wheel 仅打包 `src/octop_harness`（`pyproject.toml:134-146`），顶层 `app.py` 不作为库代码发布，库内不含 HTTP server，最大程度贴合库约束；01 §六.3、`AGENTS.md` §12.7 要求显式记录取舍 |
| 4 | 是否为公共 API | **否**。作为独立可运行脚本，不进 `src/octop_harness/__init__.py` 的 `__all__`，不改 README 公共 API 说明 | 不是库能力，无需 `AGENTS.md:36,347` 的 `__all__`/docstring/README 公共 API 流程，改动范围最小；`__init__.py:61` 导出约定仅库符号适用 |

---

## 三、执行证据（本阶段实际执行的核对动作与结果）

> 01 §二 的证据为前序结论；以下为 **02 阶段为复核并支撑设计而重新实地执行** 的只读动作。

| # | 动作 | 关键结果 |
|---|------|----------|
| 1 | 读 `00-overview.md`、`01-clarify.md` | 确认进度、前序结论与 §六 待裁决项 |
| 2 | Glob `**/app.py` | 全仓无 `app.py` |
| 3 | `git ls-files \| grep -iE '(app\|routes\|wsgi\|asgi\|server)\.py$'` | 仅 `src/octop_harness/acp/server.py` 等 `server.py`；无 `app/routes/wsgi/asgi.py` |
| 4 | 全仓 `grep -rInE '@app\.(get\|post)\|add_route\|add_url_rule\|/welcome\|BaseHTTPRequestHandler\|HTTPServer' src/` | 无任何路由装饰器 / HTTP server 符号；唯一 `welcome` 命中在 CLI REPL 横幅（01 §二.4） |
| 5 | 读 `pyproject.toml` 全文 | 项目 `octop-harness` v1.0.11、`requires-python >=3.12`（:6,8,12）；`dependencies`（:32-54）无 Web 框架；`[project.scripts]` 仅 `octop_harness.cli.main:cli`（:99-100）；pytest 配置（:261-286）、coverage（:288-298）、mypy `files=["src/octop_harness"]` 与 `strict=true`（:207-217）、ruff `src=["src","tests"]`（:152-155） |
| 6 | 读 `Makefile` 全文 | `all: format lint typecheck test`（:106）；`lint/format/typecheck` 仅覆盖 `src tests`（:111,113,119,124）；`test: pytest --cov=octop_harness`（:129）；`install`（:141-148）；`RUN := $(if $(UV),uv run,)`（:23） |
| 7 | 读 `tests/conftest.py` 全文 | 3 个 autouse fixtures，模块顶层 `import octop_harness.agent/config/manager/observability`（:11-14）→ 任何 `tests/` 用例收集都会加载完整依赖；含 HOME 隔离、`teardown_logging`、`HarnessAgent.__init__` 跟踪 |
| 8 | 读 `src/octop_harness/cli/main.py` | Click `cli` group，无 Web/监听端口逻辑 |
| 9 | 读 `src/octop_harness/acp/server.py:1` | "Expose HarnessAgent as an ACP agent over **stdio**"，非 HTTP |
| 10 | 读 `src/octop_harness/__init__.py:40-84` | `__getattr__` 惰性导出 + `__all__`（:61）模式，确认「公共 API」的导出约定所在 |
| 11 | Grep `AGENTS.md` 约束行 | `:36,37`（先写失败测试 / 新增公共 API 流程）、`:40`（ship bar `make all`）、`:52`（库非应用、HTTP server 不在此）、`:156,184`（`make all`/hooks）、`:191,311`（Must not/Do not add HTTP server）、`:347,348`（公共 API / 门禁）、`:385`（未绿不得称完成） |
| 12 | 读 `CHANGELOG.md:1-10` | 存在 `## [Unreleased]`（:8），为取舍记录落点 |
| 13 | `ls examples/`、`ls tests/`、`git branch --show-current`、`git status --short`、`python3 --version`、`uv`/`.venv` 探针 | 分支 `feature/wally-experience-7247d256`；工作树仅 `?? .wally/`；`examples/` 为 12 个编号示例；本机 `python3 3.11.6`（项目要求 ≥3.12）、`uv` 不存在、无 `.venv`（与 01 §二.8 一致，运行环境由平台托管） |
| 14 | **只读可行性探针**（`python3 - <<'PY'`，不写文件）：标准库 `ThreadingHTTPServer` 绑定 `127.0.0.1:0`，`http.client` 真实发起 GET | `GET /welcome → 200 \| application/json \| {"message": "welcome"}`；`GET /other → 404`；`shutdown()+server_close()` 正常退出。证明 §五.1/5.2 的技术路线在本机解释器可行、零新增依赖 |

> 14 号探针仅验证设计可行性，未创建任何仓库文件；`app.py` 与 `tests/test_welcome.py` 留待 03 阶段「先写测试 → 再实现」时创建。

---

## 四、关键文件清单

**核对读取（本阶段已读，作为裁决依据）**

| 文件（含行号） | 角色 / 结论 |
|----------------|-------------|
| `pyproject.toml:6,8,12` | 库身份 v1.0.11、`≥3.12` |
| `pyproject.toml:32-54` | 核心依赖无 Web 框架 → 支持「标准库原生」裁决 |
| `pyproject.toml:99-100` | 唯一启动入口是 CLI，非 Web server；本方案不改动它 |
| `pyproject.toml:134-146` | hatch wheel 仅打包 `src/octop_harness` → 顶层 `app.py` 不入库、不发布 |
| `pyproject.toml:152-155,207-217,261-298` | ruff / mypy strict / pytest / coverage 配置，约束测试与门禁 |
| `Makefile:106,111,113,119,124,129,141-148` | `all`/各门禁目标只覆盖 `src tests`；`install` 命令 |
| `tests/conftest.py:11-14,32-100` | autouse fixtures 顶层 import `octop_harness` → 测试需完整依赖环境 |
| `AGENTS.md:36,37,40,52,156,184,191,311,347,348,385` | 测试约定、库约束、门禁、CHANGELOG 要求 |
| `src/octop_harness/cli/main.py` / `acp/server.py:1` / `__init__.py:61` | CLI/stdio 入口、`__all__` 导出约定 |
| `CHANGELOG.md:8` | `## [Unreleased]` 取舍记录落点 |
| `01-clarify.md` §二/§五/§六/§七/§八 | 前序结论、验收条件、待裁决项、前置依赖 |

**实现阶段将新增/修改（本阶段不创建）**

| 文件 | 动作 | 说明 |
|------|------|------|
| `app.py`（仓库根，新建） | 新增 | 标准库 `http.server` 原生 `/welcome` 路由，独立可运行脚本，发布包之外 |
| `tests/test_welcome.py`（新建） | 新增 | 接口契约测试（真实 loopback HTTP），先红后绿 |
| `CHANGELOG.md:8` | 修改 | `## [Unreleased]` 增一行，记录「用户授权覆盖库内 HTTP server 约束」的取舍 |
| `src/octop_harness/__init__.py`、`README.md`、`pyproject.toml` | **不动** | 非公共 API、无新依赖、启动入口不变（§二.4、§五.4） |

---

## 五、方案设计（供 03 阶段执行）

### 5.1 原生 `/welcome` 路由设计 — `app.py`

- **落点**：仓库根目录 `app.py`（新建，发布包之外，§二.1/2.3）。
- **技术**：`http.server.ThreadingHTTPServer` + `BaseHTTPRequestHandler`（标准库，零新增运行依赖）；`ThreadingHTTPServer` 自带 `daemon_threads=True`，子进程/线程不阻塞退出。
- **接口契约**：
  - `GET /welcome` → `200`，`Content-Type: application/json`，带 `Content-Length`，体为 UTF-8 的 `json.dumps({"message": "welcome"})`（精确 `{"message": "welcome"}`）。
  - 其它路径 → `404`（`send_error`），证明是「路由」而非 catch-all。
  - 仅实现 `do_GET`；其它方法由基类返回 `501`。
- **代码骨架**（带完整类型注解，满足 `mypy --strict` 的 `disallow_untyped_defs` 与 ruff `E/W/F/I/B/UP/SIM/RUF/N/PL`）：

```python
"""Minimal stdlib HTTP service exposing the native GET /welcome route."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class WelcomeHandler(BaseHTTPRequestHandler):
    """Serve GET /welcome as JSON; return 404 for every other path."""

    def do_GET(self) -> None:
        if self.path == "/welcome":
            body = json.dumps({"message": "welcome"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        """Silence default stderr request logging (keeps test output clean)."""
        return


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    """Build a server; port=0 lets the OS pick a free port (used by tests)."""
    return ThreadingHTTPServer((host, port), WelcomeHandler)


def main() -> None:
    host = os.environ.get("WELCOME_HOST", "127.0.0.1")
    port = int(os.environ.get("WELCOME_PORT", "8000"))
    server = create_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```

- 说明：`log_message` 覆写仅为降噪，可用 `contextlib`/不覆写替代；`create_server(port=0)` 是测试用临时端口的关键；`main()` 用 `try/finally: server_close()` 保证干净退出。

### 5.2 接口契约测试 — `tests/test_welcome.py`

- **落点**：`tests/test_welcome.py`（新建）。命名与 `app.py` 对齐（`AGENTS.md:298` 一一对应约定；因 `app.py` 不在 `src/octop_harness` 下，不走 `__all__`）。
- **顺序**：按 `AGENTS.md:36-38`「先写（失败的）测试 → 再实现」——先落测试文件，`import app` 失败/连接失败 → 红；再落 `app.py` → 绿。
- **方式**（不新增任何测试依赖，纯标准库）：
  - pytest fixture：`create_server("127.0.0.1", 0)` 绑定临时端口 → 后台 daemon 线程 `serve_forever()` → `yield (host, port)` → teardown `shutdown()` + `server_close()`。
  - 用 `http.client.HTTPConnection(host, port)` 发起**真实 loopback GET**（进程内接口契约验证，非外网，符合 `AGENTS.md:9`「测试无外网、mock 第三方」）。
- **断言**（对应 §六 验收条件 1–3）：
  1. `GET /welcome` → `status == 200`；
  2. `json.loads(body) == {"message": "welcome"}`（精确体）；
  3. `resp.getheader("Content-Type")` 以 `application/json` 开头；
  4.（附加，证明是路由）`GET /other` → `404`。
- **须遵守的仓库约束（本阶段核对所得）**：
  - `tests/conftest.py` autouse fixtures 对本用例同样生效且顶层 `import octop_harness`（§三.7）→ 运行需平台 dev 环境（Python ≥3.12 + `make install`），与 01 §二.8/§五 环境提示一致；本用例自身只用标准库。
  - `pyproject.toml:271 filterwarnings=["error"]` → 必须 `try/finally` 显式 `conn.close()`、`shutdown()`、`server_close()`，否则 `ResourceWarning` 会被升级为错误；`ThreadingHTTPServer` 的 `daemon_threads=True` 避免挂起。
  - `pyproject.toml:264 pythonpath=["."]` → 测试在仓库根可 `import app`；`asyncio_mode="auto"`（:270）不影响同步用例；`--strict-markers`（:267）→ 不引入未注册 marker。
  - 探针（§三.14）已证明该测试路径可行，无需 mock Web 框架客户端。

### 5.3 启动方案

| 项 | 命令 / 口径 |
|----|-------------|
| 启动（默认） | `python3 app.py` → 监听 `127.0.0.1:8000` |
| 自定义主机/端口 | `WELCOME_HOST=0.0.0.0 WELCOME_PORT=8080 python3 app.py` |
| 手动验证 | `curl -i http://127.0.0.1:8000/welcome` → `HTTP/1.0 200` + `Content-Type: application/json` + `{"message": "welcome"}` |
| 停止 | `Ctrl-C`（`KeyboardInterrupt` → `server_close()`）；或结束进程；无持久状态 |
| 环境 | 运行环境由平台托管；`app.py` 仅标准库，本机 3.11 亦可直接跑；但 `pytest`/`make all` 需完整依赖（`deepagents` 等），必要时先 `make install`（`uv sync --group dev` 或 `pip install -e ".[dev]"`）。本机快照缺 `uv`/`.venv`、Python 3.11（01 §二.8） |

> 注：探针中 `BaseHTTPRequestHandler` 默认 `HTTP/1.0` 响应行不影响 200/JSON 契约判定。

### 5.4 回滚方案

- **改动集合（可完整枚举）**：新增 `app.py`、新增 `tests/test_welcome.py`、`CHANGELOG.md:8` 增一行。**无**既有文件行为变更、**无** `pyproject.toml` 依赖/脚本变更、**无**配置/数据库/迁移、**无**生产入口注册（`pyproject.toml:100` 脚本不变）。
- **回滚动作**：分支隔离 + 平台收尾提交 → `git revert <平台提交>`；或删除两个新增文件并回退 CHANGELOG 一行。服务无状态，停进程即停服，零数据迁移风险。
- **取舍记录（必须）**：`AGENTS.md:52,191,311` 禁止库内 HTTP server；本方案把服务放在发布包之外的顶层脚本（§二.3），库本身不含 HTTP server；残留的「仓库内新增 HTTP server」由用户授权覆盖，须在 `CHANGELOG.md` `## [Unreleased]` 与 MR 描述中**显式记录该取舍**（01 §六.3、`AGENTS.md` §12.7）。
- **质量门禁补充（重要）**：`Makefile:111,113,119,124` 的 lint/format/typecheck 仅覆盖 `src tests`，**根目录 `app.py` 不在其中**。为确保新文件同样过风格/类型门禁，03/06 阶段验证命令须额外显式纳入：`ruff check app.py`、`ruff format --check app.py`、`mypy app.py`（复用 `pyproject.toml` 的 strict 配置）；`tests/test_welcome.py` 因在 `tests/` 下已被 `make all` 覆盖。

---

## 六、验收条件（与 01 §五 对齐，作为 03/05 阶段判定口径）

1. `GET /welcome` 返回 HTTP `200`；
2. 响应为 JSON 且精确等于 `{"message": "welcome"}`（`message == "welcome"`）；
3. 响应头 `Content-Type: application/json`；
4. `tests/test_welcome.py` 覆盖该路由，且遵循「先红后绿」；
5. 不破坏既有行为：质量门禁 `make all` 全绿，且补充 `ruff check/format --check app.py`、`mypy app.py` 通过（`AGENTS.md:156,385`）；
6. 取舍在 `CHANGELOG.md` `## [Unreleased]` 与 MR 中显式记录；
7. 启动（`python3 app.py` + `curl`）与回滚（`git revert`）命令可执行、服务无状态。

---

## 七、涉及文件与命令汇总（交付 03 阶段）

**文件**

| 文件 | 动作 | 要点 |
|------|------|------|
| `app.py`（根，新建） | 新增 | 标准库 `http.server`，`do_GET /welcome`、`create_server(port=0)`、`main()`；发布包之外 |
| `tests/test_welcome.py`（新建） | 新增 | 临时端口 + daemon 线程 + `http.client`；断言 200/JSON/Content-Type；先红后绿 |
| `CHANGELOG.md:8` | 修改 | `## [Unreleased]` 记录授权覆盖取舍 |
| `src/octop_harness/**`、`README.md`、`pyproject.toml` | 不动 | 非公共 API、无新依赖、入口不变 |

**命令（按执行顺序）**

```bash
# 0) 环境（平台托管；本机缺依赖时）
make install            # uv sync --group dev / pip install -e ".[dev]"

# 1) 先写测试 → 预期 FAIL（import app 不存在 / 连接失败）
pytest tests/test_welcome.py -q

# 2) 实现 app.py 后 → 针对性用例转绿
pytest tests/test_welcome.py -q

# 3) 补充门禁（app.py 不在 make all 覆盖范围）
ruff check app.py tests/test_welcome.py
ruff format --check app.py tests/test_welcome.py
mypy app.py

# 4) 全量门禁
make all                # = format + lint + typecheck + test；未全绿不得称完成

# 5) 手动启动 / 冒烟
python3 app.py
curl -i http://127.0.0.1:8000/welcome

# 6) 回滚（平台提交后）
git revert <平台提交>   # 或删除两新文件并回退 CHANGELOG 一行
```

---

## 八、阶段边界与验收结论

- **边界**：本阶段严格限于方案设计。仅执行只读核对命令（§三）与一次不写文件的可行性探针（§三.14），并写入本文件；**未创建** `app.py` / `tests/test_welcome.py`、**未改动任何源码**、**未运行实现/测试命令**、**未执行任何 Git 提交**（提交由平台收尾）。
- **前置依赖已解除**：01 §八 指出的「落点 / 技术选型」前置依赖，已由本阶段 §二 四项裁决定案，可直接进入 03 编码。
- **阻塞判定**：无工具/读取层面的阻塞；01 发现的「任务前提与仓库身份不符」已转化为明确的、有用户授权覆盖的技术裁决，并记录取舍与补救门禁，不触发「停止并记失败」。
- **验收结论**：**Plan 阶段完成**。框架（无）、启动入口（CLI/stdio）、路由位置（无→新建 `app.py`）、测试约定、接口契约、启动/回滚方案、关键文件与命令均已给出并附执行证据（§三）；方案可直接交由 03 Implement + UT + Docs 落地。
