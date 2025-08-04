document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('document-upload');
    
    if (!fileInput.files[0]) {
        alert("Please select a file first.");
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        // Call the new ID OCR API
        const response = await fetch('http://127.0.0.1:5002/extract_id_data', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API returned status: ${response.status}`);
        }
        
        const data = await response.json();

        // Populate the form with the extracted data
        document.getElementById('full_name').value = data.full_name || '';
        document.getElementById('document_type').value = data.document_type || '';
        document.getElementById('document_number').value = data.document_number || '';
        document.getElementById('date_of_birth').value = data.date_of_birth || '';
        document.getElementById('gender').value = data.gender || '';

    } catch (error) {
        console.error('Error during extraction:', error);
        alert(`Error: ${error.message}. Check your API server.`);
    }
});