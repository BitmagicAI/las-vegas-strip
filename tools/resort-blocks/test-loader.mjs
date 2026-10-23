// Compile the same TypeScript geometry/visibility helpers used in the game.
import fs from 'node:fs/promises';
import ts from 'typescript';
export {resolve} from '../geographic-strip/test-loader.mjs';
export async function load(url,context,next){
 if(url.endsWith('.ts'))return {format:'module',shortCircuit:true,source:ts.transpileModule(await fs.readFile(new URL(url),'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText};
 if(url.endsWith('.json'))return {format:'module',shortCircuit:true,source:'export default '+await fs.readFile(new URL(url),'utf8')};
 return next(url,context);
}
