import json,os,re
F='/home/claude/finradar/index.html'
s=open(F,encoding='utf-8').read()
A='<script type="application/json" id="data">'
a=s.index(A)+len(A);b=s.index('</script>',a)
D=json.loads(s[a:b])
fin=json.load(open('fin.json'));rat=json.load(open('rat.json'))
mix=json.load(open('mix.json')) if os.path.exists('mix.json') else []
SEC=json.load(open('sector.json'))
c={"t":"TTRAK","name":"Türk Traktör","sector":"Tarım makineleri · traktör üretimi","color":"#0e7490","accent":"#22b8cf",
 "intro":"Yurt içi traktör pazarı, ihracat adetleri, ürün fiyatlaması ve finansman koşulları (tarım kredileri, faiz) birlikte takip edilir. Şirket New Holland ve Case IH markalarıyla Türkiye traktör pazarının lideridir; ortakları Koç Holding ve CNH Industrial'dır.",
 "drivers":[["Yurt içi traktör pazarı ve pazar payı","Hasılatın büyük kısmı yurt içi satışlardan gelir. Pazar büyüklüğü ve TÜİK tescil verisine göre pay yıllık faaliyet raporunda açıklanır; ara dönemlerde açıklanmaz."],
  ["İhracat adetleri","Ürettiği traktörlerin bir bölümünü ihraç eder; yurt dışı satış payı kur ve Avrupa talebiyle değişir. Şirket Türkiye traktör ihracatının büyük bölümünü tek başına yapar."],
  ["Satış indirimleri ve fiyatlama","Brüt satışlardan yapılan indirimler hasılatın önemli bir kısmına denk gelir; kampanya ve finansman destekleri marjı doğrudan etkiler."],
  ["Finansman maliyeti ve tarım kredileri","Traktör talebi çiftçi kredilerine ve faize duyarlıdır. Şirketin kendi borçlanma maliyeti de faaliyet raporunda açıklanır (ağırlıklı ortalama faiz)."],
  ["Yatırımlar ve teşvikler","Erenler ve Ankara fabrikalarındaki yatırımlar, aktifleştirilen geliştirme giderleri ve teşvik kaynaklı vergi varlıkları faaliyet raporlarından izlenir."]],
 "kap":"https://www.kap.org.tr/tr/sirket-bildirimleri/1393-turk-traktor-ve-ziraat-makineleri-a-s",
 "rat":rat['rat'],"mix":mix,"div":rat['div'],"kpi":SEC["kpi"],"kpiNotes":SEC["kpiNotes"],"ms":SEC["ms"],"periods":fin['periods'],"fin":fin['fin']}
D['companies']=[x for x in D['companies'] if x['t']!='TTRAK']+[c]
D['companies'].sort(key=lambda x:x['t'])
s=s[:a]+json.dumps(D,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+s[b:]
L='<script type="application/json" id="logos">'
a=s.index(L)+len(L);b=s.index('</script>',a)
LO=json.loads(s[a:b]);LO['TTRAK']=open('ttrak_logo.b64').read().strip()
s=s[:a]+json.dumps(LO)+s[b:]
if "TTRAK:'" not in s:
    s=s.replace("TOASO:'#d6457a',TUPRS:'#e5484d'}","TOASO:'#d6457a',TTRAK:'#22b8cf',TUPRS:'#e5484d'}",1)
open(F,'w',encoding='utf-8').write(s)
print('ok',[x['t'] for x in D['companies']], len(mix))
