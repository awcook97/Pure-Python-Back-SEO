// Add your JavaScript code here to handle button clicks and send requests to the API endpoints
document.addEventListener('DOMContentLoaded', function() {
    // Handle button clicks and send requests to the API endpoints
    // Example:
    document.getElementById('generateReport').addEventListener('click', function() {
        // Get the selected client and report details
        var client = document.getElementById('clientSelector').value;
        var reportTitle = document.getElementById('reportTitle').value;
        var reportSubtitle = document.getElementById('reportSubtitle').value;
        // ...

        // Send a POST request to the /generate_report endpoint
        fetch('/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client: client,
                reportTitle: reportTitle,
                reportSubtitle: reportSubtitle
                // ...
            })
        })
        .then(function(response) {
            return response;
        });
    });

    // Handle other button clicks and send requests similarly
});