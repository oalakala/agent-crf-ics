from datetime import datetime, timedelta
import hashlib
def _format(dt): return dt.strftime('%Y%m%dT%H%M%S')
def _uid(s): return hashlib.md5(s.encode()).hexdigest()+'@agent-crf-ics'
def build_ics(events):
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Agent CRF 2025//ICS 1.0//PT-BR',
           'CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-TIMEZONE:America/Sao_Paulo',
           'X-WR-CALNAME:Flamengo 2025 (Oficiais)','X-WR-CALDESC:Atualizado automaticamente.']
    for e in events:
        start=e['start']; end=e['start']+timedelta(minutes=e.get('duration_min',120))
        uid=_uid(f"{e.get('competition','')}.{e.get('match_id','')}.{start.isoformat()}")
        desc=[]
        if e.get('onde_assistir'): desc.append('Onde assistir: '+e['onde_assistir'])
        if e.get('cbf_url'): desc.append('Oficial: '+e['cbf_url'])
        if e.get('notes'): desc.append(e['notes'])
        if e.get('description_footer'): desc.append(e['description_footer'])
        lines+=['BEGIN:VEVENT','UID:'+uid,'SUMMARY:'+e.get('summary','Jogo do Flamengo'),
                'DTSTART;TZID=America/Sao_Paulo:'+_format(start),
                'DTEND;TZID=America/Sao_Paulo:'+_format(end),
                'LOCATION:'+e.get('location',''),
                'BEGIN:VALARM','ACTION:DISPLAY','TRIGGER:-PT30M','DESCRIPTION:Lembrete do jogo','END:VALARM',
                'DESCRIPTION:'+'\n'.join(desc),'STATUS:CONFIRMED','END:VEVENT']
    lines.append('END:VCALENDAR'); return '\n'.join(lines)
