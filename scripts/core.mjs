import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export const json=p=>JSON.parse(fs.readFileSync(p,'utf8'));
export function files(dir){let out=[];for(const e of fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name,'en'))){const p=path.join(dir,e.name);if(e.isSymbolicLink())throw Error(`Symlink forbidden: ${p}`);if(e.isDirectory())out.push(...files(p));else if(e.isFile())out.push(p);else throw Error(`Not a regular file: ${p}`);}return out;}
export function rel(base,p){return path.relative(base,p).split(path.sep).join('/');}
export function inside(base,p){const r=path.relative(base,path.resolve(base,p));if(path.isAbsolute(p)||r==='..'||r.startsWith('..'+path.sep))throw Error('Path outside package: '+p);return path.resolve(base,p);}
export function write(p,s){fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,s);}
export function selected(selection){const c=json(path.join(root,'catalog.json'));const m=selection==='all'?c.modules:c.modules.filter(m=>m.id===selection);if(!m.length)throw Error('Unknown module: '+selection);return {catalog:c,modules:m};}
export function inventory(dir){return Object.fromEntries(files(dir).map(p=>[rel(dir,p),hash(fs.readFileSync(p))]));}
export function skillMeta(s){const head=s.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);if(!head)throw Error('Missing YAML frontmatter');const result={};for(const line of head[1].split(/\r?\n/)){const m=line.match(/^(name|description):\s*(.+)$/);if(m){let v=m[2];if(v.startsWith('"'))v=JSON.parse(v);result[m[1]]=v;}}if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(result.name||'')||result.name.length>64||!result.description?.trim())throw Error('Invalid skill identity');return result;}

export const isMain = url => !!process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(url);

export function noSymlink(p){let q=path.resolve(p);while(true){try{if(fs.lstatSync(q).isSymbolicLink())throw Error('Symlink refused: '+q);}catch(e){if(e.code!=='ENOENT')throw e;}const parent=path.dirname(q);if(parent===q)break;q=parent;}}
