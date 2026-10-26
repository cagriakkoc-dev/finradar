import json,urllib.request,datetime
oids={"ANHYT":"4028e4a140e95be70140ed40cb930098","AKSA":"4028e4a240f2ef470141175e189f0453"}
today=datetime.date.today();frm=(today-datetime.timedelta(days=10)).isoformat()
for t,o in oids.items():
    body=json.dumps({"fromDate":frm,"toDate":today.isoformat(),"memberType":"IGS","mkkMemberOidList":[o],"inactiveCompanies":"N","bdkMemberOidList":[],"subjectList":[],"srcCategory":"","index":"","market":"","isLate":"","term":"","ruleType":"","period":"","year":"","disclosureClass":""}).encode()
    req=urllib.request.Request("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria",data=body,headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0","Accept":"application/json"})
    try:
        r=urllib.request.urlopen(req,timeout=30);j=json.loads(r.read());print(t,r.status,len(j),[(x.get("disclosureIndex"),x.get("title")) for x in j[:3]])
    except Exception as e:print(t,"HATA",repr(e)[:300])
