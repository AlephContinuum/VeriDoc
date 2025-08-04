let originalExtractedData = {};

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('document-upload');
    const isHandwritten = document.getElementById('is-handwritten').checked;
    
    if (!fileInput.files[0]) {
        alert("Please select a file first.");
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const apiEndpoint = isHandwritten ? 'http://127.0.0.1:5000/extract_handwritten_text' : 'http://127.0.0.1:5000/extract_text';

    try {
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API returned status: ${response.status}`);
        }
        
        const data = await response.json();
        originalExtractedData = data;

        // Populate the form with the extracted data
        document.getElementById('first_name').value = data.first_name || '';
        document.getElementById('last_name').value = data.last_name || '';
        document.getElementById('date_of_birth').value = data.date_of_birth || '';

    } catch (error) {
        console.error('Error during extraction:', error);
        alert(`Error: ${error.message}. Check your API server.`);
    }
});

document.getElementById('verify-button').addEventListener('click', async () => {
    const submittedData = {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        date_of_birth: document.getElementById('date_of_birth').value
    };

    try {
        const response = await fetch('http://127.0.0.1:5001/verify_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ submitted_data: submittedData, original_data: originalExtractedData })
        });
        
        if (!response.ok) {
            throw new Error(`API returned status: ${response.status}`);
        }
        
        const results = await response.json();

        const resultsDiv = document.getElementById('verification-results');
        resultsDiv.innerHTML = JSON.stringify(results, null, 2);

        for (const key in results) {
            if (results[key].match_status === 'Mismatch') {
                document.getElementById(key).classList.add('mismatch');
            } else {
                document.getElementById(key).classList.remove('mismatch');
            }
        }

    } catch (error) {
        console.error('Error during verification:', error);
        alert(`Error: ${error.message}. Check your API server.`);
    }
});