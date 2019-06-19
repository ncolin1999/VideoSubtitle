const form = document.getElementById('form');
const bar = document.getElementById('bar');
const status = document.getElementById('status');
const loader = document.getElementById('loader');
const progressbar = document.getElementById('progressbar');
const video = document.getElementById("player");
const downlaodsrt = document.getElementById('download');

file = document.getElementById('customFile');
file.addEventListener("change", function (event) {
    let label = document.getElementsByClassName("custom-file-label")[0];
    label.innerHTML = event.target.files[0].name;
    progressbar.style.width = "0%";
    progressbar.innerHTML = "";
    status.innerHTML = "";
    video.classList.add("d-none");
    downlaodsrt.classList.add("d-none");
});

form.onsubmit = function (event) {
    event.preventDefault();
    bar.classList.remove("d-none");

    let formdata = new FormData(form);


    let action = form.getAttribute('action');
    //var   header = form.getAttribute('enctype');
    let xhttp = new XMLHttpRequest();

    xhttp.open("POST", action, true);
    //xhttp.setRequestHeader("Content-type",header);
    xhttp.upload.addEventListener('progress', function (e) {
        if (e.lengthComputable) {
            //console.log("bytes loaded",e.loaded);
            //console.log("totel size",e.total);
            //console.log(Math.round((e.loaded*100)/e.total));
            var progress = Math.round((e.loaded * 100) / e.total);
            progressbar.style.width = String(progress) + "%";
            progressbar.innerHTML = String(progress) + "%";
            status.innerHTML = "Uploading...";
            if (progress === 100) {
                status.innerText = 'Completed';
                loader.classList.remove("d-none");
            }
        }
    });
    xhttp.onload = function (event) {
        if (this.status === 200) {
            let json = JSON.parse(this.responseText);
            document.getElementsByTagName("source")[0].setAttribute("src", json.video);
            bar.classList.add("d-none");
            loader.classList.add('d-none');

            video.classList.remove("d-none");

            downlaodsrt.setAttribute('href', json.download);
            downlaodsrt.classList.remove('d-none');
            video.addEventListener("loadedmetadata", function () {
                let track = document.createElement("track");
                track.kind = "subtitles";
                track.label = "English";
                track.srclang = "en";
                track.src = json.subtitle;
                track.addEventListener("load", function () {
                    //by default subtitle is hidden
                    this.mode = "showing"; //both  statements have same meaning but i have written both of them just for browser compatibility
                    //video.textTracks[0].mode = "showing";
                    video.textTracks[video.textTracks.length - 1].mode = "showing";
                });
                for (let i = 0; i < video.textTracks.length; i++) {
                    video.textTracks[i].mode = "hidden";
                }
                this.appendChild(track);


            });
            video.load();
        }
    };

    xhttp.send(formdata);


};
