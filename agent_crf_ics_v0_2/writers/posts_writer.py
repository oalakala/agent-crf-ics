import os
def write_pre_post_posts(events, out_dir):
    pre=os.path.join(out_dir,'posts','pre'); post=os.path.join(out_dir,'posts','post')
    os.makedirs(pre,exist_ok=True); os.makedirs(post,exist_ok=True)
    for e in events:
        title=e.get('summary','Jogo'); start=e['start']
        venue=e.get('location',''); tv=e.get('onde_assistir','a confirmar'); cbf=e.get('cbf_url','')
        slug=''.join(c.lower() if c.isalnum() else '-' for c in title).strip('-')
        pre_md=f"""---
title: "[Pré] {title}"
date: {start:%Y-%m-%d}
competition: {e.get('competition','')}
onde_assistir: "{tv}"
local: "{venue}"
link_oficial: "{cbf}"
tags: [Esporte, Flamengo]
categories: [Agenda]
---

**Jogo:** {title}
**Data/Hora:** {start:%d/%m/%Y %H:%M} (America/Sao_Paulo)  
**Local:** {venue}  
**Onde Assistir:** {tv}  

Fonte oficial: {cbf}
"""
        open(os.path.join(pre,f"{start:%Y%m%d%H%M}-{slug}.md"),'w',encoding='utf-8').write(pre_md)
        post_md=f"""---
title: "[Pós] {title}"
date: {start:%Y-%m-%d}
competition: {e.get('competition','')}
resultado: "a preencher"
tags: [Esporte, Flamengo, resultado]
categories: [Agenda]
---

**Jogo:** {title}
**Data/Hora:** {start:%d/%m/%Y %H:%M} (America/Sao_Paulo)  
**Local:** {venue}  

**Resultado:** a preencher
"""
        open(os.path.join(post,f"{start:%Y%m%d%H%M}-{slug}.md"),'w',encoding='utf-8').write(post_md)
