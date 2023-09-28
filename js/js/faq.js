const faqItems = document.querySelectorAll('.faq-item');


faqItems.forEach((item) => {
    const question = item.querySelector('.question');
    const answer = item.querySelector('.answer');

    answer.style.maxHeight = '0px';
    answer.style.padding="0px";

    question.addEventListener('click', () => {
        if (answer.style.maxHeight === '0px') {
            answer.style.maxHeight = answer.scrollHeight + 'px';
            answer.style.padding="20px";
        } else {
            answer.style.maxHeight = '0';
            answer.style.padding="0px";
        }
    });
});


function go_to_examples_section(){
    examplesButton.click();
    scroll_to_input_div();
}

function go_to_faq_section(){
    window.scrollTo({top: document.getElementById("faqContainer").offsetTop + 3000, behavior: "smooth"})
}

function go_to_troubleshooting_question(){
    answer = document.querySelectorAll('.answer')[2];
    question =  document.querySelectorAll('.question')[2];

    if(answer.style.maxHeight === '0px'){
        question.click();
    }
    
    go_to_faq_section()

}

