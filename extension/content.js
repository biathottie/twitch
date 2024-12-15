console.log("test");

function observeDOM(callback) {
    
    // Select the target node to observe (in this case, the entire document body)
    const targetNode = document.body;

    // Define the configuration for the observer
    const config = {
        childList: true,
        subtree: true,   
    };

    // Create an instance of MutationObserver
    const observer = new MutationObserver((mutationsList) => {
        // Iterate through the mutations detected
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                // Check for added nodes
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Ensure it's an element node
                        console.log('New element added:', node);
                        callback(node); // Trigger the callback with the new node
                    }
                });
            }
        }
    });

    // Start observing the target node with the specified configuration
    observer.observe(targetNode, config);

    console.log('MutationObserver initialized to track new elements.');
}

// Example callback function to handle new elements
function handleNewElement(newElement) {
    // Example: Check if the new element is a specific type
    if (newElement.matches('.target-class')) {
        console.log('A new element with .target-class appeared:', newElement);
    }
    // Add custom logic here for different element types
}

// Start observing the page
document.addEventListener('DOMContentLoaded', () => {
    console.log("event listener test")
    observeDOM(handleNewElement);
});