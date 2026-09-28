"""职责分离（四权分离）合规检测。

原理
----
本体内置两条 SWRL 规则，由推理机执行：

  1. 四权分离违规
     Employee(?e) ∧ assignedRole(?e,?r1) ∧ assignedRole(?e,?r2)
       ∧ separatedFrom(?r1,?r2) → SeparationOfDutyViolation(?e)

  2. 报送编制复核分离违规
     Employee(?e) ∧ compilesReport(?e,?r) ∧ reviewsReport(?e,?r)
       → SeparationOfDutyViolation(?e)

局限（务必理解）
----------------
SWRL 是**单调**的：它只能「推导并标记」已经存在的违规，
不能「阻止」授权被赋予，也无法在缺少陈述时判定违规（开放世界假设）。
因此本脚本用于**离线审计与持续检测**，真正的强制拦截必须由
RBAC 授权服务在赋权时做。

用法
----
    python check_separation_of_duty.py            # 检测本体，退出码 1 表示存在违规
    python check_separation_of_duty.py --demo     # 在临时副本上构造演示数据验证规则

依赖项：需要可用的 java（自动探测 Protégé 内置 JRE）。
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.expanduser("~/.workbuddy/ontology-mcp"))

from ontology_core import load  # noqa: E402

DEFAULT_ONTOLOGY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "bank-enterprise.owl")

PROTEGE_JRE = os.environ.get("PROTEGE_JRE") or (
    "/Applications/Protégé.app/Contents/jre/bin" if sys.platform == "darwin" else ""
)


def _ensure_java() -> None:
    """确保 java 可用，优先借用 Protégé 内置 JRE。"""
    if shutil.which("java"):
        return
    if PROTEGE_JRE and os.path.isdir(PROTEGE_JRE):
        os.environ["PATH"] = PROTEGE_JRE + os.pathsep + os.environ.get("PATH", "")
    if not shutil.which("java"):
        raise SystemExit(
            "未找到 java，无法运行推理机。Windows 下可安装 JDK，"
            "或设置环境变量 PROTEGE_JRE 指向 Protégé 自带的 jre\\bin 目录"
        )


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _name(x) -> str:
    return getattr(x, "name", str(x))


def _label(x) -> str:
    lab = getattr(x, "label", None)
    return lab[0] if lab else ""


def run_reasoner(onto) -> None:
    from owlready2 import sync_reasoner_hermit

    with onto:
        sync_reasoner_hermit(onto, infer_property_values=True)


def find_violations(onto) -> list[dict]:
    """返回违规明细。每个元素含员工名、标签、冲突类型与冲突明细。"""
    cls = getattr(onto, "SeparationOfDutyViolation", None)
    if cls is None:
        raise SystemExit("本体中缺少 SeparationOfDutyViolation 类")

    out = []
    for ind in cls.instances():
        name = _name(ind)
        detail: list[str] = []

        roles = _as_list(getattr(ind, "assignedRole", None))
        for a in roles:
            for b in roles:
                if a is b:
                    continue
                if b in _as_list(getattr(a, "separatedFrom", None)):
                    pair = f"{_label(a) or _name(a)} × {_label(b) or _name(b)}"
                    if pair not in detail and f"{_label(b) or _name(b)} × {_label(a) or _name(a)}" not in detail:
                        detail.append(pair)

        compiled = {_name(r) for r in _as_list(getattr(ind, "compilesReport", None))}
        reviewed = {_name(r) for r in _as_list(getattr(ind, "reviewsReport", None))}
        both = sorted(compiled & reviewed)
        for r in both:
            detail.append(f"报文 {r}：编制与复核为同一人")

        out.append({
            "name": name,
            "label": _label(ind),
            "roles": [_label(r) or _name(r) for r in roles],
            "conflicts": detail,
        })
    return out


def demo(onto_path: str) -> int:
    """在临时副本上构造违规与合规样本，验证规则确实生效。"""
    tmp = os.path.join(tempfile.gettempdir(), "sod_demo.owl")
    shutil.copy(onto_path, tmp)
    onto = load(tmp)

    with onto:
        bad = onto.Employee("EmpZhang", namespace=onto)
        bad.label.append("张三（违规样本）")
        bad.assignedRole = [onto.RoleSystemAdmin, onto.RoleBusinessOperator]

        good = onto.Employee("EmpLi", namespace=onto)
        good.label.append("李四（合规样本）")
        good.assignedRole = [onto.RoleBusinessOperator]

        rep_bad = onto.Employee("EmpWang", namespace=onto)
        rep_bad.label.append("王五（编制复核同一人）")
        batch = onto.ReportingBatch("DemoBatch", namespace=onto)
        batch.label.append("演示报送批次")
        rep_bad.compilesReport = [batch]
        rep_bad.reviewsReport = [batch]

    print("演示样本：张三同时持有系统管理权与业务操作权（应违规）；")
    print("          李四仅持有业务操作权（应合规）；")
    print("          王五对同一报送批次既编制又复核（应违规）。")
    print()
    run_reasoner(onto)

    violations = find_violations(onto)
    flagged = {v["name"] for v in violations}
    print("推理结果：")
    for who, expect in (("EmpZhang", True), ("EmpLi", False), ("EmpWang", True)):
        got = who in flagged
        mark = "符合预期" if got == expect else "!! 与预期不符"
        print(f"  {who:<10} 被判定违规={got}  期望={expect}  {mark}")
    print()
    return report(violations)


def report(violations: list[dict]) -> int:
    if not violations:
        print("结果：未检出职责分离违规")
        return 0
    print(f"结果：检出 {len(violations)} 个主体存在职责分离违规")
    for i, v in enumerate(violations, 1):
        who = f"{v['label']}({v['name']})" if v["label"] else v["name"]
        print(f"  {i}. {who}")
        if v["roles"]:
            print(f"     持有角色: {', '.join(v['roles'])}")
        for d in v["conflicts"]:
            print(f"     冲突: {d}")
    return 1


def main() -> int:
    _ensure_java()
    path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DEFAULT_ONTOLOGY
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    print(f"检测本体 : {path}")
    if "--demo" in flags:
        return demo(path)

    onto = load(path)
    run_reasoner(onto)
    return report(find_violations(onto))


if __name__ == "__main__":
    raise SystemExit(main())
