"""本体操作核心库 — 基于 owlready2，供命令行脚本与 MCP server 共用。

设计约定：
  * 类 / 属性 / 个体的 IRI 片段一律使用英文标识符（IRI 安全、跨工具兼容）；
  * 中文语义写入 rdfs:label 与 rdfs:comment，Protégé 可切换 label 渲染；
  * 序列化统一 RDF/XML，兼容 Protégé 5.x（OWL API 4.x）。
"""

from __future__ import annotations

import os
from typing import Any

from owlready2 import (
    AllDisjoint,
    DataProperty,
    FunctionalProperty,
    InverseFunctionalProperty,
    ObjectProperty,
    SymmetricProperty,
    TransitiveProperty,
    Thing,
    get_ontology,
)

DEFAULT_IRI = "http://www.bank.example/ontology/bank-enterprise#"
DEFAULT_FORMAT = "rdfxml"


def _abs(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def _iri_of(path: str) -> str:
    return "file://" + _abs(path)


def load(path: str):
    """加载本地本体文件。"""
    return get_ontology(_iri_of(path)).load()


def create(path: str, iri: str = DEFAULT_IRI):
    """创建空本体并落盘。"""
    onto = get_ontology(iri)
    onto.save(file=_abs(path), format=DEFAULT_FORMAT)
    return onto


def save(onto, path: str, fmt: str = DEFAULT_FORMAT) -> str:
    onto.save(file=_abs(path), format=fmt)
    return _abs(path)


def _entity(onto, name: str):
    """按名称解析类 / 属性 / 个体。支持 'BankParty' 与完整 IRI。"""
    if name.startswith("http://") or name.startswith("https://"):
        return onto.world[name]
    ent = getattr(onto, name, None)
    if ent is None:
        for base in (name, "_" + name):
            ent = onto.world.get(base) or onto.world.get(onto.base_iri + base)
            if ent is not None:
                break
    if ent is None:
        found = onto.search_one(iri="*" + name)
        ent = found
    if ent is None:
        raise KeyError(f"本体中找不到实体: {name}")
    return ent


def _annotate(entity, label: str | None, comment: str | None) -> None:
    if label:
        entity.label.append(label)
    if comment:
        entity.comment.append(comment)


def add_class(onto, name: str, parent: str | None = None,
              label: str | None = None, comment: str | None = None,
              disjoint_with: list[str] | None = None):
    """新增类。parent 为父类名，缺省 owl:Thing。"""
    with onto:
        bases = (Thing,) if not parent else (_entity(onto, parent),)
        cls = type(name, bases, {"namespace": onto})
        _annotate(cls, label, comment)
        for other in disjoint_with or []:
            cls.disjoint_with.append(_entity(onto, other))
    return cls


def add_disjoint(onto, names: list[str]):
    """声明一组类两两不相交。"""
    with onto:
        return AllDisjoint([_entity(onto, n) for n in names])


_CHARACTERISTICS = {
    "functional": FunctionalProperty,
    "inverse_functional": InverseFunctionalProperty,
    "symmetric": SymmetricProperty,
    "transitive": TransitiveProperty,
}


def add_object_property(onto, name: str, domain: list[str] | None = None,
                        range_: list[str] | None = None,
                        characteristics: list[str] | None = None,
                        inverse_of: str | None = None,
                        label: str | None = None, comment: str | None = None):
    """新增对象属性。"""
    with onto:
        bases = [ObjectProperty] + [
            _CHARACTERISTICS[c] for c in (characteristics or []) if c in _CHARACTERISTICS
        ]
        prop = type(name, tuple(bases), {"namespace": onto})
        if domain:
            prop.domain = [_entity(onto, d) for d in domain]
        if range_:
            prop.range = [_entity(onto, r) for r in range_]
        if inverse_of:
            prop.inverse_property = _entity(onto, inverse_of)
        _annotate(prop, label, comment)
    return prop


def add_data_property(onto, name: str, domain: list[str] | None = None,
                      range_type: str = "str",
                      functional: bool = False,
                      label: str | None = None, comment: str | None = None):
    """新增数据属性。range_type: str | int | float | bool | datetime。"""
    rng = {"str": str, "int": int, "float": float, "bool": bool, "datetime": str}[range_type]
    with onto:
        bases = (DataProperty,) if not functional else (DataProperty, FunctionalProperty)
        prop = type(name, bases, {"namespace": onto, "range": [rng]})
        if domain:
            prop.domain = [_entity(onto, d) for d in domain]
        _annotate(prop, label, comment)
    return prop


def add_individual(onto, class_name: str, name: str,
                   label: str | None = None, comment: str | None = None,
                   relations: dict[str, list[str]] | None = None,
                   values: dict[str, Any] | None = None):
    """新增个体，可附带对象属性关系与数据属性值。"""
    with onto:
        cls = _entity(onto, class_name)
        ind = cls(name, namespace=onto)
        _annotate(ind, label, comment)
        for prop_name, targets in (relations or {}).items():
            prop = _entity(onto, prop_name)
            for t in targets:
                getattr(ind, prop_name).append(_entity(onto, t))
            _ = prop
        for prop_name, value in (values or {}).items():
            setattr(ind, prop_name, value)
    return ind


def add_restriction(onto, class_name: str, property_name: str,
                    kind: str, target: str | None = None,
                    cardinality: int | None = None):
    """为类添加限制公理。kind: some | only | min | max | exactly | value。"""
    prop = _entity(onto, property_name)
    if kind == "some":
        restr = prop.some(_entity(onto, target))
    elif kind == "only":
        restr = prop.only(_entity(onto, target))
    elif kind == "min":
        restr = prop.min(cardinality, _entity(onto, target) if target else None)
    elif kind == "max":
        restr = prop.max(cardinality, _entity(onto, target) if target else None)
    elif kind == "exactly":
        restr = prop.exactly(cardinality, _entity(onto, target) if target else None)
    elif kind == "value":
        restr = prop.value(_entity(onto, target))
    else:
        raise ValueError(f"不支持的限制类型: {kind}")
    with onto:
        _entity(onto, class_name).is_a.append(restr)
    return restr


def list_classes(onto, with_label: bool = True) -> list[dict]:
    """列出全部类及其父类，返回可序列化结构。"""
    out = []
    for cls in onto.classes():
        parents = [p.name for p in cls.is_a if hasattr(p, "name")]
        out.append({
            "name": cls.name,
            "label": cls.label[0] if with_label and cls.label else "",
            "parents": parents,
        })
    return out


def list_properties(onto) -> dict:
    """列出对象属性与数据属性。"""
    def _fmt(prop):
        return {
            "name": prop.name,
            "label": prop.label[0] if prop.label else "",
            "domain": [getattr(d, "name", str(d)) for d in getattr(prop, "domain", [])],
            "range": [getattr(r, "name", str(r)) for r in getattr(prop, "range", [])],
        }

    return {
        "object_properties": [_fmt(p) for p in onto.object_properties()],
        "data_properties": [_fmt(p) for p in onto.data_properties()],
    }


def describe(onto, name: str) -> dict:
    """查看单个实体的完整定义。"""
    ent = _entity(onto, name)
    info: dict[str, Any] = {
        "name": ent.name,
        "iri": ent.iri,
        "type": ent.__class__.__name__,
        "label": list(ent.label),
        "comment": list(ent.comment),
    }
    if hasattr(ent, "is_a"):
        info["is_a"] = [str(x) for x in ent.is_a]
    if hasattr(ent, "equivalent_to"):
        info["equivalent_to"] = [str(x) for x in ent.equivalent_to]
    if hasattr(ent, "disjoint_with"):
        info["disjoint_with"] = [getattr(x, "name", str(x)) for x in ent.disjoint_with]
    if hasattr(ent, "domain"):
        info["domain"] = [getattr(x, "name", str(x)) for x in ent.domain]
    if hasattr(ent, "range"):
        info["range"] = [getattr(x, "name", str(x)) for x in ent.range]
    if hasattr(ent, "instances"):
        info["instances"] = [i.name for i in ent.instances()]
    return info


def stats(onto) -> dict:
    return {
        "classes": len(list(onto.classes())),
        "object_properties": len(list(onto.object_properties())),
        "data_properties": len(list(onto.data_properties())),
        "individuals": len(list(onto.individuals())),
        "disjoint_axioms": len(list(onto.disjoints())),
        "ontology_iri": onto.base_iri.rstrip("#"),
    }


def run_reasoner(onto, infer_property_values: bool = True) -> dict:
    """运行 HermiT 推理机做一致性检查与分类（需要本机 Java）。"""
    try:
        with onto:
            from owlready2 import sync_reasoner_hermit
            sync_reasoner_hermit(onto, infer_property_values=infer_property_values)
        return {"ok": True, "inconsistent": False, "reasoner": "HermiT"}
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        inconsistent = "inconsistent" in msg.lower() or "unsatisfiable" in msg.lower()
        return {"ok": False, "inconsistent": inconsistent,
                "reasoner": "HermiT", "error": msg[:800]}


def validate(onto) -> dict:
    """轻量校验：悬空引用、缺失 label、无父类的孤立类。"""
    issues = []
    known = {c.name for c in onto.classes()}
    for p in list(onto.object_properties()) + list(onto.data_properties()):
        for d in getattr(p, "domain", []):
            if getattr(d, "name", None) not in known:
                issues.append(f"属性 {p.name} 的定义域引用了未知类 {d}")
        for r in getattr(p, "range", []):
            if hasattr(r, "name") and r.name not in known:
                issues.append(f"属性 {p.name} 的值域引用了未知类 {r}")
    for c in onto.classes():
        if not c.label:
            issues.append(f"类 {c.name} 缺少中文 label")
    return {"ok": not issues, "issues": issues}
