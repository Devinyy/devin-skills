#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_SUBDIR = ""
TOPIC_DIR = "主题"
LINK_SECTION_TITLE = "## Obsidian 关联"
CATEGORY_TREE = {
    "研发": ["前端", "DevOps", "工程质量", "架构", "SOP"],
    "AI工程": ["Agent", "Skill", "Harness", "AI Coding"],
    "管理": ["团队协作", "流程治理", "CodeReview"],
    "设计": ["产品设计", "UIUX"],
    "生活": ["阅读", "摄影", "旅行", "调酒", "杂谈"],
}
CATEGORIES = [f"{domain}/{item}" for domain, items in CATEGORY_TREE.items() for item in items]

CATEGORY_KEYWORDS = {
    "管理/团队协作": [
        "管理", "团队", "组织", "协作", "领导", "绩效", "复盘", "code review", "codereview", "代码评审",
        "沟通", "文化", "项目管理",
    ],
    "管理/流程治理": [
        "流程", "治理", "规范", "制度", "审批", "SOP", "标准化", "项目管理",
    ],
    "管理/CodeReview": [
        "code review", "codereview", "代码评审", "评审", "review", "代码审查",
    ],
    "研发/前端": [
        "前端", "javascript", "typescript", "react", "vue", "ui", "组件", "浏览器", "css", "webpack",
        "前端架构", "前端监控",
    ],
    "研发/DevOps": [
        "devops", "ci/cd", "cicd", "持续集成", "持续交付", "部署", "运维", "gitlab", "jenkins",
        "流水线",
    ],
    "研发/工程质量": [
        "工程质量", "代码质量", "测试", "监控", "错误监控", "质量", "技术债", "告警", "日志",
        "sourcemap", "性能",
    ],
    "研发/架构": [
        "架构", "系统设计", "模块化", "monorepo", "微服务", "技术栈", "设计系统", "架构治理",
    ],
    "研发/SOP": [
        "sop", "操作手册", "流程步骤", "规范流程", "执行清单", "标准作业",
    ],
    "AI工程/Agent": [
        "agent", "智能体", "multi-agent", "browser use", "工具调用", "自动规划", "自主执行",
        "coding agent",
    ],
    "AI工程/Skill": [
        "skill", "技能", "codex skill", "claude skill", "可复用技能", "工作流技能", "skill.md",
    ],
    "AI工程/Harness": [
        "harness", "评测", "benchmark", "基建", "上下文工程", "验证", "测试集", "自动验证",
        "可交付性", "脚手架",
    ],
    "AI工程/AI Coding": [
        "ai coding", "vibe coding", "trae", "代码生成", "辅助编程", "编程助手",
    ],
    "生活/阅读": [
        "阅读", "读书", "书单", "书评", "笔记", "作者", "文学", "小说", "非虚构",
    ],
    "生活/摄影": [
        "摄影", "相机", "镜头", "构图", "光圈", "快门", "焦段", "照片", "拍摄", "后期",
    ],
    "生活/旅行": [
        "旅行", "旅游", "出行", "攻略", "城市", "酒店", "机票", "路线", "景点",
    ],
    "生活/调酒": [
        "调酒", "酒谱", "配方", "鸡尾酒", "微醺", "便利店调酒", "超市调酒", "中式调酒",
        "白酒特调", "劲酒特调", "低度白酒", "果酒", "基酒", "酒体", "口感", "分层",
        "蜜桃乌龙", "水溶 c100", "元气森林", "旺仔牛奶", "古井贡酒", "中国劲酒",
    ],
    "生活/杂谈": [
        "生活", "健康", "饮食", "睡眠", "家庭", "情绪", "心理", "习惯", "消费", "理财", "杂谈",
    ],
    "设计/产品设计": [
        "产品设计", "产品", "原型", "需求", "用户体验", "交互", "流程图",
    ],
    "设计/UIUX": [
        "设计", "ui", "ux", "figma", "原型", "交互", "视觉", "组件", "体验", "产品设计",
    ],
}


def obsidian_config_path() -> Path:
    override = os.getenv("OBSIDIAN_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"


def detect_vault(config_path: Path | None = None) -> Path | None:
    env_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if env_path:
        vault = Path(env_path).expanduser()
        return vault if vault.exists() and vault.is_dir() else None

    config = config_path or obsidian_config_path()
    if not config.exists():
        return None

    try:
        payload = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    vaults = payload.get("vaults") or {}
    candidates = []
    for item in vaults.values():
        path = item.get("path")
        if not path:
            continue
        vault = Path(path).expanduser()
        if vault.exists() and vault.is_dir():
            candidates.append((bool(item.get("open")), int(item.get("ts") or 0), vault))

    if not candidates:
        return None

    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return candidates[0][2]


def safe_filename(value: str, fallback: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", value).strip()
    name = re.sub(r"\s+", " ", name)
    name = name.rstrip(".")
    if not name:
        name = fallback
    return name[:100].strip() or fallback


def normalize_category(value: str) -> str | None:
    raw = value.strip().replace("\\", "/")
    aliases = {
        "Agent": "AI工程/Agent",
        "skill": "AI工程/Skill",
        "Skill": "AI工程/Skill",
        "harness": "AI工程/Harness",
        "Harness": "AI工程/Harness",
        "AI Coding": "AI工程/AI Coding",
        "管理": "管理/团队协作",
        "研发": "研发/架构",
        "设计": "设计/产品设计",
        "生活": "生活/杂谈",
        "杂谈": "生活/杂谈",
        "摄影": "生活/摄影",
        "阅读": "生活/阅读",
        "旅行": "生活/旅行",
        "调酒": "生活/调酒",
    }
    if raw in CATEGORIES:
        return raw
    return aliases.get(raw)


def title_from_summary(summary_path: Path) -> str | None:
    try:
        for line in summary_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        return None
    return None


def metadata_title(task_dir: Path) -> str | None:
    metadata_path = task_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    title = payload.get("title")
    return title.strip() if isinstance(title, str) and title.strip() else None


def read_metadata(task_dir: Path) -> dict:
    metadata_path = task_dir / "metadata.json"
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_metadata(task_dir: Path, metadata: dict) -> None:
    (task_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def category_context(task_dir: Path, summary_path: Path) -> dict:
    metadata = read_metadata(task_dir)
    title = title_from_summary(summary_path) or metadata_title(task_dir) or ""
    try:
        summary = summary_path.read_text(encoding="utf-8")
    except OSError:
        summary = ""
    nested_metadata = metadata.get("metadata") if isinstance(metadata.get("metadata"), dict) else {}
    return {
        "title": title,
        "platform": metadata.get("platform") or "",
        "content_type": nested_metadata.get("content_type") or "",
        "text_preview": nested_metadata.get("text_preview") or "",
        "summary": summary,
    }


def category_scores(context: dict) -> dict[str, int]:
    text = "\n".join(
        [
            context.get("title") or "",
            context.get("platform") or "",
            context.get("content_type") or "",
            context.get("text_preview") or "",
            (context.get("summary") or "")[:12000],
        ]
    ).lower()

    scores = {category: 0 for category in CATEGORIES}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            normalized = keyword.lower()
            count = text.count(normalized)
            if count:
                scores[category] += count
    return scores


def category_priority() -> dict[str, int]:
    return {category: index for index, category in enumerate([
        "AI工程/Agent", "AI工程/Skill", "AI工程/Harness", "AI工程/AI Coding",
        "研发/前端", "研发/DevOps", "研发/工程质量", "研发/架构", "研发/SOP",
        "管理/CodeReview", "管理/流程治理", "管理/团队协作",
        "设计/UIUX", "设计/产品设计",
        "生活/调酒", "生活/摄影", "生活/阅读", "生活/旅行", "生活/杂谈",
    ])}


def related_categories_by_rules(context: dict, primary: str, limit: int = 3) -> list[str]:
    scores = category_scores(context)
    priority = category_priority()
    candidates = [
        category for category in CATEGORIES
        if category != primary and scores[category] > 0
    ]
    candidates.sort(key=lambda category: (scores[category], -priority.get(category, 99)), reverse=True)
    return candidates[:limit]


def rule_classify_category(context: dict) -> tuple[str, str, list[str]]:
    scores = category_scores(context)
    # Specific technical folders should win ties over broad catch-all folders.
    priority = category_priority()
    best = max(CATEGORIES, key=lambda category: (scores[category], -priority.get(category, 99)))
    if scores[best] <= 0:
        return "生活/杂谈", "规则分类未命中明确关键词，回退到生活/杂谈。", []
    related = related_categories_by_rules(context, best)
    return best, f"规则分类命中 {best}，分数 {scores[best]}。", related


def normalize_related_categories(value: object, primary: str) -> list[str]:
    if not isinstance(value, list):
        return []
    related = []
    for item in value:
        category = normalize_category(str(item))
        if category and category != primary and category not in related:
            related.append(category)
    return related[:3]


def parse_model_category(raw: str) -> tuple[str, str, list[str]] | None:
    text = raw.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        category = normalize_category(str(payload.get("category") or ""))
        reason = str(payload.get("reason") or "").strip()
        if category:
            related = normalize_related_categories(payload.get("related_categories"), category)
            return category, reason or "模型未提供原因。", related

    for category in CATEGORIES:
        if text == category or text.startswith(category):
            return category, text, []
    normalized = normalize_category(text)
    if normalized:
        return normalized, text, []
    return None


def model_classify_category(context: dict) -> tuple[str, str, list[str]] | None:
    load_dotenv()
    if os.getenv("OBSIDIAN_CLASSIFIER", "model").lower() == "rules":
        return None
    if not os.getenv("OPENAI_API_KEY"):
        return None

    categories = "\n".join(f"- {domain}/{item}" for domain, items in CATEGORY_TREE.items() for item in items)
    prompt = (
        "你是 Obsidian 知识库分类助手。请只从给定二级分类中选择一个最合适的主分类路径，"
        "并选择 0-3 个跨域相关主题。\n"
        f"可选分类路径：\n{categories}\n\n"
        "分类含义：\n"
        "- 研发/前端：前端架构、前端监控、浏览器、React/Vue/JS/TS、前端工程化。\n"
        "- 研发/DevOps：DevOps、CI/CD、持续交付、部署、运维、流水线。\n"
        "- 研发/工程质量：测试、监控、告警、代码质量、错误追踪、技术债。\n"
        "- 研发/架构：系统设计、架构治理、模块化、技术栈、平台架构。\n"
        "- 研发/SOP：标准流程、操作手册、执行步骤、规范化作业。\n"
        "- AI工程/Agent：AI Agent、Coding Agent、智能体、工具调用、自主执行。\n"
        "- AI工程/Skill：Codex/Claude/Agent skill、技能包、技能编写、可复用工作流。\n"
        "- AI工程/Harness：评测、benchmark、验证基建、上下文工程、可交付性验证。\n"
        "- AI工程/AI Coding：AI 辅助编程、AI Coding 实践、Vibe Coding、代码生成。\n"
        "- 管理/团队协作：团队协作、组织沟通、领导、文化、复盘。\n"
        "- 管理/流程治理：流程治理、制度、标准化、审批、项目管理。\n"
        "- 管理/CodeReview：代码评审、代码审查、Review 机制与文化。\n"
        "- 设计/产品设计：产品设计、需求、原型、用户体验、流程。\n"
        "- 设计/UIUX：UI、UX、视觉、交互、Figma、组件体验。\n"
        "- 生活/阅读、生活/摄影、生活/旅行、生活/调酒、生活/杂谈：个人知识主题。\n\n"
        "如果内容同时涉及多个分类，请把文章最应该存放的位置作为 category，把跨域或次要主题放入 related_categories。\n"
        "只输出 JSON，格式：{\"category\":\"一级/二级\",\"related_categories\":[\"一级/二级\"],\"reason\":\"一句话说明依据\"}"
    )
    content = {
        "title": context.get("title", ""),
        "platform": context.get("platform", ""),
        "content_type": context.get("content_type", ""),
        "text_preview": (context.get("text_preview", "") or "")[:3000],
        "summary": (context.get("summary", "") or "")[:12000],
    }
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(content, ensure_ascii=False)},
    ]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        raw = resp.choices[0].message.content or ""
    except Exception:
        raw = classify_with_http_fallback(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=model,
            messages=messages,
        )
    return parse_model_category(raw)


def classify_with_http_fallback(api_key: str | None, base_url: str | None, model: str, messages: list[dict]) -> str:
    if not api_key or not base_url:
        raise RuntimeError("OPENAI_API_KEY and OPENAI_BASE_URL are required for HTTP fallback category classification.")

    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"

    resp = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0,
        },
        timeout=60,
    )
    resp.raise_for_status()
    payload = json.loads(resp.content.decode("utf-8"))
    return payload["choices"][0]["message"]["content"] or ""


def classify_category(task_dir: Path, summary_path: Path) -> tuple[str, str, str, list[str]]:
    override = os.getenv("OBSIDIAN_CATEGORY")
    context = category_context(task_dir, summary_path)
    if override:
        normalized = normalize_category(override)
        if normalized:
            return normalized, "env", "通过 OBSIDIAN_CATEGORY 手动指定。", related_categories_by_rules(context, normalized)

    try:
        model_result = model_classify_category(context)
    except Exception as exc:
        model_result = None
        model_error = f"模型分类失败，回退规则分类：{exc.__class__.__name__}"
    else:
        model_error = ""

    if model_result:
        category, reason, related = model_result
        if not related:
            related = related_categories_by_rules(context, category)
        return category, "model", reason, related

    category, reason, related = rule_classify_category(context)
    if model_error:
        reason = f"{model_error}；{reason}"
    return category, "rules", reason, related


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem} {index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot find unique Obsidian output path for {path}")


def wiki_escape(value: str) -> str:
    return value.replace("|", " ").replace("[", " ").replace("]", " ").strip()


def wikilink(target: str, label: str | None = None) -> str:
    safe_target = wiki_escape(target)
    safe_label = wiki_escape(label or "")
    if safe_label and safe_label != safe_target:
        return f"[[{safe_target}|{safe_label}]]"
    return f"[[{safe_target}]]"


def relative_wiki_target(path: Path, vault: Path) -> str:
    try:
        relative = path.relative_to(vault)
    except ValueError:
        relative = path
    return str(relative.with_suffix(""))


def topic_title(category: str) -> str:
    return category.replace("/", " ")


def topic_path(vault: Path, category: str) -> Path:
    return vault / TOPIC_DIR / f"{safe_filename(topic_title(category), fallback='topic')}.md"


def ensure_topic(vault: Path, category: str) -> Path:
    domain, item = category.split("/", 1)
    path = topic_path(vault, category)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        siblings = [
            sibling for sibling in CATEGORY_TREE.get(domain, [])
            if sibling != item
        ]
        sibling_links = " ".join(
            wikilink(relative_wiki_target(topic_path(vault, f"{domain}/{sibling}"), vault), sibling)
            for sibling in siblings
        )
        path.write_text(
            f"# {topic_title(category)}\n\n"
            f"{LINK_SECTION_TITLE}\n\n"
            f"- 分类路径：`{category}`\n"
            f"- 一级领域：{domain}\n"
            f"- 相邻主题：{sibling_links}\n",
            encoding="utf-8",
        )
    return path


def ensure_all_topics(vault: Path) -> None:
    for category in CATEGORIES:
        ensure_topic(vault, category)


def existing_related_notes(target_dir: Path, target_path: Path, limit: int = 5) -> list[Path]:
    notes = []
    for path in sorted(target_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
        if path == target_path:
            continue
        notes.append(path)
        if len(notes) >= limit:
            break
    return notes


def add_obsidian_links(
    note_path: Path,
    vault: Path,
    category: str,
    category_reason: str,
    related_categories: list[str],
    related_notes: list[Path],
) -> None:
    ensure_all_topics(vault)
    primary_topic = ensure_topic(vault, category)
    related_topics = [ensure_topic(vault, item) for item in related_categories]

    text = note_path.read_text(encoding="utf-8")
    if LINK_SECTION_TITLE in text:
        text = text.split(LINK_SECTION_TITLE, 1)[0].rstrip()

    lines = [
        "",
        LINK_SECTION_TITLE,
        "",
        f"- 主主题：{wikilink(relative_wiki_target(primary_topic, vault), topic_title(category))}",
        f"- 分类依据：{category_reason}",
    ]
    if related_topics:
        lines.append("- 相关主题：" + " ".join(
            wikilink(relative_wiki_target(path, vault), topic_title(category))
            for path, category in zip(related_topics, related_categories)
        ))
    if related_notes:
        lines.append("- 同类笔记：" + " ".join(
            wikilink(relative_wiki_target(path, vault), path.stem) for path in related_notes
        ))
    lines.append("")

    note_path.write_text(text.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def export_summary(task_dir: Path, vault: Path | None = None, subdir: str | None = None) -> Path | None:
    summary_path = task_dir / "summary.md"
    if not summary_path.exists():
        return None

    target_vault = vault or detect_vault()
    if not target_vault:
        return None

    target_subdir = subdir if subdir is not None else os.getenv("OBSIDIAN_OUTPUT_DIR", DEFAULT_SUBDIR)
    category, category_method, category_reason, related_categories = classify_category(task_dir, summary_path)
    category_parts = category.split("/", 1)
    category_root = target_vault / target_subdir if target_subdir else target_vault
    for domain, items in CATEGORY_TREE.items():
        for item in items:
            (category_root / domain / item).mkdir(parents=True, exist_ok=True)
    target_dir = category_root / category_parts[0] / category_parts[1]
    target_dir.mkdir(parents=True, exist_ok=True)

    title = title_from_summary(summary_path) or metadata_title(task_dir) or task_dir.name
    filename = safe_filename(title, fallback=task_dir.name)
    target_path = unique_path(target_dir / f"{filename}.md")
    shutil.copyfile(summary_path, target_path)
    related_notes = existing_related_notes(target_dir, target_path)
    add_obsidian_links(
        target_path,
        target_vault,
        category,
        category_reason,
        related_categories,
        related_notes,
    )
    metadata = read_metadata(task_dir)
    metadata["obsidian_category"] = category
    metadata["obsidian_category_method"] = category_method
    metadata["obsidian_category_reason"] = category_reason
    metadata["obsidian_related_categories"] = related_categories
    metadata["obsidian_path"] = str(target_path)
    write_metadata(task_dir, metadata)
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir")
    parser.add_argument("--vault", help="Obsidian vault path. Defaults to auto-detected open/recent vault.")
    parser.add_argument("--subdir", help="Vault subdirectory. Defaults to the vault root.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser() if args.vault else None
    exported = export_summary(Path(args.task_dir), vault=vault, subdir=args.subdir)
    if exported:
        print(str(exported))


if __name__ == "__main__":
    main()
