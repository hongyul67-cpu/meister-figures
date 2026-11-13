# 고친 그림 html 을 png 로 다시 만든다 — 원래 png 와 같은 가로 픽셀로 맞춰 줌
#  사용 (명령 창에서) :
#     python 다시그리기.py "..\서론_2026\06_11쪽_경기제조AI.html"
#     python 다시그리기.py "..\서론_2026\06_11쪽_경기제조AI.html" "..\학과별\피지컬AI로봇운용과_1_경력발전경로.html"
#  · png 는 html 옆에 같은 이름으로 저장됩니다(원래 png 는 같은 폴더 _백업 에 시각 붙여 남김).
#  · 배치도(plan_c/m1/m2.html)는 창조관1층_변경후.png 처럼 이름이 달라 그 이름으로 저장합니다.
#  · 필요한 것 : python, playwright (pip install playwright → playwright install chromium)
#               크롬 대신 엣지가 있으면 그것을 씁니다.
import sys, pathlib, shutil, datetime
from playwright.sync_api import sync_playwright
PLAN = {'plan_c': '창조관1층_변경후', 'plan_m1': '명장관1층_변경후', 'plan_m2': '명장관2층_변경후'}
FIND = '''() => { const r = [...document.body.children].find(e => !['STYLE','SCRIPT','META','LINK'].includes(e.tagName)) || document.body;
  const b = r.getBoundingClientRect(); return [b.width, b.height] }'''
files = [pathlib.Path(a).resolve() for a in sys.argv[1:]]
if not files: print(__doc__ or '사용법은 파일 맨 위 설명을 보세요'); sys.exit()
with sync_playwright() as p:
    try: br = p.chromium.launch()
    except Exception: br = p.chromium.launch(channel='msedge')
    for h in files:
        png = h.with_name(PLAN.get(h.stem, h.stem) + '.png')
        pg = br.new_page(viewport={'width': 2400, 'height': 1600})
        pg.goto(h.as_uri()); pg.wait_for_timeout(300)
        w, hh = pg.evaluate(FIND)
        scale = 2.0
        if png.exists():                                   # 원래 그림과 같은 가로 픽셀
            from PIL import Image
            with Image.open(png) as im: scale = im.size[0] / w
            bk = png.parent / '_백업'; bk.mkdir(exist_ok=True)
            shutil.copy2(png, bk / f'{png.stem}_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
        pg.close(); pg = br.new_page(viewport={'width': 2400, 'height': 1600}, device_scale_factor=scale)
        pg.goto(h.as_uri()); pg.wait_for_timeout(300)
        el = pg.evaluate_handle('''() => [...document.body.children].find(e => !['STYLE','SCRIPT','META','LINK'].includes(e.tagName)) || document.body''')
        el.as_element().screenshot(path=str(png)); pg.close()
        print('다시 그림 :', png.name, f'(배율 {scale:.2f})')
    br.close()
print('끝. 신청서(한글)에 넣으려면 그림을 지우고 새 png 를 같은 너비로 넣으세요.')
