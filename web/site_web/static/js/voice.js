var audioChunks;
startRecord.onclick = e => {
    startRecord.disabled = true;
    stopRecord.disabled=false;
    // This will prompt for permission if not allowed earlier
    navigator.mediaDevices.getUserMedia({audio:true})
        .then(stream => {
            audioChunks = [];
            rec = new MediaRecorder(stream);
            rec.ondataavailable = e => {
                audioChunks.push(e.data);
                if (rec.state == "inactive"){
                    let blob = new Blob(audioChunks,{type:'audio/x-mpeg-3'});
                    recordedAudio.src = URL.createObjectURL(blob);
                    recordedAudio.controls=true;
                    recordedAudio.autoplay=true;
                    audioDownload.href = recordedAudio.src;
                    audioDownload.download = 'mp3';
                    audioDownload.innerHTML = 'download';
                }
            }
            rec.start();
        })
        .catch(e=>console.log(e));
}
stopRecord.onclick = e => {
    startRecord.disabled = false;
    stopRecord.disabled=true;
    rec.stop();
}