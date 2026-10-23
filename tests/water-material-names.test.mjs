// Exercise the actual pure classifier without booting its browser/engine imports.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import ts from 'typescript';
const source=ts.createSourceFile('RealisticWater.ts',fs.readFileSync('src/work/RealisticWater.ts','utf8'),ts.ScriptTarget.Latest,true);
const declaration=source.statements.find(n=>ts.isFunctionDeclaration(n)&&n.name?.text==='waterKind');
assert.ok(declaration);
const code=ts.transpileModule(ts.createPrinter().printNode(ts.EmitHint.Unspecified,declaration,source),{compilerOptions:{module:ts.ModuleKind.ES2022}}).outputText;
const {waterKind}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
for(const s of ['aria_pool','Strip / aria_pool','Strip / westin_pool','Strip / platinum_pool','fb_pool','Strip / nm_pool','mirage_water'])assert.equal(waterKind(s),'pool',s);
for(const s of ['Strip / vh-pool-tile','Strip / lake-underwater','pool-chair'])assert.equal(waterKind(s),null,s);
assert.equal(waterKind('Strip / lake-water'),'lake');assert.equal(waterKind('Strip / canal-water'),'canal');
console.log('12 actual water-material classification cases passed');
