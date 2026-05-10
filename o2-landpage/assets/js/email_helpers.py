"""
O2 Data Solutions - Email HTML Helpers
Importado por server.py para gerar HTML de emails de assessment.
"""
import sys as _sys
_sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import email_data as _ED

def score_rows_internal(scores: dict) -> str:
    rows = []
    for qid, score in scores.items():
        label = _ED.QUESTION_LABELS.get(qid, qid)
        bc = "#ef4444" if score <= 3 else "#f59e0b" if score <= 6 else "#22c55e"
        bp = score * 10
        rows.append(
            f'<tr><td style="padding:7px 0;font-size:12px;color:#94a3b8;width:55%;border-bottom:1px solid #1e293b">{label}</td>'
            f'<td style="padding:7px 8px;width:35%;border-bottom:1px solid #1e293b">'
            f'<div style="background:#1e293b;border-radius:4px;height:7px;overflow:hidden">'
            f'<div style="width:{bp}%;height:7px;background:{bc};border-radius:4px"></div></div></td>'
            f'<td style="padding:7px 0;text-align:right;font-weight:700;font-size:12px;color:{bc};border-bottom:1px solid #1e293b">{score:.1f}/10</td></tr>'
        )
    return "".join(rows)

def score_rows_client(scores: dict) -> str:
    rows = []
    for qid, score in scores.items():
        label = _ED.QUESTION_LABELS.get(qid, qid)
        bc = "#ef4444" if score <= 3 else "#f59e0b" if score <= 6 else "#22c55e"
        bp = score * 10
        rows.append(
            f'<tr><td style="padding:8px 0;font-size:13px;color:#475569;width:55%;border-bottom:1px solid #e2e8f0">{label}</td>'
            f'<td style="padding:8px 8px;width:35%;border-bottom:1px solid #e2e8f0">'
            f'<div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden">'
            f'<div style="width:{bp}%;height:8px;background:{bc};border-radius:4px"></div></div></td>'
            f'<td style="padding:8px 0;text-align:right;font-weight:700;font-size:13px;color:{bc};border-bottom:1px solid #e2e8f0">{score:.1f}/10</td></tr>'
        )
    return "".join(rows)

def recs_internal(area: str, level_key: str) -> str:
    recs = _ED.RECOMMENDATIONS.get(area, {}).get(level_key, [])
    if not recs: return ""
    items = "".join(
        f'<li style="margin-bottom:10px;padding:10px 12px;background:#0f172a;border-radius:8px;'
        f'border-left:3px solid #3b82f6;font-size:12px;color:#cbd5e1;line-height:1.5">{r}</li>'
        for r in recs
    )
    return (
        f'<div style="margin-top:24px">'
        f'<p style="margin:0 0 12px;font-size:10px;font-weight:700;color:#475569;'
        f'text-transform:uppercase;letter-spacing:1.5px">&#x1F4CB; Recomenda&#xE7;&#xF5;es Priorit&#xE1;rias</p>'
        f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
    )

def recs_client(area: str, level_key: str) -> str:
    recs = _ED.RECOMMENDATIONS.get(area, {}).get(level_key, [])
    if not recs: return ""
    items = "".join(
        f'<li style="margin-bottom:12px;padding:14px 16px;background:#f8fafc;border-radius:10px;'
        f'border-left:4px solid #2563eb;font-size:13px;color:#334155;line-height:1.6">'
        f'<span style="font-weight:700;color:#1d4ed8">&#x2192;</span> {r}</li>'
        for r in recs
    )
    return (
        f'<div style="margin-top:28px">'
        f'<p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#1e293b">'
        f'&#x1F3AF; Recomenda&#xE7;&#xF5;es Priorit&#xE1;rias para Voc&#xEA;</p>'
        f'<ul style="margin:0;padding:0;list-style:none">{items}</ul></div>'
    )

AREA_LABELS = _ED.AREA_LABELS
AREA_ICONS  = _ED.AREA_ICONS_EMOJI
AREA_COLORS = _ED.AREA_COLORS
