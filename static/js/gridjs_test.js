function render_data() {
    fetch("/gridjs/2")
    .then(response => response.json())
    .then(data => parse_response(data))
}

function parse_response(data) {
    console.log(data)
    new gridjs.Grid({
        data: data,
        sort: true,
  pagination: true,
  fixedHeader: true,
  resizable: true,
    }).render(document.getElementById("wrapper"));
}

render_data()