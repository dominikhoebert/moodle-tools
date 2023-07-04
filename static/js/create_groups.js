async function uploadFile() {
    let uploadButton = document.getElementById("upload-button");
    uploadButton.disabled = true;
    uploadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Upload';
    let formData = new FormData();
    formData.append("file", fileupload.files[0]);
    await fetch('/create-groups/file-upload', {
        method: "POST",
        body: formData
    }).then(response => response.json())
    .then(data => parse_response(data, uploadButton));
}

function toast(message) {
    document.getElementById("flash-toast").innerHTML = message
    flash_toast()
}

function update(url) {
    deactivateButton(url)
    fetch("/create-groups/" + url)
    .then(response => response.json())
    .then(data => parse_response(data))
}

function deactivateButton(name) {
    let button = null
    switch (name) {
        case "enroll":
            button = document.getElementById("enroll-button")
            break;
        case "create":
            button = document.getElementById("create-button")
            break;
        case "add":
            button = document.getElementById("add-button")
            break;
    }
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + button.innerHTML;
    }
}

function parse_response(response, button) {
    if(button) {
        button.disabled = false;
        button.innerHTML = 'Upload';
    }
    for (let [key, value] of Object.entries(response)) {
        if(key=="flash") {
            toast(value)
        }
        else if(key=="Error") {
            console.log(key, value)
        }
        else if(key.endsWith('-button')) {
            element = document.getElementById(key)
            if (element) {
                element.disabled = value;
            }
        }
        else {
            element = document.getElementById(key)
            if (element) {
                element.innerHTML = value
            }
        }
    }
    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
}

update('get_all')