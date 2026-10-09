import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
import {deck} from './content.mjs';
process.env.RUNTIME_NODE_MODULES='/Users/markyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const root='/Users/markyang/Projects/UNUK-Year-3/Y3_Autumn/COMP2013_DMS/lab';
const build=root+'/.devops-build';
const skill='/Users/markyang/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const source=root+'/DevOps Template.pptx';
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const originals=[...p.slides.items];
const outputs=[];
for(const spec of deck){const slide=originals[spec.source].duplicate();slide.moveTo(p.slides.items.length-1);outputs.push(slide);}
const outputIds=new Set(outputs.map(x=>x.id));
p.slides.keep(p.slides.items.map((s,i)=>outputIds.has(s.id)?i:null).filter(i=>i!==null));
if(p.slides.items.length!==deck.length)throw new Error('Slide count mismatch');
console.log('Slides',deck.length);
const records=(await p.inspect({kind:'slide,textbox,shape',maxChars:180000})).ndjson.split('\n').filter(Boolean).map(l=>JSON.parse(l));
function text(s,name,value,x,y,w,h,size=30,color='#000000',bold=false){
 const sh=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=value;
 sh.text.style={typeface:'Aptos',fontSize:size,color,bold,alignment:'left',verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0};
 return sh;
}
const tableSlides=[];
for(let i=0;i<deck.length;i++){
 const spec=deck[i],s=p.slides.items[i];
 const shapeRecs=records.filter(x=>x.slideIndex===i && ['textbox','shape'].includes(x.kind));
 const titleRec=shapeRecs.find(x=>x.placeholder==='title')||shapeRecs[0];
 const title=p.resolve(titleRec.id);
 title.text=spec.kind==='cover'?'Understanding and Applying DevOps Principles':spec.title;
 if(spec.kind==='cover'){
  title.text.style={typeface:'Aptos Display',fontSize:80,bold:false,color:'#000000',alignment:'center',verticalAlignment:'middle',insets:0,autoFit:'none'};
  const sub=shapeRecs.find(x=>x.placeholder==='subtitle');
  const st=p.resolve(sub.id);st.text=spec.subtitle;
  st.text.style={typeface:'Aptos',fontSize:32,color:'#000000',alignment:'center',verticalAlignment:'top',autoFit:'none',insets:0};
 }else{
  title.position={left:88,top:38.33,width:1104,height:139.17};
  title.text.style={typeface:'Aptos Display',fontSize:58.67,bold:false,color:'#000000',alignment:'left',verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'square'};
  const remove=shapeRecs.filter(x=>x.id!==titleRec.id).map(x=>x.id);
  if(remove.length)p.delete(remove);
  if(spec.kind==='team'){
   text(s,'members-label',spec.blocks[0][0],88,192,1104,35,28,'#C00000');
   text(s,'members',spec.blocks[0][1],88,248,1104,178,37.33);
   text(s,'team-admin-label',spec.blocks[1][0],88,485,1104,35,28,'#C00000');
   text(s,'team-admin',spec.blocks[1][1],88,538,1104,64,32);
  }else if(spec.kind==='blocks'){
   spec.blocks.forEach(([label,value],j)=>{
    const y=190+j*157;
    text(s,`block-${j+1}-label`,label,88,y,1104,36,26.67,'#C00000');
    text(s,`block-${j+1}-text`,value,88,y+40,1104,113,28);
   });
  }else if(spec.kind==='table'){
   tableSlides.push(i+1);
   const vals=[spec.headers,...spec.rows];
   const t=s.tables.add({rows:vals.length,columns:spec.headers.length,left:88,top:192,width:1104,height:440,columnWidths:spec.widths,values:vals});
   t.borders.assign({style:'solid',fill:'#D9D9D9',width:1});
   t.cells.block({row:0,column:0,rowCount:vals.length,columnCount:spec.headers.length}).assign({textStyle:{typeface:'Aptos',fontSize:24,color:'#000000'},margins:{top:5,bottom:5,left:12,right:12},anchor:'top'});
   for(let r=0;r<vals.length;r++){
    t.rows[r].height=r===0?52:(388/spec.rows.length);
    for(let c=0;c<spec.headers.length;c++){
     const cell=t.getCell(r,c);
     cell.fill=r===0?'#F2F2F2':'#FFFFFF';
     cell.text.style={typeface:'Aptos',fontSize:24,color:'#000000',bold:r===0,autoFit:'none',verticalAlignment:'top'};
    }
   }
   if(spec.foot)text(s,'table-footnote',spec.foot,88,646,1080,44,21.33,'#595959');
  }
  text(s,'page-number',String(i+1).padStart(2,'0'),1165,693,38,22,16,'#7F7F7F');
 }
 s.speakerNotes.text=spec.notes;
}
await fs.mkdir(build+'/draft',{recursive:true});await fs.mkdir(build+'/render',{recursive:true});
await fs.writeFile(build+'/authored.ndjson',(await p.inspect({kind:'slide,textbox,table,notes',maxChars:260000})).ndjson);
for(let i=0;i<p.slides.items.length;i++){
 const s=p.slides.items[i];
 await fs.writeFile(build+`/render/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await (await s.export({format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(build+`/render/slide-${String(i+1).padStart(2,'0')}.json`,await (await s.export({format:'layout'})).text());
}
await fs.writeFile(build+'/render/montage.webp',new Uint8Array(await (await p.export({format:'webp',montage:true,scale:0.5})).arrayBuffer()));
const candidate=build+'/draft/reference.pptx';
await (await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:root+'/output/COMP2013_Lab2_DevOps_Reference.pptx',pythonExecutable:'/Users/markyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableSlides.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableSlides,fontPolicy:{basis:'reference',families:['Aptos Display','Aptos'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},verifyArtifactToolImport:true,receiptPath:build+'/validation.json'});
console.log(JSON.stringify(result));
