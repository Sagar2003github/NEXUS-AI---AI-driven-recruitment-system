// File name display update (When user selects a PDF)
document.getElementById('resume').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : "Select Candidate PDF";
    document.getElementById('fileNameDisplay').innerText = fileName;
});

// Form submission logic
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const resumeFile = document.getElementById('resume').files[0];
    const jdText = document.getElementById('jd').value;

    // Basic Validation
    if (!resumeFile || !jdText.trim()) {
        alert("Please upload a resume and provide a job description first!");
        return;
    }

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jdText);

    // 🤖 Loading State (Visual Feedback)
    submitBtn.innerHTML = `
        <span class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            AI IS THINKING...
        </span>
    `;
    submitBtn.disabled = true;

    try {
        // AI Server ko data bhejna
        const response = await fetch('/analyze', { 
            method: 'POST', 
            body: formData 
        });
        
        const data = await response.json();

        if (data.status === "Success" && data.redirect) {
            // ✅ AGAR SUCCESS HAI: Toh seedha Report page par bhej do
            // Hum ab index.html par result nahi dikhayenge
            window.location.href = data.redirect;
        } else {
            // Agar koi backend error hai
            alert("Error: " + (data.error || "Analysis failed"));
            resetButton(submitBtn);
        }
    } catch (err) {
        console.error(err);
        alert("Server Error! Make sure your Python server is running.");
        resetButton(submitBtn);
    }
});

// Helper function to reset button state
function resetButton(btn) {
    btn.innerText = "Generate AI Analysis";
    btn.disabled = false;
}