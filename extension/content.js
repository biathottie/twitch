setTimeout(() => {
    const parentElement = document.querySelector('[data-test-selector="chat-input-buttons-container"]');

    if (parentElement) {
        const targetElement = parentElement.querySelector('.Layout-sc-1xcs6mc-0.cwtKyw');

        if (targetElement) {
            const newDiv = document.createElement('div');
            
            targetElement.style.width = '50px';
            targetElement.style.display = 'flex';
            targetElement.style.alignItems = 'center';

            const button = document.createElement('button');
            button.style.width = '20px';
            button.style.height = '20px';
            button.style.border = 'none';
            button.style.padding = '0';
            button.style.cursor = 'pointer';
            button.style.verticalAlign = 'middle';
            button.style.marginRight = '10px';

            button.style.backgroundImage = `url(${chrome.runtime.getURL('images/settings.png')})`; // Replace with your image file name
            button.style.backgroundSize = 'cover';
            button.style.backgroundRepeat = 'no-repeat';
            button.style.backgroundPosition = 'center';

            button.addEventListener('click', () => {
                const url = "http://127.0.0.1:5000/api/process";
                const data = {
                  input1: [["air coots", "prime"]]
                };
              
                fetch(url, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify(data)
                })
                .then(response => response.json())  // Assuming the API returns JSON
                .then(data => {
                  alert("Success: " + JSON.stringify(data));  // Convert data to string to display it
                })
                .catch((error) => {
                  alert("Error: " + error);  // Convert error to string for alert
                });
            });

            newDiv.appendChild(button);
            targetElement.appendChild(newDiv);

            console.log('Image button added successfully:', newDiv);
        } else {
            console.error('Target element with class ".Layout-sc-1xcs6mc-0.cwtKyw" not found inside the parent.');
        }
    } else {
        console.error('Parent element not found.');
    }
}, 1000);