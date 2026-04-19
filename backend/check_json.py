import json
data = json.load(open('c:/Users/orh/Downloads/课表_2026-04-19.json', encoding='utf-8'))
for c in data:
    print(f"{c.get('kcmc')}: 星期{c.get('xqj')} jc={c.get('jc')} jcs={c.get('jcs')} jcor={c.get('jcor')} zcd={c.get('zcd')}")