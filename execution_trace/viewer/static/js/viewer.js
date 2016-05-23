var codemirror = null;
var runStates = null;
var stateIdx = -1;
var runIdx = -1;
var varStateTemplate = Handlebars.compile($("#var-state-template").html());


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

function getCurrentRunStates() {
    return runStates[runIdx].data;
}

function renderState() {
    var currentRunStates = getCurrentRunStates();

    // stateIdx might be out of bounds (changing between executions).
    if (stateIdx >= currentRunStates.length) {
        stateIdx = currentRunStates.length - 1;
    }

    var currentState = currentRunStates[stateIdx].state;
    // Off by 1 because of how Python counts lines.
    var lineno = currentRunStates[stateIdx].lineno - 1;

    $('.state-viewer').empty();

    var vars = Object.keys(currentState);
    vars.sort();

    for (i = 0; i < vars.length; i++) {
        var name = formatVarName(vars[i]);
        var value = formatStateValue(currentState[vars[i]])
        var html = varStateTemplate({
                               name: name,
                               value: value
                           });
        $('.state-viewer').append(html);
    }

    highlightLine(lineno);
    setSlider(stateIdx);
}

function highlightLine(lineno) {
    codemirror.setCursor({line: lineno});
}

function nextStep() {
    var aux = stateIdx + 1;

    if (aux >= getCurrentRunStates().length) {
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

function formatStateValue(value) {
    // remove leading and ending `"`, if any.
    if (value[0] == '"' && value[value.length - 1]) {
        return value.slice(1, value.length - 1);
    }
    return value;
}

function formatVarName(name) {
    if (name == "_retval_hidden_123") {
        return "return value";
    }
    return name;
}

function setSlider(pos) {
    $('#slider').val(pos);
}

function initSlider(end) {
    $('#slider').attr('max', end);
    setSlider(0);
}

function initNumber(end) {
    $('#number').attr('min', 0);
    $('#number').attr('max', end);
}

function main() {
    document.onkeydown = keyHandler;

    // Tie slider to rest of world.
    $('#slider').on('input', function (e) {
        // It's a string.
        var value = $('#slider').val() | 0;
        stateIdx = value;
        renderState();
    });

    // Disable regular slider key inputs.
    $('#slider').on('keydown', function(e) {
        e.preventDefault();
    });

    // Tie number to rest of world.
    $('#number').on('input', function (e) {
        // It's a string.
        var value = $('#number').val() | 0;
        runIdx = value;
        // This execution might have different number of steps.
        initSlider(getCurrentRunStates().length - 1);
        renderState();
    });

    // Disable regular number key inputs.
    $('#number').on('keydown', function(e) {
        e.preventDefault();
    });

    $.getJSON("source.json", function(data) {
        $('#source-viewer').text(data.source);

        $.getJSON("state.json", function(data) {
            runStates = data.data;
            runIdx = 0;

            initStateViewer();
            initSourceViewer();

            initSlider(getCurrentRunStates().length - 1);
            initNumber(runStates.length - 1);

            renderState();
        });
    });
}

// Go!
main();
