// Checking input
function validateInput(questionNumber) {
    const question = document.getElementById(`question${questionNumber}`);
    const input = question.querySelector('input');
    const textarea = question.querySelector('textarea');
    
    // Check if input or textarea element exists
    if (input || textarea) {
        if (input) {
            if (!input.checkValidity()) {
                alert('Please provide a valid answer');
                return false;
            }
            if (input.type === 'text') {
                if (input.value.trim() === '') {
                    alert('Please provide a valid answer');
                    return false;
                }
            }
        }

        if (textarea) {
            // Check if textarea is not empty or only whitespace
            if (textarea.value.trim() === '') {
                alert('Please provide a valid answer');
                return false;
            }
        }
    }

    return true;
}

// Next question
function nextQuestion(currentQuestion) {
    if (!validateInput(currentQuestion)) {
        return;
    }
    const current = document.getElementById(`question${currentQuestion}`);
    const next = document.getElementById(`question${currentQuestion + 1}`);
    if (next) {
        current.classList.remove('active');
        next.classList.add('active');
    }
}

// Handle form submission
function handleSubmit(event) {
    event.preventDefault();
    const totalQuestions = 4; // Adjust this based on the number of questions in your form
    for (let i = 1; i <= totalQuestions; i++) {
        if (!validateInput(i)) {
            return false;
        }
    }
    document.forms['surveyForm'].submit();
}

// Attach submit event listener to form
document.forms['surveyForm'].addEventListener('submit', handleSubmit);

// Press enter to go to next question
document.querySelectorAll('input').forEach(function(inputElement) {
    inputElement.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent default form submission behavior

            // Find the current question number
            const currentQuestion = parseInt(inputElement.closest('.question').id.replace('question', ''));

            // Move to the next question
            nextQuestion(currentQuestion);
        }
    });
});

// Previous question
function prevQuestion(currentQuestion) {
    const current = document.getElementById(`question${currentQuestion}`);
    const prev = document.getElementById(`question${currentQuestion - 1}`);
    if (prev) {
        current.classList.remove('active');
        prev.classList.add('active');
    }
}

// Press enter to submit
document.getElementById('q4').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit(event);
    }
});

function validateAndSubmitEvaluationForm(event) {
    event.preventDefault();
    
    const form = document.forms['evaluationForm'];
    const radioButtons = form.elements['evaluation'];
    let isChecked = false;

    for (let i = 0; i < radioButtons.length; i++) {
        if (radioButtons[i].checked) {
            isChecked = true;
            break;
        }
    }

    if (!isChecked) {
        alert('Please select a rating before submitting.');
        return false;
    }

    form.submit();
}

document.forms['evaluationForm'].addEventListener('submit', validateAndSubmitEvaluationForm);
