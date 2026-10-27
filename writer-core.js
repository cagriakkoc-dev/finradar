(function(root){
'use strict';
const parts=text=>text.split(/\n\s*———\s*\n/).map(x=>x.trim()).filter(Boolean);
const numbers=text=>(text.match(/\d+(?:[.,]\d+)*/g)||[]).join('|');
function markdown(c){const u=c.summary.substack;if(!u)return '';return '# '+u.title+'\n\n'+(u.subtitle?u.subtitle+'\n\n':'')+u.blocks.map(b=>b.h?'## '+b.h:b.p||b.cta||(b.url?'!['+(b.alt||'')+']('+b.url+')':'![Görsel '+(b.img+1)+']('+c.t+'-'+c.summary.p+'-substack-'+(b.img+1)+'.png)')).join('\n\n')+'\n\nKaynaklar: '+u.sources.map(s=>'['+s.l+']('+s.u+')').join(' · ')+'\n\n'+u.disclaimer;}
function source(c){return {x:(c.summary.social?.tweets||[]).map(t=>t.t).join('\n\n———\n\n'),substack:markdown(c)};}
function review(text,original,platform){const warnings=[];
 if(numbers(text)!==numbers(original))warnings.push('Rakam veya numaralama değişti. Kaynak tabloyla yeniden karşılaştır.');
 if(/portföy|satın ald|beklentim|tahminlerinin üzerinde|daha istikrarlı/i.test(text))warnings.push('Kişisel beyan veya karşılaştırmalı yorum var; sana ait olduğunu ve dayanağını kontrol et.');
 if(platform==='x')parts(text).forEach((t,i,a)=>{if([...t].length>280)warnings.push((i+1)+'. parça 280 karakteri aşıyor.');if(!t.endsWith('('+(i+1)+'/'+a.length+')'))warnings.push((i+1)+'. parçanın zincir numarası güncel değil.');});
 return warnings;}
function record(profile,example,rule,date){if(!example.trim()||!rule.trim())throw Error('Örnek ve çıkarılan kural birlikte gerekli.');return profile+'\n\n## Onayladığım yazı örneği · '+date+'\n\n'+example.trim().split('\n').map(l=>'> '+l).join('\n')+'\n\nTercihim: '+rule.trim()+'\n';}
const api={parts,numbers,source,review,record};if(typeof module!=='undefined')module.exports=api;else root.FRWriterCore=api;
})(typeof window!=='undefined'?window:this);
