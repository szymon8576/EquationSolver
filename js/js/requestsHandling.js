
function show_instructions(instructionsData){
    const container = document.getElementById("imageContainer");
    container.innerHTML="";

    instructionsData.forEach((item, index) => {
    

    const descriptionElement = document.createElement("p");
    descriptionElement.textContent = item[0];

    const imgElement = document.createElement("img");
    imgElement.src = 'data:image/png;base64,' + item[1];


    container.appendChild(descriptionElement);
    container.appendChild(imgElement);

    if (index != instructionsData.length -1){
    const spacer = document.createElement("hr");
    container.appendChild(spacer);
    }
});
}



function loadLocalImage(event) {
    const imageElement = document.getElementById("imagePlaceholder");
    const fileInput = event.target;

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {

            imageElement.src = e.target.result;
        };

        reader.readAsDataURL(fileInput.files[0]);
    }
}

let numOfSolutions = document.getElementById('numOfSolutions')
let solutionSteps = document.getElementById('solutionSteps')
let solutionSimple = document.getElementById('solutionSimple')
let solutionImageDiv = document.getElementById('solutionImageDiv')
let errorDiv = document.getElementById('errorDiv')
let errorSubDivText = document.getElementById("errorDivSubText")

function scroll_to_input_div(){
    let inputDivWrapperY = document.getElementById("inputDivWrapper").offsetTop;

    if ( window.scrollY > inputDivWrapperY) {
        window.scrollTo({ top: 0, behavior: "smooth"});
    }
}

function clear_result(){
    numOfSolutions.innerText = "";
    document.getElementById("imageContainer").innerHTML="";
    document.getElementById("imagePlaceholder").src="";
    document.getElementById("solutionImagePlaceholder").src="";
    document.getElementById("solutionDiv").classList.remove("active");
    dropZone.style.display = "block";

}

 async function send_image(imageData){
    try {

        const response = await fetch("http://localhost:5000/solve", {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: imageData }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        let solutionDiv = document.getElementById("solutionDiv");
        solutionDiv.classList.add("active");
        solutionDiv.scrollIntoView({ behavior: "smooth" });

        if (data.processing_status === "ERROR") {

                solutionSteps.classList.add("hidden");
                solutionSimple.classList.add("hidden");
                errorSubDivText.innerHTML = `Please try again or have a look at <a href='javascript:go_to_troubleshooting_question()'> troubleshooting</a> instructions.</p>`
                
                errorDivText.textContent = "Well.. that's embarrassing. We couldn't recognize your equation.";
                errorDiv.classList.add("active");

            } else {

                
                errorDiv.classList.remove("active");
                solutionSimple.classList.remove("hidden");
                solutionSteps.classList.remove("hidden");
                solutionImageDiv.classList.remove("hidden");

                document.getElementById("solutionImagePlaceholder").src = 'data:image/png;base64,' + data.solution.image;
                
                equation_status = data.equation_status;

                if (equation_status === "MARKED"){
                                    
                    numOfSolutions.innerText = "This equation has one solution.";
                    
                    show_instructions(data.instructions);
                }
                else if (equation_status === "INDETERMINATE"){

                    solutionSteps.classList.add("hidden");
                    numOfSolutions.innerText = "This is indeterminate equation. It has infinite number of solutions.";
                }
                else{
 
                    solutionSteps.classList.add("hidden");
                    numOfSolutions.innerText = "This equation is a contradiction. It has no solutions.";
                }

                
            }

    } catch (error) {

        let solutionDiv = document.getElementById("solutionDiv");
        solutionDiv.classList.add("active");
        solutionDiv.scrollIntoView({ behavior: "smooth" });
        
        solutionSteps.classList.add("hidden");
        solutionSimple.classList.add("hidden");
        
        errorDivText.textContent = `Couldn't connect to the server.`;
        errorDiv.classList.add("active");

        errorSubDivText.innerText = `${error.message} - that's all we know.`
        
        console.error("Error:", error);
    }

    


 }

 function getVisibleDiv() {
    if (canvasDiv.classList.contains("active")) {
        return "canvas";
    } else if (imageDiv.classList.contains("active")) {
        return "image";
    } 
    else if (examplesDiv.classList.contains("active")) {
        return "examples";
    }
    else {
        return null;
    }
}

function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    return canvas.toDataURL("image/png");
  }
  

async function solveEquation() {


    let visibleDiv = getVisibleDiv();


    if (visibleDiv === "canvas"){
        const canvasData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        ctx.putImageData(canvasData, 0, 0);
        const imageData = canvas.toDataURL("image/png");
        send_image(imageData);
    }
    else if (visibleDiv === "image" && cropper){  
        const croppedCanvas = cropper.getCroppedCanvas();
        
        if (croppedCanvas){
            const croppedDataURL = croppedCanvas.toDataURL("image/png");
            send_image(croppedDataURL);
        }

    }
    else if (visibleDiv == "examples"){

        let currSlideImg = document.getElementsByClassName("slide")[currentSlide].querySelector("img");
        let base64 = getBase64Image(currSlideImg);

        send_image(base64);
    }

}
    

   
    


