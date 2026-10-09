import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
import {strict} from './strict-content.mjs';
process.env.RUNTIME_NODE_MODULES='/Users/markyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const root='/Users/markyang/Projects/UNUK-Year-3/Y3_Autumn/COMP2013_DMS/lab';
const dir=root+'/.devops-build/strict';
const source=root+'/DevOps Template.pptx';
const python='/Users/markyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const skill='/Users/markyang/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const p=await PresentationFile.importPptx(await FileBlob.load(source));
for(let i=0;i<12;i++)p.slides.items[i].speakerNotes.text=strict[i].notes;
await fs.writeFile(dir+'/spec.json',JSON.stringify(strict,null,2));
await (await PresentationFile.exportPptx(p)).save(dir+'/notes-artifact.pptx');
console.log(execFileSync(python,[root+'/.devops-build/strict-preserve.py'],{encoding:'utf8'}));
const filled=await PresentationFile.importPptx(await FileBlob.load(dir+'/candidate.pptx'));
await fs.writeFile(dir+'/filled.ndjson',(await filled.inspect({kind:'slide,textbox,shape,notes,layout',maxChars:150000})).ndjson);
for(let i=0;i<12;i++){
 await fs.writeFile(dir+`/render/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await (await filled.slides.items[i].export({format:'png',scale:1})).arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:dir+'/candidate.pptx',finalPath:root+'/output/COMP2013_Lab2_DevOps_StrictTemplate.pptx',explicitTotalSlideCount:12,pythonExecutable:python,integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'reference',families:['Aptos Display','Aptos'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},verifyArtifactToolImport:true,receiptPath:dir+'/validation.json'});
console.log(JSON.stringify({finalPath:result.finalPath,slideCount:result.packageIntegrity.slide_count,findings:result.presentationLayout.findings,warnings:result.presentationLayout.warnings}));
