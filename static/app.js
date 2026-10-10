const $ = id => document.getElementById(id);
let currentVideo=null, indexing=false, searching=false;
function status(text){$('status').textContent=text;}
function timeLabel(seconds){const s=Math.floor(seconds);return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;}
function controls(){ $('load').disabled=indexing||searching; $('upload').disabled=indexing||searching; document.querySelector('label[for="upload"]').classList.toggle('busy',indexing||searching); $('search').disabled=!currentVideo||indexing||searching; }
async function api(path,options){const response=await fetch(path,options);const body=await response.json();if(!response.ok)throw Error(body.error||'Request failed');return body;}
async function loadVideo(path,options={method:'POST'}){
  if(indexing||searching)return;indexing=true;currentVideo=null;controls();$('results').replaceChildren();status('Preparing video…');
  try{const start=await api(path,options);let job;do{await new Promise(r=>setTimeout(r,700));job=await api('/api/job?id='+encodeURIComponent(start.jobId));status(job.message);}while(job.state==='queued'||job.state==='indexing');if(job.state!=='ready')throw Error(job.message);
    currentVideo=job.video;$('player').src=currentVideo.video;$('player').poster=currentVideo.poster;$('video-name').textContent=`${currentVideo.name} · ${Math.round(currentVideo.duration)} seconds`;status(`${currentVideo.frameCount} frames indexed · one frame every ${currentVideo.interval} seconds`);
  }catch(e){status(e.message);}finally{indexing=false;controls();}
}
$('load').addEventListener('click',()=>loadVideo('/api/sample'));
$('upload').addEventListener('change',()=>{const file=$('upload').files[0];if(!file)return;if(file.size>50*1024*1024){status('Choose a video under 50 MB.');return;}loadVideo('/api/upload',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},body:file});$('upload').value='';});
async function runSearch(){
  const query=$('query').value.trim();if(!currentVideo||!query||indexing||searching)return;searching=true;controls();status('Embedding your text query and comparing video frames…');
  try{const body=await api('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({videoId:currentVideo.id,query})});$('results').replaceChildren(...body.results.map(result=>{
    const row=document.createElement('article');row.className='result-row';const image=document.createElement('img');image.src=result.thumbnail;image.alt=`Frame at ${timeLabel(result.timestamp)}`;const info=document.createElement('div');info.className='result-info';const stamp=document.createElement('strong');stamp.textContent=timeLabel(result.timestamp);const name=document.createElement('p');name.textContent=currentVideo.name;const score=document.createElement('p');score.textContent=`Cosine similarity: ${result.similarity.toFixed(3)}`;const jump=document.createElement('button');jump.className='jump';jump.textContent='Jump to moment';jump.setAttribute('aria-label',`Jump to moment ${timeLabel(result.timestamp)}`);jump.addEventListener('click',()=>{$('player').currentTime=result.timestamp;$('player').play().catch(()=>{});document.querySelectorAll('.result-row').forEach(r=>r.classList.remove('selected'));row.classList.add('selected');});info.append(stamp,name,score,jump);row.append(image,info);return row;
  }));status(`${currentVideo.frameCount} frames indexed · one frame every ${currentVideo.interval} seconds · nearby results spaced 4 seconds apart`);
  }catch(e){status(e.message);}finally{searching=false;controls();}
}
$('search-form').addEventListener('submit',e=>{e.preventDefault();runSearch();});
document.querySelectorAll('[data-query]').forEach(button=>button.addEventListener('click',()=>{$('query').value=button.dataset.query;if(currentVideo)runSearch();else status('Click Load sample first, then try this search.');}));
api('/api/status').then(result=>{if(!result.ready)status(result.error||`Download the model: ollama pull ${result.model}`);}).catch(e=>status(e.message));
