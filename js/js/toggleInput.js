const canvasButton = document.getElementById("canvasButton");
const imageButton = document.getElementById("imageButton");
const examplesButton = document.getElementById("examplesButton");


const canvasDiv = document.getElementById("canvasDiv");
const imageDiv = document.getElementById("imageDiv");
const examplesDiv = document.getElementById("examplesDiv");

canvasButton.disabled=true;
imageButton.disabled=false;
examplesButton.disabled=false;



function buttonClicked(button){

    buttons = [canvasButton, imageButton, examplesButton];
    divs =  [canvasDiv, imageDiv, examplesDiv];

    for (let i = 0; i < buttons.length; i++) {

        if (buttons[i] === button){
            divs[i].classList.add("active");
            buttons[i].disabled=true;
            buttons[i].classList.add("pressed")
        }
        else {
            divs[i].classList.remove("active");
            buttons[i].disabled=false;
            buttons[i].classList.remove("pressed");
        }

    }


    if (button == examplesButton){
        solveButton.classList.add("solveButtonInExamples")
        solveButton.classList.remove("whole-button")
        clearButton.style.display = "none";
        nextButton.style.display = "block";
        prevButton.style.display = "block";
        
    }
    else{
        solveButton.classList.remove("solveButtonInExamples")
        solveButton.classList.add("whole-button")
        clearButton.style.display = "block";
        nextButton.style.display = "none";
        prevButton.style.display = "none";
    }

}

canvasButton.addEventListener("click", () => {
    buttonClicked(canvasButton);
});

imageButton.addEventListener("click", () => {
    buttonClicked(imageButton);
}); 


examplesButton.addEventListener("click", () => {
    buttonClicked(examplesButton);
}); 