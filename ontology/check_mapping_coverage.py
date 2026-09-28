#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""映射覆盖率校验。

检查报送字段（本体中 east* 数据属性）是否已建立来源映射，
并校验映射条目自身的完整性与一致性。

背景：OWL 限制公理在开放世界假设下只能表达「应当有」，
无法判定「实际没有」（未陈述 ≠ 违反）。因此映射完备性必须在
封闭世界下逐项核对——本脚本承担的就是这一层。

用法：
    python check_mapping_coverage.py                 # 报告模式，退出码 0
    python check_mapping_coverage.py --strict        # 存在未映射字段则退出码 1
    python check_mapping_coverage.py --min-coverage 0.8
    python check_mapping_coverage.py <本体文件路径>

退出码：
    0  校验通过（或仅报告模式）
    1  存在未映射字段（--strict）／覆盖率低于阈值／发现结构性错误
"""

import os
import sys

sys.path.insert(0, os.path.expanduser("~/.workbuddy/ontology-mcp"))

from ontology_core import load  # noqa: E402

DEFAULT_ONTOLOGY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "bank-enterprise.owl"
)

# 报送记录的管理属性，不参与源字段映射
MANAGED_PROPS = {"reportedPeriod", "snapshotTime"}

# 无需源字段的转换类型（常量与多源拼接本就没有单一来源字段）
SOURCELESS_TYPES = {"常量赋值", "字符串拼接"}


def _as_list(value):
    """owlready2 中 functional 属性返回单值、非 functional 返回列表、缺失返回 None。"""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def collect_reporting_fields(onto):
    """收集各 EAST 主题域的报送字段：{域名: [属性名]}。"""
    base = onto.EASTDataItem
    domains = [base] + list(base.descendants())
    domain_names = {d.name for d in domains if hasattr(d, "name")}

    result = {}
    for prop in onto.data_properties():
        if prop.name in MANAGED_PROPS:
            continue
        for d in prop.domain:
            dn = getattr(d, "name", None)
            if dn in domain_names and dn != base.name:
                result.setdefault(dn, []).append(prop.name)
    return dict(sorted(result.items()))


def collect_mappings(onto):
    """收集映射条目：{目标属性名: [个体]}。"""
    result = {}
    for ind in onto.FieldMapping.instances():
        target = ind.targetOntologyProperty
        if target:
            result.setdefault(target, []).append(ind)
    return result


def validate(onto, fields_by_domain, mappings):
    """返回 (errors, warnings)，均为字符串列表。"""
    errors, warnings = [], []

    all_props = {p.name for p in onto.data_properties()}
    domain_of = {}
    for domain, props in fields_by_domain.items():
        for p in props:
            domain_of[p] = domain

    for target, inds in sorted(mappings.items()):
        # 结构性错误：引用了不存在的本体属性
        if target not in all_props:
            errors.append(
                "映射 %s 的目标属性 %s 在本体中不存在"
                % (inds[0].name, target)
            )
            continue

        if target not in domain_of:
            errors.append(
                "映射 %s 的目标属性 %s 不属于任何 EAST 主题域"
                % (inds[0].name, target)
            )
            continue

        if len(inds) > 1:
            warnings.append(
                "属性 %s 存在 %d 条映射条目：%s"
                % (target, len(inds), ", ".join(i.name for i in inds))
            )

        for ind in inds:
            # 限制公理要求：每条映射必须归属某个规格
            if not _as_list(getattr(ind, "inSpecification", None)):
                errors.append("映射条目 %s 未设置 inSpecification" % ind.name)

            declared = ind.targetDomainClass
            if declared and declared != domain_of[target]:
                warnings.append(
                    "映射 %s 声明目标类 %s，但属性实际域为 %s"
                    % (ind.name, declared, domain_of[target])
                )

            status = ind.mappingStatus or ""
            if status in ("已确认", "待确认"):
                ttype = ind.transformationType or ""
                has_src = bool(_as_list(getattr(ind, "mapsSourceField", None)))
                if not has_src and ttype not in SOURCELESS_TYPES:
                    warnings.append(
                        "映射 %s 状态为 %s 但无源字段，且转换类型 %s 需要取数来源"
                        % (ind.name, status, ttype or "(空)")
                    )
    # 限制公理 SourceField ⊑ ∃belongsToTable.SourceTable 在开放世界下不生效，
    # 须在此逐项核对：源字段若未归属任何表，转换引擎无法定位取数对象。
    for ind in onto.SourceField.instances():
        if not _as_list(getattr(ind, "belongsToTable", None)):
            errors.append("源字段 %s 未设置 belongsToTable" % ind.name)
        elif not getattr(ind, "fieldName", None):
            warnings.append("源字段 %s 未设置物理字段名 fieldName" % ind.name)

    # 已确认但未经官方规范校准的条目，汇总提示
    uncalibrated = [
        i.name for i in onto.FieldMapping.instances()
        if (getattr(i, "mappingStatus", "") or "") == "已确认"
        and (getattr(i, "mappingConfidence", "") or "") != "已验证"
    ]
    if uncalibrated:
        warnings.append(
            "%d 条映射状态为「已确认」但置信度未达「已验证」：%s"
            % (len(uncalibrated), ", ".join(sorted(uncalibrated)))
        )

    return errors, warnings


def classify(fields_by_domain, mappings):
    """按域统计映射状态，返回 (rows, total, mapped, pending, unmapped, no_entry)。"""
    rows = []
    total = mapped = pending = unmapped = no_entry = 0
    for domain, props in fields_by_domain.items():
        d_total = len(props)
        d_mapped = d_pending = d_unmapped = d_none = 0
        missing = []
        for p in sorted(props):
            inds = mappings.get(p)
            total += 1
            if not inds:
                no_entry += 1
                d_none += 1
                missing.append(p)
                continue
            status = getattr(inds[0], "mappingStatus", "") or "未映射"
            if status == "已确认":
                mapped += 1
                d_mapped += 1
            elif status == "待确认":
                pending += 1
                d_pending += 1
                missing.append(p)
            else:
                unmapped += 1
                d_unmapped += 1
                missing.append(p)
        rows.append((domain, d_total, d_mapped, d_pending, d_unmapped, d_none, missing))
    return rows, total, mapped, pending, unmapped, no_entry


def main(argv):
    path = DEFAULT_ONTOLOGY
    strict = "--strict" in argv
    min_cov = 0.0
    for i, a in enumerate(argv):
        if a == "--min-coverage" and i + 1 < len(argv):
            min_cov = float(argv[i + 1])
        elif a.endswith(".owl"):
            path = a

    print("=" * 72)
    print("映射覆盖率校验")
    print("=" * 72)
    print("本体文件: %s" % path)
    print()

    onto = load(path)
    fields = collect_reporting_fields(onto)
    mappings = collect_mappings(onto)
    rows, total, mapped, pending, unmapped, no_entry = classify(fields, mappings)
    errors, warnings = validate(onto, fields, mappings)

    print("--- 按主题域统计 ---")
    print("%-22s %6s %8s %8s %8s %8s" % ("主题域", "字段数", "已确认", "待确认", "未映射", "无条目"))
    print("-" * 72)
    for domain, t, m, p, u, n, _ in rows:
        print("%-22s %6d %8d %8d %8d %8d" % (domain, t, m, p, u, n))
    print("-" * 72)
    print("%-22s %6d %8d %8d %8d %8d" % ("合计", total, mapped, pending, unmapped, no_entry))
    print()

    ratio = (mapped / total) if total else 0.0
    print("已确认覆盖率 : %.1f%%  (%d/%d)" % (ratio * 100, mapped, total))
    print("待确认       : %d" % pending)
    print("未映射       : %d" % unmapped)
    print("无映射条目   : %d" % no_entry)
    print()

    if errors:
        print("--- 结构性错误 (%d) ---" % len(errors))
        for e in errors:
            print("  [错误] %s" % e)
        print()
    if warnings:
        print("--- 告警 (%d) ---" % len(warnings))
        for w in warnings:
            print("  [告警] %s" % w)
        print()

    print("--- 未覆盖字段清单 ---")
    any_missing = False
    for domain, _t, _m, _p, _u, _n, missing in rows:
        if missing:
            any_missing = True
            print("  %s (%d): %s" % (domain, len(missing), ", ".join(missing)))
    if not any_missing:
        print("  （无）")
    print()

    failed = False
    if errors:
        failed = True
    if min_cov and ratio < min_cov:
        print("覆盖率 %.1f%% 低于阈值 %.1f%%" % (ratio * 100, min_cov * 100))
        failed = True
    if strict and (unmapped + no_entry + pending) > 0:
        print("严格模式：存在未覆盖字段 %d 个" % (unmapped + no_entry + pending))
        failed = True

    print("结论: %s" % ("未通过" if failed else "通过"))
    print("提示: 映射完备性无法由 OWL 推理保证（开放世界假设），须以本脚本作为数据门禁。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
