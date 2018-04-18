function load_input_math(submissionid, key, input) {
    var field = $("form#task input[name='" + key + "']");
    if(key in input)
         window["matheditor_" + key].setLatex(input[key]);
    else
         window["matheditor_" + key].setLatex("");
}

function studio_init_template_math(well, pid, problem)
{
    if("answer" in problem)
        $('#answer-' + pid, well).val(problem["answer"]);
}