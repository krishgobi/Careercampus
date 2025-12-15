// Question Paper Generator JavaScript

// Parse requirements from text like "10 questions of 2 marks, 5 questions of 5 marks"
function parseRequirements(text) {
    const requirements = {};

    // Match patterns like "10 questions of 2 marks" or "5 of 5 marks"
    const pattern = /(\d+)\s*(?:questions?\s*)?of\s*(\d+)\s*marks?/gi;
    const matches = text.matchAll(pattern);

    for (const match of matches) {
        const count = parseInt(match[1]);
        const marks = parseInt(match[2]);
        requirements[marks] = count;
    }

    return requirements;
}

document.addEventListener('DOMContentLoaded', function () {
    // Tab switching
    const tabs = document.querySelectorAll('.qp-tab');
    const tabContents = document.querySelectorAll('.qp-tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });

    // Source type toggle
    const sourceRadios = document.querySelectorAll('input[name="source_type"]');
    const topicInput = document.getElementById('topic-input');
    const documentInput = document.getElementById('document-input');

    sourceRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'topic') {
                topicInput.classList.remove('hidden');
                documentInput.classList.add('hidden');
            } else {
                topicInput.classList.add('hidden');
                documentInput.classList.remove('hidden');
            }
        });
    });

    // File upload display
    const previousPapersInput = document.getElementById('previous-papers');
    const fileList = document.getElementById('file-list');

    previousPapersInput.addEventListener('change', (e) => {
        fileList.innerHTML = '';
        Array.from(e.target.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <i class="fas fa-file-pdf"></i>
                <span>${file.name}</span>
            `;
            fileList.appendChild(fileItem);
        });
    });

    // Important Questions Form
    const importantForm = document.getElementById('important-form');
    importantForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        const sourceType = document.querySelector('input[name="source_type"]:checked').value;

        formData.append('source_type', sourceType);
        formData.append('subject', document.getElementById('subject').value || 'General');

        if (sourceType === 'topic') {
            const topic = document.getElementById('topic').value.trim();
            if (!topic) {
                alert('Please enter a topic or content');
                return;
            }
            formData.append('topic', topic);
        } else {
            const docFile = document.getElementById('document').files[0];
            if (!docFile) {
                alert('Please upload a document');
                return;
            }
            formData.append('document', docFile);
        }

        // Get and parse requirements
        const requirementsText = document.getElementById('requirements').value.trim();
        if (!requirementsText) {
            alert('Please specify what questions you need (e.g., "10 questions of 2 marks")');
            return;
        }

        const requirements = parseRequirements(requirementsText);

        if (Object.keys(requirements).length === 0) {
            alert('Could not understand requirements. Try: "10 questions of 2 marks, 5 questions of 5 marks"');
            return;
        }

        formData.append('requirements', JSON.stringify(requirements));

        // Show loading
        document.getElementById('loading').classList.remove('hidden');

        try {
            const response = await fetch('/api/question-paper/generate/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                displayQuestions(data.questions, data.paper_id);
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate questions. Please try again.');
        } finally {
            document.getElementById('loading').classList.add('hidden');
        }
    });

    // Predict Questions Form
    const predictForm = document.getElementById('predict-form');
    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        const subject = document.getElementById('prev-subject').value.trim();

        if (!subject) {
            alert('Please enter a subject name');
            return;
        }
        formData.append('subject', subject);

        const files = previousPapersInput.files;
        if (files.length === 0) {
            alert('Please upload at least one previous paper');
            return;
        }

        Array.from(files).forEach(file => {
            formData.append('previous_papers', file);
        });

        // Get and parse requirements
        const requirementsText = document.getElementById('pred-requirements').value.trim();
        if (!requirementsText) {
            alert('Please specify what questions you need (e.g., "15 questions of 1 mark")');
            return;
        }

        const requirements = parseRequirements(requirementsText);

        if (Object.keys(requirements).length === 0) {
            alert('Could not understand requirements. Try: "15 questions of 1 mark, 10 questions of 2 marks"');
            return;
        }

        formData.append('requirements', JSON.stringify(requirements));

        // Show loading
        document.getElementById('loading').classList.remove('hidden');

        try {
            const response = await fetch('/api/question-paper/predict/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                displayQuestions(data.questions, data.paper_id);
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to predict questions. Please try again.');
        } finally {
            document.getElementById('loading').classList.add('hidden');
        }
    });

    // Display questions
    function displayQuestions(questionsByMarks, paperId) {
        const resultsSection = document.getElementById('results');
        const questionsDisplay = document.getElementById('questions-display');

        questionsDisplay.innerHTML = '';

        // Sort marks
        const sortedMarks = Object.keys(questionsByMarks).sort((a, b) => parseInt(a) - parseInt(b));

        sortedMarks.forEach(marks => {
            const questions = questionsByMarks[marks];
            if (questions.length === 0) return;

            const section = document.createElement('div');
            section.className = 'question-section';
            section.innerHTML = `
                <h3>${marks} Marks Questions</h3>
                ${questions.map((q, idx) => `
                    <div class="question-item">
                        <strong>${idx + 1}. ${q.question}</strong>
                        ${q.hint || q.reasoning ? `
                            <div class="question-hint">
                                <i class="fas fa-lightbulb"></i> ${q.hint || q.reasoning}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            `;
            questionsDisplay.appendChild(section);
        });

        // Store paper ID for export
        document.getElementById('export-pdf').dataset.paperId = paperId;
        document.getElementById('view-paper').dataset.paperId = paperId;

        // Show results
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Export PDF
    document.getElementById('export-pdf').addEventListener('click', function () {
        const paperId = this.dataset.paperId;
        if (paperId) {
            window.location.href = `/api/question-paper/${paperId}/export/`;
        }
    });

    // View Paper
    document.getElementById('view-paper').addEventListener('click', function () {
        const paperId = this.dataset.paperId;
        if (paperId) {
            window.location.href = `/question-paper/${paperId}/`;
        }
    });

    // Learn Mode
    document.getElementById('learn-btn').addEventListener('click', function () {
        const paperId = document.getElementById('export-pdf').dataset.paperId;
        if (paperId) {
            window.location.href = `/question-paper/${paperId}/learn/`;
        }
    });
});
