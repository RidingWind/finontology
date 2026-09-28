"""本体建模 MCP server（零第三方依赖，仅依赖 owlready2）。

自行实现 MCP 的 stdio JSON-RPC 2.0 传输层，避免受 pip 安装环境影响。
生成的 .owl 为标准 RDF/XML，已验证可被 Protégé 5.6.9 的 OWL API 4.x 直接解析。

启动（供 ~/.workbuddy/mcp.json 调用）：
    /Users/zhongyuanpan/.workbuddy/binaries/python/envs/default/bin/python \
        ~/.workbuddy/ontology-mcp/server.py
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Any, Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ontology_core as core  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "ontology-mcp"

_STATE: dict[str, Any] = {"current": None, "onto": None}


# --------------------------------------------------------------------------
# 内部辅助
# --------------------------------------------------------------------------
def _resolve(path: str | None) -> str:
    p = path or _STATE.get("current")
    if not p:
        raise ValueError("未指定本体文件，请先调用 ontology_use 或传入 path 参数。")
    return os.path.abspath(os.path.expanduser(p))


def _onto(path: str | None = None, reload: bool = False):
    p = _resolve(path)
    if reload or _STATE.get("current") != p or _STATE.get("onto") is None:
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"本体文件不存在: {p}，请先调用 ontology_create 或 ontology_seed_bank。")
        _STATE["current"] = p
        _STATE["onto"] = core.load(p)
    return _STATE["onto"]


def _commit(onto, path: str | None = None) -> None:
    core.save(onto, _resolve(path))


def _s(prop: str, desc: str = "") -> dict:
    return {"type": "string", "description": desc} if desc else {"type": "string"}


def _arr(items: dict, desc: str = "") -> dict:
    d = {"type": "array", "items": items}
    if desc:
        d["description"] = desc
    return d


_STR_ARR = _arr({"type": "string"})


# --------------------------------------------------------------------------
# 工具实现
# --------------------------------------------------------------------------
def t_use(a: dict) -> dict:
    path = a["path"]
    p = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(p):
        return {"ok": False, "error": f"文件不存在: {p}"}
    onto = _onto(p, reload=True)
    return {"ok": True, "path": p, "stats": core.stats(onto)}


def t_create(a: dict) -> dict:
    p = os.path.abspath(os.path.expanduser(a["path"]))
    onto = core.create(p, a.get("iri") or core.DEFAULT_IRI)
    _STATE["current"] = p
    _STATE["onto"] = onto
    return {"ok": True, "path": p, "iri": a.get("iri") or core.DEFAULT_IRI}


def t_seed(a: dict) -> dict:
    from bank_seed import build
    p = os.path.abspath(os.path.expanduser(a["path"]))
    out = build(p)
    onto = _onto(out, reload=True)
    return {"ok": True, "path": out, "stats": core.stats(onto)}


def t_add_class(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_class(onto, a["name"], a.get("parent") or None,
                   a.get("label") or None, a.get("comment") or None,
                   a.get("disjoint_with"))
    _commit(onto, a.get("path") or None)
    return {"ok": True, "class": a["name"], "parent": a.get("parent") or "owl:Thing"}


def t_add_disjoint(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_disjoint(onto, a["names"])
    _commit(onto, a.get("path") or None)
    return {"ok": True, "disjoint": a["names"]}


def t_add_object_property(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_object_property(onto, a["name"], a.get("domain"), a.get("range"),
                             a.get("characteristics"), a.get("inverse_of") or None,
                             a.get("label") or None, a.get("comment") or None)
    _commit(onto, a.get("path") or None)
    return {"ok": True, "object_property": a["name"]}


def t_add_data_property(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_data_property(onto, a["name"], a.get("domain"),
                           a.get("range_type") or "str",
                           bool(a.get("functional")),
                           a.get("label") or None, a.get("comment") or None)
    _commit(onto, a.get("path") or None)
    return {"ok": True, "data_property": a["name"]}


def t_add_individual(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_individual(onto, a["class"], a["name"], a.get("label") or None,
                        a.get("comment") or None, a.get("relations"), a.get("values"))
    _commit(onto, a.get("path") or None)
    return {"ok": True, "individual": a["name"], "class": a["class"]}


def t_add_restriction(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    core.add_restriction(onto, a["class"], a["property"], a["kind"],
                         a.get("target") or None, a.get("cardinality"))
    _commit(onto, a.get("path") or None)
    return {"ok": True, "restriction": f"{a['class']} ⊑ {a['kind']} {a['property']}"}


def t_list_classes(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    classes = core.list_classes(onto)
    return {"ok": True, "count": len(classes), "classes": classes}


def t_list_properties(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    return {"ok": True, **core.list_properties(onto)}


def t_describe(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    try:
        return {"ok": True, **core.describe(onto, a["name"])}
    except KeyError as exc:
        return {"ok": False, "error": str(exc)}


def t_stats(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    return {"ok": True, **core.stats(onto)}


def t_run_reasoner(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    return core.run_reasoner(onto)


def t_validate(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    return core.validate(onto)


def t_save(a: dict) -> dict:
    onto = _onto(a.get("path") or None)
    return {"ok": True, "saved": core.save(onto, _resolve(a.get("path") or None))}


TOOLS: list[dict[str, Any]] = [
    {"name": "ontology_use", "fn": t_use,
     "description": "加载并切换当前操作的本体文件，返回规模统计。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体 .owl 文件路径")},
                     "required": ["path"]}},

    {"name": "ontology_create", "fn": t_create,
     "description": "创建一个空本体文件。",
     "inputSchema": {"type": "object",
                     "properties": {"path": _s("", "输出路径"),
                                    "iri": _s("", "本体 IRI，默认银行本体命名空间")},
                     "required": ["path"]}},

    {"name": "ontology_seed_bank", "fn": t_seed,
     "description": "生成银行业务本体骨架：九大域、RBAC 四权分离、国密算法、技术组件。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "输出 .owl 路径")},
                     "required": ["path"]}},

    {"name": "ontology_add_class", "fn": t_add_class,
     "description": "新增类。parent 为空则挂在 owl:Thing 下。",
     "inputSchema": {"type": "object",
                     "properties": {"name": _s("", "类名，英文标识符"),
                                    "parent": _s("", "父类名"),
                                    "label": _s("", "中文标签"),
                                    "comment": _s("", "中文注释"),
                                    "disjoint_with": _arr({"type": "string"}, "与之不相交的类"),
                                    "path": _s("", "本体文件路径")},
                     "required": ["name"]}},

    {"name": "ontology_add_disjoint", "fn": t_add_disjoint,
     "description": "声明一组类两两不相交。",
     "inputSchema": {"type": "object",
                     "properties": {"names": _arr({"type": "string"}, "类名列表"),
                                    "path": _s("", "本体文件路径")},
                     "required": ["names"]}},

    {"name": "ontology_add_object_property", "fn": t_add_object_property,
     "description": "新增对象属性。characteristics 可选 functional / inverse_functional / symmetric / transitive。",
     "inputSchema": {"type": "object",
                     "properties": {"name": _s("", "属性名"),
                                    "domain": _STR_ARR, "range": _STR_ARR,
                                    "characteristics": _STR_ARR,
                                    "inverse_of": _s("", "逆属性名"),
                                    "label": _s("", "中文标签"),
                                    "comment": _s("", "中文注释"),
                                    "path": _s("", "本体文件路径")},
                     "required": ["name"]}},

    {"name": "ontology_add_data_property", "fn": t_add_data_property,
     "description": "新增数据属性。range_type: str / int / float / bool / datetime。",
     "inputSchema": {"type": "object",
                     "properties": {"name": _s("", "属性名"),
                                    "domain": _STR_ARR,
                                    "range_type": _s("", "默认 str"),
                                    "functional": {"type": "boolean"},
                                    "label": _s("", "中文标签"),
                                    "comment": _s("", "中文注释"),
                                    "path": _s("", "本体文件路径")},
                     "required": ["name"]}},

    {"name": "ontology_add_individual", "fn": t_add_individual,
     "description": "新增个体，可附带对象属性关系与数据属性值。",
     "inputSchema": {"type": "object",
                     "properties": {"class": _s("", "所属类名"),
                                    "name": _s("", "个体名"),
                                    "label": _s("", "中文标签"),
                                    "comment": _s("", "中文注释"),
                                    "relations": {"type": "object",
                                                  "description": "属性名到目标个体名列表的映射"},
                                    "values": {"type": "object",
                                               "description": "数据属性名到字面值的映射"},
                                    "path": _s("", "本体文件路径")},
                     "required": ["class", "name"]}},

    {"name": "ontology_add_restriction", "fn": t_add_restriction,
     "description": "为类添加限制公理。kind: some / only / min / max / exactly / value。",
     "inputSchema": {"type": "object",
                     "properties": {"class": _s("", "类名"),
                                    "property": _s("", "属性名"),
                                    "kind": _s("", "some|only|min|max|exactly|value"),
                                    "target": _s("", "目标类名"),
                                    "cardinality": {"type": "integer"},
                                    "path": _s("", "本体文件路径")},
                     "required": ["class", "property", "kind"]}},

    {"name": "ontology_list_classes", "fn": t_list_classes,
     "description": "列出全部类、中文标签与父类。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},

    {"name": "ontology_list_properties", "fn": t_list_properties,
     "description": "列出全部对象属性与数据属性及定义域、值域。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},

    {"name": "ontology_describe", "fn": t_describe,
     "description": "查看单个类 / 属性 / 个体的完整定义与公理。",
     "inputSchema": {"type": "object",
                     "properties": {"name": _s("", "实体名"), "path": _s("", "本体文件路径")},
                     "required": ["name"]}},

    {"name": "ontology_stats", "fn": t_stats,
     "description": "返回本体规模统计。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},

    {"name": "ontology_run_reasoner", "fn": t_run_reasoner,
     "description": "运行 HermiT 推理机做一致性检查与自动分类（需要本机 Java）。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},

    {"name": "ontology_validate", "fn": t_validate,
     "description": "轻量校验：悬空引用、缺失中文标签等问题。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},

    {"name": "ontology_save", "fn": t_save,
     "description": "把当前本体保存回文件。",
     "inputSchema": {"type": "object", "properties": {"path": _s("", "本体文件路径")}}},
]

_BY_NAME = {t["name"]: t for t in TOOLS}


# --------------------------------------------------------------------------
# MCP stdio 传输层（JSON-RPC 2.0）
# --------------------------------------------------------------------------
def _read_message() -> dict | None:
    stdin = sys.stdin.buffer
    line = stdin.readline()
    if not line:
        return None
    if line.lstrip().startswith(b"{"):
        return json.loads(line.decode("utf-8"))
    # LSP 风格：Content-Length 头
    headers: dict[str, str] = {}
    while line not in (b"\r\n", b"\n", b""):
        k, _, v = line.decode("utf-8", "replace").partition(":")
        headers[k.strip().lower()] = v.strip()
        line = stdin.readline()
        if not line:
            return None
    n = int(headers.get("content-length", 0))
    body = stdin.read(n)
    return json.loads(body.decode("utf-8"))


def _write_message(msg: dict, framed: bool) -> None:
    data = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    out = sys.stdout.buffer
    if framed:
        out.write(b"Content-Length: " + str(len(data)).encode() + b"\r\n\r\n")
    out.write(data)
    if not framed:
        out.write(b"\n")
    out.flush()


def _result(req: dict, payload: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req.get("id"), "result": payload}


def _error(req: dict, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req.get("id"),
            "error": {"code": code, "message": message}}


def _handle(req: dict) -> dict | None:
    method = req.get("method")
    if method == "initialize":
        return _result(req, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": "1.0.0"},
        })
    if method == "tools/list":
        return _result(req, {"tools": [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in TOOLS
        ]})
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        tool = _BY_NAME.get(name)
        if tool is None:
            return _error(req, -32601, f"未知工具: {name}")
        try:
            out = tool["fn"](params.get("arguments") or {})
            return _result(req, {"content": [
                {"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}
            ]})
        except Exception as exc:  # noqa: BLE001
            return _result(req, {"isError": True, "content": [
                {"type": "text", "text": f"{exc}\n{traceback.format_exc(limit=4)}"}
            ]})
    if method in ("notifications/initialized", "initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return _result(req, {})
    if method == "shutdown":
        return _result(req, {})
    if req.get("id") is None:
        return None
    return _error(req, -32601, f"不支持的方法: {method}")


def main() -> None:
    for name in ("PYTHONIOENCODING",):
        os.environ.setdefault(name, "utf-8")
    while True:
        try:
            req = _read_message()
        except (json.JSONDecodeError, ValueError):
            continue
        if req is None:
            break
        resp = _handle(req)
        if resp is not None:
            _write_message(resp, framed=False)
        if (req.get("method") or "") == "shutdown":
            break


if __name__ == "__main__":
    main()
