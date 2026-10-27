import json,os,re
F='/home/claude/finradar/index.html'
s=open(F,encoding='utf-8').read()
A='<script type="application/json" id="data">'
a=s.index(A)+len(A);b=s.index('</script>',a)
D=json.loads(s[a:b])
fin=json.load(open('fin.json'));rat=json.load(open('rat.json'))
mix=json.load(open('mix.json')) if os.path.exists('mix.json') else []
c={"t":"TOASO","name":"Tofaş","sector":"Otomotiv · üretim ve dağıtım","color":"#8a1538","accent":"#d6457a",
 "intro":"Üretim ve satış adetleri, yurt içi ve ihracat dağılımı, Stellantis ile üretim sözleşmeleri ve Nisan 2025'te devralınan Stellantis Otomotiv Pazarlama'nın dağıtım gelirleri birlikte takip edilir.",
 "drivers":[["Yurt içi / yurt dışı satış","Coğrafi gelir bağımlılığını gösterir. Stellantis Otomotiv Pazarlama'nın devri 30.04.2025'te tamamlandı (KAP 1432149); o tarihten sonra Stellantis markalarının Türkiye dağıtımı da yurt içi satışlara eklendi. Dönemler arası kıyasta bu kapsam değişikliği dikkate alınır."],
  ["Üretim ve satış adetleri","Hacim ve ürün karmasını gösterir. Model bazında kârlılık açıklanmadığında tahmin edilmez."],
  ["Brüt ve esas faaliyet marjı","Fiyatlama, ürün karması ve maliyetlerin birlikte etkisini gösterir. Dağıtım faaliyetinin marj yapısı üretimden farklıdır; 2025 sonrası marjlar bu karışımı yansıtır."],
  ["Stellantis ile üretim sözleşmeleri","Yeni model (K0, K9 ticari araç) yatırımları ve mevcut modellerin üretim süreleri gelecekteki hacmi belirler. Sözleşme, kredi ve kapasite bilgileri KAP açıklamalarından izlenir."],
  ["Finans sektörü faaliyetleri","Konsolide gelirin bir bölümü Koç Fiat Kredi'nin finansman faaliyetlerinden gelir. Bu sitede hasılat ve satışların maliyeti bu kalemlerle birlikte gösterilir."]],
 "kap":"https://www.kap.org.tr/tr/sirket-bildirimleri/1096-tofas-turk-otomobil-fabrikasi-a-s",
 "rat":rat['rat'],"mix":mix,"div":rat['div'],"kpi":[],"ms":[],"periods":fin['periods'],"fin":fin['fin']}
D['companies']=[x for x in D['companies'] if x['t']!='TOASO']+[c]
D['companies'].sort(key=lambda x:x['t'])
s=s[:a]+json.dumps(D,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+s[b:]
L='<script type="application/json" id="logos">'
a=s.index(L)+len(L);b=s.index('</script>',a)
LO=json.loads(s[a:b]);LO['TOASO']=open('/tmp/claude-0/-home-claude/307afc32-c2ae-55fc-bd6d-e9d9bcfd5576/scratchpad/toaso_logo.b64').read().strip()
s=s[:a]+json.dumps(LO)+s[b:]
if "TOASO:'" not in s:
    s=s.replace("FROTO:'#4fb3e8',ISMEN:'#e3a21a',TUPRS:'#e5484d'}","FROTO:'#4fb3e8',ISMEN:'#e3a21a',TOASO:'#d6457a',TUPRS:'#e5484d'}",1)
open(F,'w',encoding='utf-8').write(s)
print('ok',[x['t'] for x in D['companies']], len(mix))
