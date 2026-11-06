'use strict';
const $ = id => document.getElementById(id);
const token = document.querySelector('meta[name="app-token"]').content;
const colors = ['#518779','#98b5a4','#e3bd79','#91a7c6','#b6a3c4','#c3cbd2','#ce9b86','#8fa99a'];
let data = null, currentTab = 'overview', plan = null, suggested = '', busy = false;
let lastScan = null, noticeState = null;
const titles = {
    overview: ['Genel bakış','Dosyalarına yer aç.','İndirilenlerini düzenle, aynı dosyaları keşfet, alanını geri kazan.'],
    files: ['Dosyalar','Her dosya, gözünün önünde.','Klasöründeki dosyaları ara ve alan kullanımını incele.'],
    duplicates: ['Aynı dosyalar','Bir kopyası yeter.','Aynı içeriğe sahip dosyaları güvenle keşfet.'],
    history: ['İşlem geçmişi','Her adım kayıt altında.','Taşıma işlemlerini incele ve gerektiğinde geri al.']
};
function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
}
function bytes(n) {
    if (n === 0) return '0 B';
    const units = ['B','KB','MB','GB','TB'];
    const i = Math.min(4, Math.floor(Math.log(n) / Math.log(1024)));
    return (n / 1024 ** i).toLocaleString(locale(), {maximumFractionDigits: i ? 1 : 0}) + ' ' + units[i];
}
function notice(key, error = false, values = {}, details = []) {
    noticeState = {key, error, values, details};
    renderNotice();
}
function renderNotice() {
    if (!noticeState) return;
    const {key, error, values, details} = noticeState;
    $('notice').textContent = translatedError(t(key, values)) + (details.length ? '\n' + details.map(translatedError).join('\n') : '');
    $('notice').className = error ? 'error' : '';
    $('notice').hidden = false;
}
async function api(path, body = {}) {
    const response = await fetch('/api/' + path, {
        method: 'POST', headers: {'Content-Type':'application/json','X-App-Token':token}, body:JSON.stringify(body)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'İşlem tamamlanamadı.');
    return result;
}
async function task(fn, label = 'Dosyalar inceleniyor…') {
    if (busy) return;
    busy = true;
    $('busyText').textContent = t(label);
    $('busy').hidden = false;
    try { await fn(); }
    catch (e) { notice(e.message, true); }
    finally { busy = false; $('busy').hidden = true; }
}
function tab(name) {
    currentTab = name;
    for (const key of Object.keys(titles)) {
        $(key).hidden = key !== name;
        document.querySelector(`[data-tab="${key}"]`).classList.toggle('active', key === name);
    }
    [$('pageName').textContent, $('title').textContent, $('subtitle').textContent] = titles[name].map(key => t(key));
}
function fileRow(f, extra) {
    const row = el('div','file-row');
    row.append(el('div','file-icon',(f.name.includes('.') ? f.name.split('.').pop() : 'FILE').slice(0,5).toUpperCase()));
    const info = el('div','file-info');
    // Actual names and paths must never be translated.
    info.append(el('strong','',f.name), el('small','',f.path));
    row.append(info, extra ? el('span','keep-tag',t(extra)) : el('span','file-type',t(f.category)), el('span','file-size',bytes(f.size)));
    return row;
}
function files() {
    if (!data) return;
    const query = $('search').value.toLocaleLowerCase(locale());
    const list = data.files.filter(f => f.path.toLocaleLowerCase(locale()).includes(query));
    $('fileList').replaceChildren(...list.slice(0,500).map(f => fileRow(f)));
    $('fileLimit').textContent = t(list.length > 500 ? '{count} sonuçtan ilk 500 dosya gösteriliyor. Aramayı daraltabilirsin.' : '{count} dosya', {count:list.length});
}
function render() {
    $('empty').hidden = true;
    $('workspace').hidden = false;
    $('auto').checked = data.auto;
    $('statCount').textContent = data.count.toLocaleString(locale());
    $('statSize').textContent = bytes(data.size);
    $('statWaste').textContent = bytes(data.wasted);
    $('statGroups').textContent = t('{count} kopya grubu', {count:data.duplicates.length});
    $('duplicateBadge').textContent = data.duplicates.length;
    $('statFree').textContent = bytes(data.disk.free);
    $('diskTotal').textContent = t('{size} toplam disk alanı', {size:bytes(data.disk.total)});
    $('chartSize').textContent = bytes(data.size);
    const categories = Object.entries(data.categories).sort((a,b) => b[1].size - a[1].size);
    let angle = 0;
    const stops = [];
    $('legend').replaceChildren();
    categories.forEach(([name,values],i) => {
        const next = angle + (data.size ? values.size / data.size * 360 : 0);
        stops.push(`${colors[i % colors.length]} ${angle}deg ${next}deg`);
        angle = next;
        const row = el('div','legend-row'), dot = el('i');
        dot.style.background = colors[i % colors.length];
        row.append(dot, el('span','',t(name)), el('b','',bytes(values.size)));
        $('legend').append(row);
    });
    $('donut').style.background = data.size ? 'conic-gradient(' + stops.join(',') + ')' : '#edf0f2';
    const fraction = data.disk.total ? data.disk.used / data.disk.total * 100 : 0;
    $('diskPercent').textContent = t('{percent}% · {size} kullanılıyor', {percent:fraction.toLocaleString(locale(), {maximumFractionDigits:1}),size:bytes(data.disk.used)});
    $('diskBar').style.width = fraction + '%';
    $('largest').replaceChildren(...data.largest.slice(0,5).map(f => fileRow(f)));
    if (!data.files.length) $('largest').append(el('p','muted',t('Henüz dosya yok.')));
    files();
    $('duplicateList').replaceChildren();
    for (const group of data.duplicates) {
        const box = el('div','duplicate-group'), title = el('div','group-title');
        title.append(el('strong','',t('{count} aynı dosya',{count:group.files.length})),el('span','',t('{size} fazla alan',{size:bytes(group.wasted)})));
        box.append(title,...group.files.map((f,i) => fileRow(f,i === 0 ? 'Korunacak' : 'Karantinaya taşınacak')));
        $('duplicateList').append(box);
    }
    if (!data.duplicates.length) $('duplicateList').append(el('p','muted',t('Güzel haber: aynı içerikli dosya bulunamadı.')));
    $('clean').disabled = !data.duplicates.length;
    $('historyList').replaceChildren();
    for (const entry of data.history) {
        const row = el('div','history-row'), info = el('div');
        info.append(el('strong','',t(entry.label)),el('small','',t('{date} · {count} kayıt',{date:new Date(entry.time*1000).toLocaleString(locale()),count:entry.count})));
        const button = el('button','secondary',t(entry.undone ? 'Geri alındı' : 'Geri al'));
        button.disabled = entry.undone;
        button.onclick = () => task(async () => {
            const result = await api('undo',{id:entry.id}); await scan(); showResult(result,'undo');
        }, 'Dosyalar ilk konumlarına taşınıyor…');
        row.append(info,button); $('historyList').append(row);
    }
    if (!data.history.length) $('historyList').append(el('p','muted',t('Henüz bir taşıma işlemi yapılmadı.')));
    $('lastScan').textContent = t('Son tarama {time}',{time:lastScan.toLocaleTimeString(locale())}) + (data.last_auto ? t(' · Otomatik: ') + autoStatus(data.last_auto) : '');
    tab(currentTab);
}
async function scan() {
    data = await api('scan'); lastScan = new Date(); $('folder').value = data.root; render();
    if (data.errors.length) notice('Bazı dosyalar taranamadı:',true,{},data.errors.slice(0,5));
}
function showResult(result, kind) {
    notice(kind === 'undo' ? '{count} dosya geri alındı.' : '{count} dosya taşındı.',result.errors.length > 0,{count:result.count},result.errors.length ? ['Atlanan işlemler:',...result.errors.slice(0,8)] : []);
}
function renderPreview() {
    if (!plan) return;
    $('previewTitle').textContent = t(plan.kind === 'organize' ? 'Dosyaları yerlerine taşı.' : 'Fazla kopyaları karantinaya taşı.');
    $('previewDescription').textContent = t(plan.moves.length ? '{count} dosya taşınacak. Mevcut dosyaların üzerine yazılmaz. Önizleme 5 dakika geçerlidir.' : 'Taşınacak dosya bulunamadı. Son 10 saniyede değişen dosyalar ve alt klasörlerdeki dosyalar düzenlemeye dahil edilmez.',{count:plan.moves.length});
    $('moveList').replaceChildren(...plan.moves.map(move => {
        const row = el('div','move-row',move.src);
        row.append(el('span','','→ ' + move.dst)); return row;
    }));
    $('apply').disabled = !plan.moves.length;
}
async function preview(kind) {
    await task(async () => {plan = await api('preview',{kind}); renderPreview(); $('preview').showModal();});
}
$('select').onclick = () => task(async () => {
    await api('root',{path:$('folder').value}); noticeState = null; $('notice').hidden = true; await scan();
});
$('folder').addEventListener('keydown',e => {if (e.key === 'Enter') $('select').click();});
$('useDownloads').onclick = () => {$('folder').value = suggested; $('select').click();};
$('refresh').onclick = () => task(scan);
$('organize').onclick = () => preview('organize');
$('clean').onclick = () => preview('duplicates');
$('search').oninput = files;
$('auto').onchange = () => {
    const enabled = $('auto').checked;
    task(async () => {
        try {
            const result = await api('auto',{enabled});
            $('auto').checked = result.auto;
            if (data) data.auto = result.auto;
            notice(result.auto ? 'Otomatik düzenleme açık. Uygulama açıkken ana klasördeki tamamlanmış dosyalar 15 saniyede bir düzenlenir.' : 'Otomatik düzenleme kapatıldı.');
        } catch(e) { $('auto').checked = !enabled; throw e; }
    });
};
$('apply').onclick = () => {
    const planToken = plan.token;
    $('preview').close();
    task(async () => {const result = await api('apply',{token:planToken}); await scan(); showResult(result,'move');},'Dosyalar taşınıyor ve işlem kaydediliyor…');
};
$('close').onclick = $('cancel').onclick = () => $('preview').close();
document.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => tab(b.dataset.tab));
document.querySelectorAll('[data-go]').forEach(b => b.onclick = () => tab(b.dataset.go));
function updateLanguage() {
    translateStatic();
    $('language').value = language;
    if (data) render(); else tab(currentTab);
    renderPreview(); renderNotice();
}
$('language').onchange = () => {
    language = $('language').value === 'de' ? 'de' : 'tr';
    try { localStorage.setItem('derli-language',language); } catch (_) {}
    updateLanguage();
};
updateLanguage();
task(async () => {
    const status = await api('status'); suggested = status.suggested;
    $('folder').value = status.root || suggested;
    if (status.root) await scan();
});
