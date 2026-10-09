from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json,re,html,hashlib
root=Path('/Users/markyang/Projects/UNUK-Year-3/Y3_Autumn/COMP2013_DMS/lab')
build=root/'.devops-build/strict'
source=root/'DevOps Template.pptx'
spec=json.loads((build/'spec.json').read_text())
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
# Start with the original package. Only fill existing paragraph text slots.
def fill_paragraph(raw,values):
 values=list(values)
 matches=list(re.finditer(r'<a:t(?:\s[^>]*)?>.*?</a:t>',raw,re.S))
 if matches:
  assert len(matches)==len(values),(len(matches),len(values))
  idx=iter(values)
  return re.sub(r'(<a:t(?:\s[^>]*)?>).*?(</a:t>)',lambda m:m.group(1)+html.escape(next(idx),quote=False)+m.group(2),raw,flags=re.S)
 assert len(values)==1
 end=re.search(r'<a:endParaRPr(?:\s[^>]*)?(?:/>|>.*?</a:endParaRPr>)',raw,re.S)
 rpr=end.group(0).replace('a:endParaRPr','a:rPr') if end else '<a:rPr/>'
 run='<a:r>'+rpr+'<a:t>'+html.escape(values[0],quote=False)+'</a:t></a:r>'
 return raw[:end.start()]+run+raw[end.start():] if end else raw.replace('</a:p>',run+'</a:p>')
def patch_slide(raw,changes):
 by_shape={}
 for c in changes: by_shape.setdefault(c['shape'],{})[c['p']]=c['text']
 sidx=-1
 def shape_patch(m):
  nonlocal sidx
  sidx+=1
  if sidx not in by_shape: return m.group(0)
  paragraph_idx=-1
  def pp(mm):
   nonlocal paragraph_idx
   paragraph_idx+=1
   vals=by_shape[sidx].get(paragraph_idx)
   return fill_paragraph(mm.group(0),vals) if vals is not None else mm.group(0)
  return re.sub(r'<a:p(?:\s[^>]*)?>.*?</a:p>',pp,m.group(0),flags=re.S)
 return re.sub(r'<p:sp(?:\s[^>]*)?>.*?</p:sp>',shape_patch,raw,flags=re.S)
with ZipFile(source) as src, ZipFile(build/'notes-artifact.pptx') as art:
 data={name:src.read(name) for name in src.namelist()}
 originals=dict(data)
 for i,s in enumerate(spec,1):
  name=f'ppt/slides/slide{i}.xml'
  data[name]=patch_slide(data[name].decode('utf-8'),s['changes']).encode('utf-8')
  # Insert a notes relationship while retaining every original relationship.
  rel=f'ppt/slides/_rels/slide{i}.xml.rels'
  link=f'<Relationship Id="rIdStrictNotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{i}.xml"/>'
  data[rel]=data[rel].decode('utf-8').replace('</Relationships>',link+'</Relationships>').encode('utf-8')
 note_names=[name for name in art.namelist() if name.startswith(('ppt/notesSlides/','ppt/notesMasters/')) and not name.endswith('/')]
 for name in note_names:data[name]=art.read(name)
 ct=E.fromstring(art.read('[Content_Types].xml'))
 additions=''.join(f'<Override PartName="{o.get("PartName")}" ContentType="{o.get("ContentType")}"/>' for o in ct if o.get('PartName','').startswith(('/ppt/notesSlides/','/ppt/notesMasters/')))
 data['[Content_Types].xml']=data['[Content_Types].xml'].decode('utf-8').replace('</Types>',additions+'</Types>').encode('utf-8')
 # Notes master registration changes only non-visible presentation metadata.
 pm='ppt/presentation.xml'
 data[pm]=data[pm].decode('utf-8').replace('<p:sldIdLst>','<p:notesMasterIdLst><p:notesMasterId r:id="rIdStrictNotesMaster"/></p:notesMasterIdLst><p:sldIdLst>').encode('utf-8')
 pr='ppt/_rels/presentation.xml.rels'
 link='<Relationship Id="rIdStrictNotesMaster" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>'
 data[pr]=data[pr].decode('utf-8').replace('</Relationships>',link+'</Relationships>').encode('utf-8')
 dest=build/'candidate.pptx'
 with ZipFile(dest,'w',ZIP_DEFLATED) as out:
  for name,bytes_ in data.items():
   if name in src.namelist():out.writestr(src.getinfo(name),bytes_)
   else:out.writestr(name,bytes_)
 # Verify shape/paragraph geometry and every existing run's formatting.
 checks=[]
 for i in range(1,13):
  old=E.fromstring(originals[f'ppt/slides/slide{i}.xml']);new=E.fromstring(data[f'ppt/slides/slide{i}.xml'])
  old_shapes=old.findall('.//p:sp',ns);new_shapes=new.findall('.//p:sp',ns)
  assert len(old_shapes)==len(new_shapes)==2
  for os,ns_ in zip(old_shapes,new_shapes):
   old_ps=os.findall('p:txBody/a:p',ns);new_ps=ns_.findall('p:txBody/a:p',ns)
   assert len(old_ps)==len(new_ps)
   for op,np in zip(old_ps,new_ps):
    ors=op.findall('a:r',ns);nrs=np.findall('a:r',ns)
    if ors:
     assert len(ors)==len(nrs)
     for a,b in zip(ors,nrs):
      ar=a.find('a:rPr',ns);br=b.find('a:rPr',ns)
      assert E.tostring(ar)==E.tostring(br),(i,'run style changed')
    for parent in [op,np]:
     for child in list(parent):
      if child.tag in [f'{{{ns["a"]}}}r',f'{{{ns["a"]}}}br',f'{{{ns["a"]}}}fld']:parent.remove(child)
  assert E.tostring(old)==E.tostring(new),(i,'non-text structure changed')
  checks.append({'slide':i,'shapes':2,'format_structure':'identical','existing_run_styles':'identical'})
 preserved=[name for name in originals if name.startswith(('ppt/slideMasters/','ppt/slideLayouts/','ppt/theme/','ppt/media/'))]
 assert all(originals[name]==data[name] for name in preserved)
 report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'slide_count':12,'format_checks':checks,'byte_identical_template_parts':len(preserved),'claim':'All original slide structures and paragraph properties match after removing text runs. Every original run style is unchanged. Added text in empty slots inherits the original paragraph end-run styling. Masters, layouts, themes and media are copied byte for byte.'}
 (build/'template-parity.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'slides':12,'format_checks':'pass','byte_identical_template_parts':len(preserved),'candidate':str(dest)}))
