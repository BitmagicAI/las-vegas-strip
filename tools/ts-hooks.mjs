// Node loader hooks for running game modules in tests: transpiles project TypeScript with the project's
// `typescript`, maps `.js` specifiers to their `.ts` sources, and resolves the tsconfig aliases
// (`engine/…`, `types/…`, and the engine's own `bundle/…`, `core/…` and the rest, which engine modules import).
// Usage: node --import ./tools/ts-register.mjs <test.mjs>
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import ts from 'typescript';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const aliases={'engine/':path.join(root,'engine/engine/'),'types/':path.join(root,'engine/types/')};
for(const dir of ['bundle','debug','editor','core','baseline','genres','bitmagic'])aliases[dir+'/']=path.join(root,'engine',dir)+'/';
export async function resolve(specifier,context,next){
  for(const [prefix,dir] of Object.entries(aliases))if(specifier.startsWith(prefix)){specifier=pathToFileURL(path.join(dir,specifier.slice(prefix.length))).href;break;}
  if(/^(file:|\.|\/)/.test(specifier)&&specifier.endsWith('.js')){
    const url=new URL(specifier,context.parentURL),ts_=fileURLToPath(url).replace(/\.js$/,'.ts');
    if(fs.existsSync(ts_))return {url:pathToFileURL(ts_).href,shortCircuit:true};
  }
  return next(specifier,context);
}
export async function load(url,context,next){
  if(url.endsWith('.ts')&&url.startsWith('file:')){
    const file=fileURLToPath(url),out=ts.transpileModule(fs.readFileSync(file,'utf8'),{fileName:file,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022,verbatimModuleSyntax:false}}).outputText;
    return {format:'module',source:out,shortCircuit:true};
  }
  if(url.endsWith('.json')&&url.startsWith('file:'))return {format:'json',source:fs.readFileSync(fileURLToPath(url),'utf8'),shortCircuit:true};
  return next(url,context);
}
