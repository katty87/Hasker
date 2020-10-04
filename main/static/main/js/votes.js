$(function() {
function onClickUpVote() {

    vote(1)
}

function onClickDownVote() {
    vote(-1);
}

function vote(vote_value) {
    $.ajax({
        url: '{% url 'vote_question' %}',
        type: 'POST',
        data:{question_id: {{ question.id }}, value: vote_value, user_id: {{ user.id }}, csrfmiddlewaretoken: '{{ csrf_token }}'},
        success: function(response) {
            current_vote = response.current_vote
            if (current_vote == -1) {
                document.getElementById("down-vote").style.color = "orange";
                document.getElementById("up-vote").style.color = "#D3D3D3";
            } else if (current_vote == 1) {
                document.getElementById("up-vote").style.color = "orange";
                document.getElementById("down-vote").style.color = "#D3D3D3";
            } else if (current_vote == 0) {
                if (vote_value == 1) {
                    document.getElementById("up-vote").style.color = "#D3D3D3";
                } else {
                    document.getElementById("down-vote").style.color = "#D3D3D3";
                }
            }

            document.getElementById("question-vote").innerHTML = response.total_votes
        },
    });
}

function onClickUpVoteAnswer(id) {
    vote_ans(id, 1)
}

function onClickDownVoteAnswer(id) {
    vote_ans(id, -1)
}

function vote_ans(id, vote_value) {
    $.ajax({
        url: '{% url 'vote_answer' %}',
        type: 'POST',
        data:{answer_id: id, value: vote_value, user_id: {{ user.id }}, csrfmiddlewaretoken: '{{ csrf_token }}'},
        success: function(response) {
            current_vote = response.current_vote
            if (current_vote == -1) {
                document.getElementById("down-vote-answer-" + id).style.color = "orange";
                document.getElementById("up-vote-answer-" + id).style.color = "#D3D3D3";
            } else if (current_vote == 1) {
                document.getElementById("up-vote-answer-" + id).style.color = "orange";
                document.getElementById("down-vote-answer-" + id).style.color = "#D3D3D3";
            } else if (current_vote == 0) {
                if (vote_value == 1) {
                    document.getElementById("up-vote-answer-" + id).style.color = "#D3D3D3";
                } else {
                    document.getElementById("down-vote-answer-" + id).style.color = "#D3D3D3";
                }
            }

            document.getElementById("answer-vote-" + id).innerHTML = response.total_votes
        },
    });

}

function onClickAnswerRight(id, user_id, author_id) {
   if (user_id != author_id) {
    return
   }

   $.ajax({
        url: '{% url 'mark_answer_right' %}',
        type: 'POST',
        data:{answer_id: id, user_id: {{ user.id }}, csrfmiddlewaretoken: '{{ csrf_token }}'},
        success: function(response) {
            if (response == 1) {
                document.getElementById("answer-right-" + id).innerHTML = '&#9733;';
            } else if (response == 0) {
                document.getElementById("answer-right-" + id).innerHTML = '&#9734;';
            }
        },
    });
}
});