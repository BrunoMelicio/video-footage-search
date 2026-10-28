const $ = id => document.getElementById(id);
let currentVideo=null, selectedSample=null, samples=[], indexing=false, searching=false;
const timeLabel = seconds => {const s=Math.floor(seconds||0);return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;};
function status(text){$('status').textContent=text;}
function controls(){
  $('load').disabled=!selectedSample||indexing||searching;
  $('upload').disabled=indexing||searching;
  document.querySelector('label[for="upload"]').classList.toggle('busy',indexing||searching);
  $('search').disabled=!currentVideo||indexing||searching;
  document.querySelectorAll('.recording').forEach(button=>button.disabled=indexing||searching);
  $('back').disabled=$('forward').disabled=!$('player').getAttribute('src');
}
async function api(path,options){const response=await fetch(path,options);const body=await response.json();if(!response.ok)throw Error(body.error||'Request failed');return body;}
function clearResults(){
  $('results').replaceChildren();$('timeline').replaceChildren();$('result-count').textContent='0 results';
  $('result-context').textContent='Index this recording, then describe what you want to find.';
}
function showDuration(duration){$('duration-label').textContent=timeLabel(duration);$('timeline-end').textContent=timeLabel(duration);}
function chooseSample(sample){
  if(indexing||searching)return;
  selectedSample=sample;currentVideo=null;clearResults();$('query').value='';
  $('player').pause();$('player').removeAttribute('poster');$('player').src='/sample-preview.mp4?id='+encodeURIComponent(sample.id);
  $('video-name').textContent=sample.name;$('source-label').textContent=sample.source;
  $('source-detail').textContent=`${sample.duration.toFixed(1)} seconds · Research sample`;
  $('index-state').textContent='Not indexed';showDuration(sample.duration);
  document.querySelectorAll('.recording').forEach(button=>button.classList.toggle('active',button.dataset.id===sample.id));
  const link=document.createElement('a');link.href=sample.sourceUrl;link.target='_blank';link.rel='noreferrer';link.textContent=sample.source;
  $('credits').replaceChildren('Footage: ',link,` · ${sample.license} · Shortened, converted; no audio.`);
  $('examples').replaceChildren(...sample.queries.map(query=>{
    const button=document.createElement('button');button.textContent=query;
    button.addEventListener('click',()=>{$('query').value=query;if(currentVideo)runSearch();else status('Index this recording to search its frames.');});return button;
  }));
  status('Preview ready. Index this recording to enable visual search.');controls();
}
async function loadVideo(path,options={method:'POST'}){
  if(indexing||searching)return;indexing=true;currentVideo=null;clearResults();controls();$('index-state').textContent='Indexing…';status('Preparing recording…');
  try{
    const start=await api(path,options);let job;
    do{await new Promise(r=>setTimeout(r,700));job=await api('/api/job?id='+encodeURIComponent(start.jobId));status(job.message);}while(job.state==='queued'||job.state==='indexing');
    if(job.state!=='ready')throw Error(job.message);
    currentVideo=job.video;$('player').src=currentVideo.video;$('player').poster=currentVideo.poster;
    $('video-name').textContent=currentVideo.name;showDuration(currentVideo.duration);
    $('index-state').textContent=`${currentVideo.frameCount} frames indexed`;
    $('result-context').textContent='Describe a scene to find candidate moments.';
    status(`Ready to search · Sampled every ${currentVideo.interval} seconds · Review surrounding footage for context.`);
  }catch(e){$('index-state').textContent='Index failed';status(e.message);}finally{indexing=false;controls();}
}
$('load').addEventListener('click',()=>{if(selectedSample)loadVideo('/api/sample?id='+encodeURIComponent(selectedSample.id));});
$('upload').addEventListener('change',()=>{
  const file=$('upload').files[0];if(!file)return;
  if(file.size>50*1024*1024){status('Choose a recording under 50 MB.');$('upload').value='';return;}
  selectedSample=null;document.querySelectorAll('.recording').forEach(button=>button.classList.remove('active'));
  $('source-label').textContent='IMPORTED RECORDING';$('source-detail').textContent=file.name;
  $('credits').textContent='Imported locally · Browser preview has no audio.';$('examples').replaceChildren();
  loadVideo('/api/upload',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});$('upload').value='';
});
function jumpTo(result,row,marker){
  $('player').currentTime=result.timestamp;$('player').play().catch(()=>{});
  document.querySelectorAll('.result-row,.timeline-marker').forEach(item=>item.classList.remove('selected','active'));
  row.classList.add('selected');marker.classList.add('active');
}
async function runSearch(){
  const query=$('query').value.trim();if(!currentVideo||!query||indexing||searching)return;
  searching=true;controls();status('Searching visual frames…');
  try{
    const body=await api('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({videoId:currentVideo.id,query})});
    $('results').replaceChildren();$('timeline').replaceChildren();
    body.results.forEach((result,index)=>{
      const row=document.createElement('article');row.className='result-row';
      const image=document.createElement('img');image.src=result.thumbnail;image.alt=`Candidate frame at ${timeLabel(result.timestamp)}`;
      const info=document.createElement('div');info.className='result-info';
      const stamp=document.createElement('strong');stamp.textContent=timeLabel(result.timestamp);
      const score=document.createElement('p');score.textContent=`Rank ${index+1} · Similarity ${result.similarity.toFixed(3)}`;
      const button=document.createElement('button');button.className='jump';button.textContent='Review moment';button.setAttribute('aria-label',`Review moment ${timeLabel(result.timestamp)}`);
      const marker=document.createElement('button');marker.className='timeline-marker';marker.style.left=`${100*result.timestamp/currentVideo.duration}%`;marker.setAttribute('aria-label',`Candidate ${index+1} at ${timeLabel(result.timestamp)}`);
      const review=()=>jumpTo(result,row,marker);button.addEventListener('click',review);marker.addEventListener('click',review);
      info.append(stamp,score,button);row.append(image,info);$('results').append(row);$('timeline').append(marker);
    });
    $('result-count').textContent=`${body.results.length} candidates`;$('result-context').textContent=`For “${query}”`;
    status('Search complete · These are nearest visual matches, not confirmed detections.');
  }catch(e){status(e.message);}finally{searching=false;controls();}
}
$('search-form').addEventListener('submit',e=>{e.preventDefault();runSearch();});
function updatePlayhead(){$('playhead').textContent=`${timeLabel($('player').currentTime)} / ${timeLabel($('player').duration)}`;}
['timeupdate','loadedmetadata','durationchange'].forEach(event=>$('player').addEventListener(event,updatePlayhead));
const importControl=document.querySelector('label[for="upload"]');
importControl.setAttribute('tabindex','0');importControl.setAttribute('role','button');
importControl.addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&!$('upload').disabled){event.preventDefault();$('upload').click();}});
function nudge(delta){const player=$('player');if(Number.isFinite(player.duration))player.currentTime=Math.max(0,Math.min(player.duration,player.currentTime+delta));}
$('back').addEventListener('click',()=>nudge(-5));$('forward').addEventListener('click',()=>nudge(5));
async function init(){
  try{
    const data=await api('/api/samples');samples=data.samples;
    $('recordings').replaceChildren(...samples.map(sample=>{
      const button=document.createElement('button');button.className='recording';button.dataset.id=sample.id;
      const category=document.createElement('span');category.className='recording-type';category.textContent=sample.name.split(' · ')[0];
      const name=document.createElement('strong');name.textContent=sample.name.split(' · ').slice(1).join(' · ');
      const meta=document.createElement('small');meta.textContent=`${timeLabel(sample.duration)} · Recorded sample`;
      button.append(category,name,meta);button.addEventListener('click',()=>chooseSample(sample));return button;
    }));
    if(samples.length)chooseSample(samples[0]);else controls();
    const result=await api('/api/status');$('model-state').textContent=result.ready?'· Model ready':'· Model unavailable';
    if(!result.ready)status(result.error||`Download the model: ollama pull ${result.model}`);
  }catch(e){status(e.message);}
}
init();
