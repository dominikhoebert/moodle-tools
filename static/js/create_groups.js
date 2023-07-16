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
    let button = deactivateButton(url)
    fetch("/create-groups/" + url)
    .then(response => response.json())
    .then(data => parse_response(data, button))
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
        return button;
    }
    return null;
}

function parse_response(response, button) {
    if(button) {
        button.disabled = false;
        button.innerHTML = button.innerHTML.replace('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ', '');
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
                element.disabled = (value === 'true');
            }
        }
        else if(key=="student-preview") {
            create_grid(value);
        }
        else if(key=="missing-students") {  // TODO: Bug when reloading page --> create_response(kind="all") missing students could be set before create_grid()
            remove_backgroundColor();
            value.forEach(function (student) {
                let cn = document.getElementById("column-name").innerHTML.trim();
                elements = document.querySelectorAll("td[data-column-id='" + cn + "']")
                if (elements) {
                    elements.forEach(function (element) {
                        if (element.innerHTML.trim() == student) {
                            element.style.backgroundColor = "#ff0000";
                        }
                    })
                }
            })
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
    set_grid_background();
}

function remove_backgroundColor() {
    elements = document.querySelectorAll("td[style]")
    if (elements) {
        elements.forEach(function (element) {
            element.style.backgroundColor = "";
        })
    }
}

function create_grid(data) {
    data = JSON.parse(data)
    const grid = new gridjs.Grid({
        data: data,
        sort: true,
  pagination: true,
  fixedHeader: true,
  resizable: true,
    }).render(document.getElementById("grid-wrapper"));
}

function set_grid_background() {
    let cn = document.getElementById("column-name").innerHTML.trim();
    let sg = document.getElementById("select-group").innerHTML.trim();
    let style_tag = document.getElementById("gridbg");
    style_tag.innerHTML = "th[data-column-id=" + cn + "] {background-color: #31d2f2 !important;} " +
        "th[data-column-id=" + sg + "] {background-color: #22bf76 !important;}";
}

update('get_all')