import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const root='/Users/markyang/Projects/UNUK-Year-3/Y3_Autumn/COMP2013_DMS/lab';
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/DevOps Template.pptx'));
await fs.writeFile(root+'/.devops-build/source/inspect.ndjson',(await p.inspect({kind:'slide,layout,textbox,shape',maxChars:120000})).ndjson);
for(let i=0;i<p.slides.items.length;i++){
 const s=p.slides.items[i];
 await fs.writeFile(root+`/.devops-build/source/slide-${i+1}.png`,new Uint8Array(await (await s.export({format:'png',scale:1})).arrayBuffer()));
 if([0,1,2,4,7].includes(i))console.log(JSON.stringify({i,shapes:s.shapes.items.map(x=>({id:x.id,text:x.text?.toString(),pos:x.position,style:x.text?.style})),frame:s.frame}));
}
await fs.writeFile(root+'/.devops-build/source/montage.webp',new Uint8Array(await (await p.export({format:'webp',montage:true})).arrayBuffer()));
