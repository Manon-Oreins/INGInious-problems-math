var homepath = "";

function load_input_math(submissionid, key, input) {
    var field = $("form#task input[name='" + key + "']");
    $("#math-fields-" + key).html("");
    if(key in input) {
        $.each(input[key], function(index) {
            math_add_answer(key, this);
        });
    } else {
        math_add_answer(key, '');
    }
}

function studio_init_template_math(well, pid, problem)
{
    var tolerance = "";
    var success_message = "";
    var error_message = "";
    var hints = "";
    var logical_comparison = 'on';
    var use_log = problem["use_log"];
    var use_trigo = problem["use_trigo"];
    var use_complex = problem["use_complex"];
    if("logical_comparison" in problem)
        logical_comparison = problem["logical_comparison"];
    if("tolerance" in problem)
        tolerance = problem["tolerance"];
    if("success_message" in problem)
        success_message = problem["success_message"];
    if("error_message" in problem)
        error_message = problem["error_message"];
    if("hints" in problem)
        hints = problem["hints"];
    if("answer" in problem) // retrocompat
        problem["answers"] = [problem["answer"]];

    $("#tolerance-" + pid).val(tolerance);
    $("#logical_comparison-" + pid).prop("checked", logical_comparison);
    $("#use_log-" + pid).prop("checked", use_log);
    $("#use_trigo-" + pid).prop("checked", use_trigo);
    $("#use_complex-" + pid).prop("checked", use_complex);
    registerCodeEditor($('#success_message-' + pid)[0], 'rst', 1).setValue(success_message);
    registerCodeEditor($('#error_message-' + pid)[0], 'rst', 1).setValue(error_message);
    registerCodeEditor($('#hints-' + pid)[0], 'rst', 1).setValue(hints);

    jQuery.each(problem["choices"], function(index, elem) {
        math_create_choice(pid, elem);
    });

    if (problem.type == "math")
        jQuery.each(problem["answers"], function(index, elem) {
            math_create_answer(pid, elem);
        });

}

function load_feedback_math(key, content) {
    var alert_type = "danger";
    if(content[0] === "timeout" || content[0] === "overflow")
        alert_type = "warning";
    if(content[0] === "success")
        alert_type = "success";
    $("#task_alert_" + key).html(getAlertCode("", content[1], alert_type, true));
}

function math_create_choice(pid, choice_data) {
    var well = $(studio_get_problem(pid));

    var index = 0;
    while($('#choice-' + index + '-' + pid).length != 0)
        index++;

    var row = $("#subproblem_math_choice").html();
    var new_row_content = row.replace(/PID/g, pid).replace(/CHOICE/g, index);
    var new_row = $("<div></div>").attr('id', 'choice-' + index + '-' + pid).html(new_row_content);
    $("#choices-" + pid, well).append(new_row);

    var editor_answer = new MathEditor("problem[" + pid + "][choices][" + index + "][answer]", $("#collapse_" + pid));
    var editor_feedback = registerCodeEditor($(".subproblem_math_feedback", new_row)[0], 'rst', 1);

    if("answer" in choice_data)
        editor_answer.setLatex(choice_data["answer"]);
    if("feedback" in choice_data)
        editor_feedback.setValue(choice_data["feedback"]);
}

function math_delete_choice(pid, choice)
{
    $('#choice-' + choice + '-' + pid).detach();
}

function math_create_answer(pid, choice_data, type="math") {
    var well = $(studio_get_problem(pid));

    var index = 0;
    while($('#answer-' + index + '-' + pid).length != 0)
        index++;

    var row = $("#subproblem_"+type+"_answer").html();
    var new_row_content = row.replace(/PID/g, pid).replace(/CHOICE/g, index);
    var new_row = $("<div></div>").attr('id', 'answer-' + index + '-' + pid).html(new_row_content);
    $("#answers-" + pid, well).append(new_row);

    var editor_answer = new MathEditor("problem[" + pid + "][answers][" + index + "]", $("#collapse_" + pid));
    editor_answer.setLatex(choice_data);
}

function math_delete_answer(pid, choice)
{
    $('#answer-' + choice + '-' + pid).detach();
}

function math_add_answer(pid, data) {
    var index = 0;
    while($('#math-field-' + index + '-' + pid).length != 0)
        index++;

    var div = $("<div></div>");
    var del_btn = $("<button></button>").attr("type", "button")
        .attr("class", "close")
        .attr("onclick", "$(this).parent().remove();");
    del_btn.html('<span>&times;</span>');
    var math_field = $("<div></div>").attr('id', 'math-field-' + index + '-' + pid);
    var math_input = $("<input></input>").attr('id', 'math-input-' + index + '-' + pid)
        .attr("name", pid)
        .attr("type", "hidden");
    div.append(del_btn).append(math_field).append(math_input);
    $("#math-fields-" + pid).append(div);

    var editor_answer = new MathEditor(index + "-" + pid, $("#collapse_" + pid));
    editor_answer.setLatex(data);
}

$( document ).ready(function() {
    $(".math_modal").on('show.bs.modal', function (e) {
        var button = $(e.relatedTarget); // Button that triggered the modal
        var problemid = button.data('problemid');

        $.ajax({
            url: homepath + '/plugins/math/hint',
            type: 'post',
            data: {courseid: courseid, taskid: taskid, problemid: problemid},
            success: function(response){
                // Add response in Modal body
                $('.math_modal_' + problemid + ' .modal-body').html(response);
                MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
            }
        });
    })
});

/////////////////////////////////////////////////////////////////////////////////
// MATH MATRIX //////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

function load_input_math_matrix(submissionid, key, input) {
    load_input_math(submissionid, key, input)
}

function load_feedback_math_matrix(key, content) {
    load_feedback_math(key,content)
}

function studio_init_template_math_matrix(well, pid, problem)
{
    studio_init_template_math(well, pid, problem)
    jQuery.each(problem["answers"], function(index, elem) {
        math_matrix_create_answer(pid, elem);
    });
}

function math_matrix_create_answer(pid, choice_data) {
    return math_create_answer(pid,choice_data, "math_matrix")
}

/////////////////////////////////////////////////////////////////////////////////
// MATH INTERVAL ////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

function load_input_math_interval(submissionid, key, input) {
    load_input_math(submissionid, key, input)
}

function load_feedback_math_interval(key, content) {
    load_feedback_math(key,content)
}

function studio_init_template_math_interval(well, pid, problem)
{
    studio_init_template_math(well, pid, problem)
    jQuery.each(problem["answers"], function(index, elem) {
        math_interval_create_answer(pid, elem);
    });
}

function math_interval_create_answer(pid, choice_data) {
    return math_create_answer(pid, choice_data, "math_interval");
}

/////////////////////////////////////////////////////////////////////////////////
// MATH SET /////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

function load_input_math_set(submissionid, key, input) {
    load_input_math(submissionid, key, input)
}

function load_feedback_math_set(key, content) {
    load_feedback_math(key,content)
}

function studio_init_template_math_set(well, pid, problem)
{
    studio_init_template_math(well, pid, problem)
    var set_type = "";
    if("set_type" in problem)
        set_type = problem["set_type"];

    $("#set_"+ set_type + "-"+pid).attr('checked', true)

    jQuery.each(problem["answers"], function(index, elem) {
        math_set_create_answer(pid, elem);
    });
}

function math_set_create_answer(pid, choice_data) {
    return math_create_answer(pid, choice_data, "math_set")
}

function math_set_modify_format(pid, value){
    $("#format_edit-" + pid).text(value)
}
