import os
from writers.ics_writer import build_ics
from writers.posts_writer import write_pre_post_posts
from sources.cbf import fetch_matches_2025_stub
from sources.libertadores import fetch_libertadores_flamengo_2025_stub
from sources.nbb import fetch_nbb_flamengo_2025_stub
from sources.bcla import fetch_bcla_flamengo_2025_stub
OUT=os.path.join(os.path.dirname(__file__),'out')
def main():
    os.makedirs(OUT, exist_ok=True)
    events=[]
    events+=fetch_matches_2025_stub()
    events+=fetch_libertadores_flamengo_2025_stub()
    events+=fetch_nbb_flamengo_2025_stub()
    events+=fetch_bcla_flamengo_2025_stub()
    for e in events: e['description_footer']='Fonte: CBF/Oficiais — Atualizações semanais.'
    ics=build_ics(events)
    open(os.path.join(OUT,'crf_2025.ics'),'w',encoding='utf-8').write(ics)
    write_pre_post_posts(events, OUT)
if __name__=='__main__': main()
