// Packaging only: retain each VLOD block's encoded bytes and identifiers verbatim.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
export function readBlocks(bytes) {
  if (bytes.readUInt32LE(0)!==0x444f4c56 || bytes.readUInt16LE(4)!==1) throw new Error('Expected VLOD 1');
  let at=8;
  const take=n=>{if(n<0 || at+n>bytes.length) throw new Error('Truncated VLOD'); const b=bytes.subarray(at,at+n);at+=n;return b;};
  const vint=()=>{let value=0,shift=0,b;do{b=take(1)[0];value+=(b&127)*2**shift;shift+=7;if(shift>49)throw new Error('Invalid varint');}while(b&128);return value;};
  const text=()=>take(vint()).toString('utf8');
  const result=[];
  for(let p=vint();p>0;p--){
    const part=text();
    for(let k=vint();k>0;k--){
      const start=at,key=text(),batches=vint();
      for(let b=0;b<batches;b++){
        vint();vint();take(4);vint();vint();take(vint());take(vint());
      }
      result.push({part,key,batches,bytes:bytes.subarray(start,at)});
    }
  }
  if(at!==bytes.length)throw new Error('Trailing VLOD bytes');
  return result;
}
function varint(n){const out=[];do{let b=n%128;n=Math.floor(n/128);if(n)b|=128;out.push(b);}while(n);return Buffer.from(out);}
function text(s){const b=Buffer.from(s);return Buffer.concat([varint(b.length),b]);}
export function encodeBlocks(blocks){
  const parts=new Map();
  for(const b of blocks){if(!parts.has(b.part))parts.set(b.part,[]);parts.get(b.part).push(b);}
  const header=Buffer.alloc(8);header.writeUInt32LE(0x444f4c56);header.writeUInt16LE(1,4);
  const out=[header,varint(parts.size)];
  for(const [part,list] of parts)out.push(text(part),varint(list.length),...list.map(b=>b.bytes));
  return Buffer.concat(out);
}
export function partitionLod(bytes,cityPart){
  const groups=new Map();
  for(const block of readBlocks(bytes)){
    let name;
    if(block.part===cityPart){
      const cell=block.key.split('/')[0];
      if(!/^(base|-?\d+,-?\d+)$/.test(cell))throw new Error(`Unexpected city block ${block.key}`);
      name=cell==='base'?'base':`cell-${cell.replace(',','_')}`;
    }else name='other-parts';
    if(!groups.has(name))groups.set(name,[]);groups.get(name).push(block);
  }
  if(groups.size<2)throw new Error(`City part not found: ${cityPart}`);
  return new Map([...groups].sort(([a],[b])=>a.localeCompare(b,'en')).map(([name,blocks])=>[name,encodeBlocks(blocks)]));
}
export function writeLodCells(input,output,cityPart){
  fs.mkdirSync(output,{recursive:true});const cells=[];
  for(const [name,bytes] of partitionLod(fs.readFileSync(input),cityPart)){
    const file=name+'.bin',dest=path.join(output,file);
    if(!fs.existsSync(dest)||!fs.readFileSync(dest).equals(bytes))fs.writeFileSync(dest,bytes);
    cells.push({file,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
  }
  const manifest=JSON.stringify({version:1,cellSize:800,cityPart,cells},null,2)+'\n';
  const dest=path.join(output,'manifest.json');
  if(!fs.existsSync(dest)||fs.readFileSync(dest,'utf8')!==manifest)fs.writeFileSync(dest,manifest);
  return cells;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
  const [input,output,cityPart]=process.argv.slice(2);
  if(!input||!output||!cityPart)throw new Error('Usage: lod-files.mjs input.bin output-directory city-part-id');
  console.log(JSON.stringify(writeLodCells(input,output,cityPart)));
}
