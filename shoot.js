const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUT = '/home/shakan/til/screenshots';
if(!fs.existsSync(OUT)) fs.mkdirSync(OUT, {recursive:true});

const PAGES = [
  {id:'home', url:'/', name:'Басты бет', desc:'Жалпы көрініс + hero'},
  {id:'dict', url:'/', nav:'dict', name:'Сөздік'},
  {id:'gram', url:'/', nav:'gram', name:'Грамматика'},
  {id:'read', url:'/', nav:'read', name:'Оқу'},
  {id:'listen', url:'/', nav:'listen', name:'Тыңдау'},
  {id:'speak', url:'/', nav:'speak', name:'Сөйлеу'},
  {id:'quiz', url:'/', nav:'quiz', name:'Тест'},
  {id:'prov', url:'/', nav:'prov', name:'Мақал-мәтел'},
  {id:'jyr', url:'/', nav:'jyr', name:'Жыр-дастан'},
  {id:'tongue', url:'/', nav:'tongue', name:'Жаңылтпаш'},
  {id:'food', url:'/', nav:'food', name:'Тағам'},
  {id:'cloth', url:'/', nav:'cloth', name:'Киім'},
  {id:'legend', url:'/', nav:'legend', name:'Аңыз'},
  {id:'history', url:'/', nav:'history', name:'Тарих'},
  {id:'orn', url:'/', nav:'orn', name:'Ою-өрнек'},
  {id:'prog', url:'/', nav:'prog', name:'Прогресс'},
];

async function shoot(browser, p, width, height, prefix){
  const page = await browser.newPage();
  await page.setViewport({width, height});
  await page.goto('http://localhost:8790'+p.url, {waitUntil:'networkidle2', timeout:20000});
  await new Promise(r=>setTimeout(r, 800));
  // Навигация
  if(p.nav){
    // Sidebar-дағы модульді тауып басу
    const clicked = await page.evaluate((navId)=>{
      const btn = document.querySelector(`.sb-item[data-v="${navId}"]`);
      if(btn){ btn.click(); return true; }
      return false;
    }, p.nav);
    if(clicked){
      await new Promise(r=>setTimeout(r, 600));
    }
  }
  // Скриншот
  const file = path.join(OUT, `${prefix}_${p.id}.png`);
  await page.screenshot({path: file, fullPage: false});
  console.log(`✓ ${prefix}_${p.id}.png`);
  await page.close();
}

(async()=>{
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
  });
  
  // Desktop 1440x900
  for(const p of PAGES){
    try{ await shoot(browser, p, 1440, 900, 'desktop'); }
    catch(e){ console.error(`ERR desktop ${p.id}:`, e.message); }
  }
  
  // Mobile 390x844
  for(const p of PAGES.slice(0, 8)){ // 8 mobile скриншот жеткілікті
    try{ await shoot(browser, p, 390, 844, 'mobile'); }
    catch(e){ console.error(`ERR mobile ${p.id}:`, e.message); }
  }
  
  await browser.close();
  console.log('Дайын! Скриншоттар:', fs.readdirSync(OUT).length);
})();
