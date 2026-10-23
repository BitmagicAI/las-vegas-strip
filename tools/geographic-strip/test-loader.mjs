import {existsSync} from 'node:fs';
export async function resolve(specifier,context,next){
 if(specifier.endsWith('.js') && specifier.startsWith('.') && context.parentURL){const url=new URL(specifier.slice(0,-3)+'.ts',context.parentURL);if(existsSync(url))return {url:url.href,shortCircuit:true};}
 return next(specifier,context);
}
