function load_input_math(submissionid, key, input) {
    var field = $("form#task input[name='" + key + "']");
    if(key in input)
         window["matheditor_" + key].setLatex(input[key]);
    else
         window["matheditor_" + key].setLatex("");
}

function studio_init_template_math(well, pid, problem)
{
    window["matheditor_" + pid] = new MathEditor("problem[" + pid + "][answer]");

    if("answer" in problem)
        window["matheditor_" + pid].setLatex(problem["answer"]);

    var success_message = "";
    var error_message = "";
    if("success_message" in problem)
        success_message = problem["success_message"];
    if("error_message" in problem)
        error_message = problem["error_message"];

    registerCodeEditor($('#success_message-' + pid)[0], 'rst', 1).setValue(success_message);
    registerCodeEditor($('#error_message-' + pid)[0], 'rst', 1).setValue(error_message);
}

function load_feedback_math(key, content) {
    var alert_type = "danger";
    if(content[0] === "timeout" || content[0] === "overflow")
        alert_type = "warning";
    if(content[0] === "success")
        alert_type = "success";
    $("#task_alert_" + key).html(getAlertCode("", content[1], alert_type, true));
}