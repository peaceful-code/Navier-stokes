"""Inventory and format checks for the delivered immersive viewer and renders."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1]
out=root/'output/immersive'
required=['EXPLORER_LE_VORTEX.html','apercu_immersif.png','animation_immersive.mp4','vortex_immersif.blend','flow_data.json','illustrative_metadata.json','illustrative_checks.json']
files=[]
for name in required:
    p=out/name
    assert p.is_file() and p.stat().st_size>0,p
    with p.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
    files.append({'file':name,'bytes':p.stat().st_size,'sha256':digest})
class HTMLCheck(HTMLParser):
    def __init__(self):super().__init__();self.externals=[];self.scripts=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script':
            self.scripts+=1
            if a.get('src'):self.externals.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.externals.append(a.get('href'))
p=HTMLCheck();p.feed((out/required[0]).read_text());assert p.scripts==1 and not p.externals
with Image.open(out/'apercu_immersif.png') as image:
    assert image.size==(1920,1080);image.verify()
movie=json.loads(subprocess.run(['/usr/local/bin/ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,nb_frames','-show_entries','format=duration','-of','json',str(out/'animation_immersive.mp4')],capture_output=True,text=True,check=True).stdout)
assert movie['streams'][0]['codec_name']=='h264'
assert int(movie['streams'][0]['nb_frames'])==240
assert float(movie['format']['duration'])==10
checks=json.loads((out/'illustrative_checks.json').read_text());assert checks['passed']
report={'scope':'Independent pedagogical velocity field; not a reconstruction of the Navier–Stokes solution','files':files,'html':{'self_contained':True,'external_script_or_style_assets':p.externals},'poster_dimensions':[1920,1080],'video':movie,
'browser_observations':{'desktop_viewport':[1280,720],'scene_visually_inspected':True,'pause_and_scrub':True,'magnification_toggle':True,'finite_endpoint_radius_percent':1,'finite_endpoint_magnification':100,'half_cut':True,'reference_rings':True,'free_orbit':True,'scope_dialog':True,'png_preview_rendered':True,'png_save_link_present':True,'download_event_confirmation':'not available in this browser automation; PNG preview and link inspected','console_errors_observed':[]},'model_numerical_checks_passed':True}
(out/'verification_livraison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'Validated {len(files)} deliverables; report saved.')
