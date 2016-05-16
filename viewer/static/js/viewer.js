var codemirror = null;
var state = null;
var stateIdx = -1;


function initSourceViewer() {
    codemirror = CodeMirror.fromTextArea(document.getElementById('source-viewer'), {
        mode: "python",
        theme: "default",
        lineNumbers: true,
        readOnly: 'nocursor',
        styleActiveLine: true
    });
}

function initStateViewer() {
    stateIdx = 0;
}

function renderState() {
    var currentState = state[stateIdx].state;
    // Off by 1 because of how Python counts lines.
    var lineno = state[stateIdx].lineno - 1;
    var rendered = JSON.stringify(currentState)

    $('#state').text(rendered);
    highlightLine(lineno);
}

function highlightLine(lineno) {
    codemirror.setCursor({line: lineno});
}

function nextStep() {
    var aux = stateIdx + 1;

    if (aux >= state.length) {
        return;
    }

    stateIdx = aux;
    renderState();
}

function prevStep() {
    var aux = stateIdx - 1;

    if (aux < 0) {
        return;
    }

    stateIdx = aux;
    renderState();
}

function keyHandler(event) {
    if (event.code == "ArrowUp") {
        prevStep();
        return;
    }
    if (event.code == "ArrowDown") {
        nextStep();
        return
    }
}


document.onkeydown = keyHandler;

$.getJSON("source.json", function(data) {
    $('#source-viewer').text(data.source);

    $.getJSON("state.json", function(data) {
        state = data.data;

        initStateViewer();
        initSourceViewer();

        renderState();
    });
});
