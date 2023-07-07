function render_data() {
    fetch("/gridjs/2")
    .then(response => response.json())
    .then(data => parse_response(data))
}

function parse_response(data) {
    console.log(data)
    columns = []
    for (let [key, value] of Object.entries(data[0])) {
        //columns.push({name: key, formatter: (cell) => gridjs.html(`<div style="background-color: red">${cell}</div>`)})
        columns.push({name: key, attributes: {'data-field':  key} })
    }
    console.log(columns)
    const grid = new gridjs.Grid({
        data: data,
        sort: true,
  pagination: true,
  fixedHeader: true,
  resizable: true,
    }).render(document.getElementById("wrapper"));

//    const element = document.querySelector('.gridjs-tr');
//    element.style.backgroundColor = 'red';
//    console.log(element)

}

render_data()

function change_style() {
    element = document.getElementById("gridbg")
    console.log(element)
    element.innerHTML = "[data-column-id=name] {background-color: blue !important;}"
}

change_style()