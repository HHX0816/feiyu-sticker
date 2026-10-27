from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

from langbot_plugin.api.definition.components.tool.tool import Tool
from langbot_plugin.api.entities.builtin.provider import session as provider_session

CAPTIONS = {
    "shengqi": "生气", "xianqi": "嫌弃", "huachi": "花痴", "jiazai": "加载中",
    "wenhao": "问号脸", "jiaban": "加班", "ganfan": "干饭", "buyao": "不要",
    "yaoqian": "求打赏", "deyi": "得意", "ok": "好嘞", "piaole": "飘了",
    "bixin": "比心", "maozhua": "猫爪", "zaoshanghao": "早上好", "qiurao": "求饶",
    "yun": "晕", "zhenjing": "震惊", "haixiu": "害羞", "toukan": "偷看",
    "wuyu": "无语", "shuijiao": "睡觉", "xia": "吓到", "tangping": "躺平",
}

EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ROOT = Path(os.environ.get("FEIYU_STICKER_DIR", "D:/qqbot/stickers"))


def _scan() -> list[tuple[Path, str, str]]:
    """返回 (路径, 情绪目录, 中文描述)。"""
    out: list[tuple[Path, str, str]] = []
    if not ROOT.is_dir():
        return out
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXT:
            mood = p.parent.name
            cap = CAPTIONS.get(p.stem, p.stem)
            out.append((p, mood, cap))
    return out


class SendSticker(Tool):
    async def call(self, params: dict[str, Any], session: provider_session.Session, query_id: int) -> str:
        mood = (params.get("mood") or "").strip().lower()
        keyword = (params.get("keyword") or "").strip()

        pool = _scan()
        if not pool:
            return "图库是空的，暂时发不了表情包。"

        picked: list[tuple[Path, str, str]] = []
        if keyword:
            picked = [t for t in pool if keyword in t[2] or keyword in t[1] or keyword in t[0].stem]
        if not picked and mood:
            picked = [t for t in pool if t[1] == mood]
        if not picked:
            picked = pool

        path, m, cap = random.choice(picked)
        try:
            from langbot_plugin.api.entities.builtin.platform import message as platform_message

            chain = platform_message.MessageChain([platform_message.Image(path=str(path))])
            await self.plugin.send_message(
                session.bot_uuid,
                session.launcher_type.value,
                str(session.launcher_id),
                chain,
            )
        except Exception as e:  # noqa: BLE001
            return f"表情包发送失败：{e}"

        return f"已发出表情包「{cap}」（{m}）。图已经在对话里了，不用再描述它，回一句短话就行。"
