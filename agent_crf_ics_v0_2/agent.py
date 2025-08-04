import os, csv, json, yaml
from datetime import datetime, timedelta
from writers.ics_writer import build_ics
from writers.posts_writer import write_pre_post_posts
from sources.cbf import fetch_matches_2025_stub  # v0.3: será trocado por scraping real

ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, 'out')
CFG = os.path.join(ROOT, 'config.yml')

def load_cfg():
    if os.path.exists(CFG):
        with open(CFG, 'r', encoding='utf-8') as f: return yaml.safe_load(f)
    return {"bundles": {}}

def normalize(events):
    """Garante campos comuns e rotulagem por modalidade/competição."""
    norm = []
    for e in events:
        x = dict(e)
        # Rotulagem básica (v0.3: CBF = futebol)
        x.setdefault("modalidade", "futebol")
        x.setdefault("competicao", "Brasileirão Série A" if "Brasileirão" in x.get("summary","") else e.get("competition",""))
        # Campos auxiliares
        x.setdefault("onde_assistir", "")
        x.setdefault("status", "scheduled")
        # Split times (quando houver)
        if "summary" in x and " x " in x["summary"]:
            # tentativa simples de separar equipes pelo " x " / " — "
            pass
        norm.append(x)
    return norm

def write_ics(events, relpath):
    path = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = build_ics(events)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def make_bundles(all_events, cfg):
    """Gera os 6 em 1 conforme config.yml"""
    bundles = cfg.get("bundles", {})
    for name, b in bundles.items():
        filt = b.get("filters", {})
        out_rel = b["output"]
        selected = []
        for ev in all_events:
            ok = True
            if "modalidade" in filt and ev.get("modalidade") not in filt["modalidade"]:
                ok = False
            if "competicoes_incluidas" in filt:
                if ev.get("competicao") not in filt["competicoes_incluidas"]:
                    ok = False
            if ok: selected.append(ev)
        write_ics(selected, out_rel)

def write_wp_csvs(events):
    """Gera CSVs (pré/pós e consolidado) com wp_status=draft (semiautomático)."""
    wp_dir = os.path.join(OUT, "wp")
    os.makedirs(wp_dir, exist_ok=True)

    def slugify(t): return "".join(c.lower() if c.isalnum() else "-" for c in t).strip("-").replace("--","-")

    pre_cols = ["title","date","hora","modalidade","competicao","fase_rodada",
                "equipe_1","equipe_2","local","onde_assistir","link_oficial",
                "tipo","wp_status","slug","conteudo_md"]
    post_cols = pre_cols.copy()

    pre_rows, post_rows, all_rows = [], [], []
    for e in events:
        title = e.get("summary","Evento")
        start = e["start"]
        date = start.strftime("%Y-%m-%d")
        hora = start.strftime("%H:%M")
        local = e.get("location","")
        tv = e.get("onde_assistir","")
        comp = e.get("competicao", e.get("competition",""))
        fase = e.get("fase_rodada", e.get("notes",""))
        link = e.get("cbf_url","")
        slug = f"{start:%Y%m%d%H%M}-{slugify(title)}"

        pre = {
            "title": f"[Pré] {title}", "date": date, "hora": hora,
            "modalidade": e.get("modalidade",""),
            "competicao": comp, "fase_rodada": fase,
            "equipe_1": "", "equipe_2": "",
            "local": local, "onde_assistir": tv, "link_oficial": link,
            "tipo": "pre", "wp_status": "draft",
            "slug": slug,
            "conteudo_md": f"**Jogo/Event:** {title}\n**Data/Hora:** {start:%d/%m/%Y %H:%M} (BRT)\n**Local:** {local}\n**Onde Assistir:** {tv}\n\nFonte oficial: {link}"
        }
        post = pre.copy()
        post["title"] = f"[Pós] {title}"
        post["tipo"]  = "post"
        post["conteudo_md"] = f"**Jogo/Event:** {title}\n**Data/Hora:** {start:%d/%m/%Y %H:%M} (BRT)\n**Local:** {local}\n\n**Resultado/Resumo:** a preencher"

        pre_rows.append(pre); post_rows.append(post); all_rows += [pre, post]

    def dump(rows, name):
        path = os.path.join(wp_dir, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=pre_cols)
            w.writeheader(); w.writerows(rows)

    dump(pre_rows, "posts_pre.csv")
    dump(post_rows,"posts_post.csv")
    dump(all_rows, "posts_consolidado.csv")  # tem pre+post; status=draft

def main():
    cfg = load_cfg()
    os.makedirs(OUT, exist_ok=True)

    # 1) CARREGAR EVENTOS (v0.3: CBF real; por ora usa stub para manter build ok)
    events = []
    events += fetch_matches_2025_stub()

    # 2) NORMALIZAR + rotular
    events = normalize(events)

    # 3) ICS individuais simples (exemplo — v0.3 vai gerar vários)
    write_ics(events, "calendars/individuais/flamengo_all.ics")

    # 4) GERAR AGREGADORES (6 em 1)
    make_bundles(events, cfg)

    # 5) POSTS (pré/pós) + CSV consolidado (semiautomático)
    write_pre_post_posts(events, OUT)  # mantém MDs
    write_wp_csvs(events)

    # 6) Catálogo de saídas para seu site
    index = {
      "generated_at": datetime.utcnow().isoformat()+"Z",
      "files": []
    }
    for root, _, files in os.walk(OUT):
        for f in files:
            rel = os.path.relpath(os.path.join(root,f), OUT)
            index["files"].append(rel)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
