const test=require('node:test'),assert=require('node:assert/strict'),C=require('./writer-core');
test('zincir parçaları ve numaralama',()=>{assert.deepEqual(C.parts('Bir (1/2)\n\n———\n\nİki (2/2)'),['Bir (1/2)','İki (2/2)']);assert.equal(C.review('Bir (1/1)','Bir (1/1)','x').length,0);assert.ok(C.review('Bir (1/2)','Bir (1/2)','x').length)});
test('rakam değişikliğini yakalar',()=>{assert.ok(C.review('Kâr 2.309,5','Kâr 2.308,5','substack').some(x=>x.includes('Rakam')))});
test('tercihsiz örneği öğrenme saymaz',()=>{assert.throws(()=>C.record('profil','örnek','','2026-10-27'));assert.match(C.record('profil','örnek','kısa cümle','2026-10-27'),/Tercihim: kısa cümle/)});
test('kaynak nesnesi değiştirilmez',()=>{const c={t:'ANHYT',summary:{social:{tweets:[{t:'Metin (1/1)'}]}}};const before=JSON.stringify(c);assert.equal(C.source(c).x,'Metin (1/1)');assert.equal(C.source(c).substack,'');assert.equal(JSON.stringify(c),before)});
test('uzun parça ve kişisel iddia uyarısı',()=>{assert.ok(C.review('a'.repeat(281),'','x').some(x=>x.includes('280')));assert.ok(C.review('portföyüm','portföyüm','substack').length)});
