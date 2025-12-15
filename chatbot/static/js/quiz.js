// quiz.js - Quiz and Learning Track functionality for Kattral AI

let currentQuiz = null;
let currentQuestionIndex = 0;
let quizSource = null;
let quizData = [];
let userAnswers = [];
let quizUploadInstance = null;

// Initialize quiz drag & drop on page load
document.addEventListener('DOMContentLoaded', function () {
    const quizZone = document.getElementById('quizDropZone');
    if (quizZone) {
        quizUploadInstance = new DragDropUpload('quizDropZone', 'quizFileInput', {
            multiple: true,
            maxFiles: 10,
            acceptedTypes: ['.pdf', '.docx', '.pptx'],
            maxSize: 50 * 1024 * 1024,
            onFilesChanged: function (files) {
                // Enable generate button when files are selected
                document.getElementById('generateQuizFromDocs').disabled = files.length === 0;

                // Auto-upload files
                if (files.length > 0) {
                    uploadQuizFiles(files);
                }
            }
        });
    }
});

// Upload quiz files
async function uploadQuizFiles(files) {
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            uploadedDocumentIds = data.documents.map(doc => doc.id);
            document.getElementById('generateQuizFromDocs').disabled = false;
        }
    } catch (error) {
        console.error('Error uploading:', error);
        alert('Upload failed');
    }
}


// ===== Modal Control =====
function openQuizModal() {
    document.getElementById('quizModal').classList.add('active');
    showQuizStep('quizSourceSelect');
}

function closeQuizModal() {
    document.getElementById('quizModal').classList.remove('active');
    resetQuiz();
}

function showQuizStep(stepId) {
    document.querySelectorAll('.quiz-step').forEach(step => step.classList.add('hidden'));
    document.getElementById(stepId).classList.remove('hidden');
}

function resetQuiz() {
    currentQuiz = null;
    currentQuestionIndex = 0;
    quizData = [];
    userAnswers = [];
    showQuizStep('quizSourceSelect');
}

// ===== Quiz Flow =====
let uploadedDocumentIds = [];

function selectQuizSource(source) {
    quizSource = source;

    if (source === 'document') {
        // Show document selection options (existing vs new)
        showQuizStep('quizDocumentSelect');
    } else {
        // Show prompt options
        showQuizStep('quizPromptOptions');
    }
}

async function showExistingDocuments() {
    showQuizStep('quizExistingDocs');

    // Fetch existing documents
    try {
        const response = await fetch('/api/documents/');
        const data = await response.json();

        const container = document.getElementById('existingDocsContainer');

        if (data.documents.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No documents uploaded yet</p>';
        } else {
            container.innerHTML = data.documents.map(doc => `
                <div class="doc-item-enhanced">
                    <div class="doc-icon">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="doc-info-enhanced">
                        <h4>${doc.title}</h4>
                        <small><i class="fas fa-calendar"></i> ${new Date(doc.uploaded_at).toLocaleDateString()}</small>
                    </div>
                    <div class="doc-actions">
                        <button class="btn-quiz-select" onclick="selectDocumentForQuiz(${doc.id}, '${doc.title.replace(/'/g, "\\'")}')">
                            <i class="fas fa-play"></i> Generate Quiz
                        </button>
                        <button class="btn-delete-doc" onclick="event.stopPropagation(); deleteDocument(${doc.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error fetching documents:', error);
        alert('Failed to load documents');
    }
}

function selectDocumentForQuiz(documentId, title) {
    // Ask for number of questions
    const numQuestions = prompt('How many questions do you want in the quiz?', '10');

    if (!numQuestions || isNaN(numQuestions) || numQuestions < 1) {
        alert('Please enter a valid number of questions');
        return;
    }

    showQuizStep('quizLoading');
    document.querySelector('#quizLoading p').textContent = `Generating ${numQuestions} questions from document...`;

    fetch('/api/quiz/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            source_type: 'document',
            topic: title,
            num_questions: parseInt(numQuestions),
            document_id: documentId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentQuiz = data.quiz;
                quizData = data.questions;
                currentQuestionIndex = 0;
                userAnswers = new Array(quizData.length).fill(null);
                showQuestion();
            } else {
                alert('Error generating quiz: ' + data.message);
                closeQuizModal();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate quiz');
            closeQuizModal();
        });
}

function showNewDocumentUpload() {
    showQuizStep('quizNewDocUpload');
    uploadedDocumentIds = [];
    document.getElementById('quizUploadedFiles').innerHTML = '';
    document.getElementById('generateQuizFromDocs').disabled = true;
}

async function handleQuizFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const uploadList = document.getElementById('quizUploadedFiles');
    uploadList.innerHTML = '<p>Uploading files...</p>';

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            uploadedDocumentIds = data.documents.map(doc => doc.id);

            uploadList.innerHTML = data.documents.map(doc => `
                <div class="uploaded-file-item">
                    <i class="fas fa-check-circle" style="color: var(--success);"></i>
                    <span>${doc.title}</span>
                </div>
            `).join('');

            document.getElementById('generateQuizFromDocs').disabled = false;
        } else {
            uploadList.innerHTML = '<p style="color: var(--danger);">Upload failed</p>';
        }
    } catch (error) {
        console.error('Error uploading:', error);
        uploadList.innerHTML = '<p style="color: var(--danger);">Upload failed</p>';
    }
}

function generateQuizFromUploadedDocs() {
    if (uploadedDocumentIds.length === 0) return;

    const documentId = uploadedDocumentIds[0];

    showQuizStep('quizLoading');
    document.querySelector('#quizLoading p').textContent = 'Generating quiz from uploaded documents...';

    fetch('/api/quiz/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            source_type: 'document',
            topic: 'Quiz from uploaded documents',
            num_questions: 10,
            document_id: documentId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentQuiz = data.quiz;
                quizData = data.questions;
                currentQuestionIndex = 0;
                userAnswers = new Array(quizData.length).fill(null);
                showQuestion();
            } else {
                alert('Error generating quiz: ' + data.message);
                closeQuizModal();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate quiz');
            closeQuizModal();
        });
}


function quizPrepChoice(choice) {
    if (choice === 'learn') {
        // Ask for topic to learn
        const topic = prompt('What topic would you like to learn about?');
        if (!topic || !topic.trim()) {
            showQuizStep('quizPromptOptions');
            return;
        }

        // Teach the topic
        teachTopic(topic, true);  // true = then take quiz
    } else {
        showQuizStep('quizPromptInput');
    }
}

async function teachTopic(topic, thenQuiz = false) {
    showQuizStep('quizLoading');
    document.querySelector('#quizLoading p').textContent = 'Generating teaching content...';

    try {
        const response = await fetch('/api/teach/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Show teaching content
            showTeachingContent(topic, data.teaching_content, thenQuiz);
        } else {
            alert('Error: ' + data.message);
            showQuizStep('quizPromptOptions');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load teaching content');
        showQuizStep('quizPromptOptions');
    }
}

function showTeachingContent(topic, content, thenQuiz) {
    // Create teaching display if it doesn't exist
    let teachingStep = document.getElementById('quizTeachingDisplay');
    if (!teachingStep) {
        // Add teaching step to modal
        const modalContent = document.querySelector('.quiz-modal-content');
        const teachingHTML = `
            <div class="quiz-step hidden" id="quizTeachingDisplay">
                <div class="quiz-header">
                    <h2 id="teachingTopic">Learning: Topic</h2>
                    <p>Study this content before taking the quiz</p>
                </div>
                <div class="teaching-content" id="teachingContent" style="
                    max-height: 60vh;
                    overflow-y: auto;
                    padding: 2rem;
                    background: var(--bg-app);
                    border-radius: 12px;
                    line-height: 1.8;
                    margin-bottom: 2rem;
                "></div>
                <button class="btn-primary" id="proceedToQuizBtn" onclick="proceedToQuizAfterLearning()">
                    I'm Ready for the Quiz
                </button>
            </div>
        `;
        modalContent.insertAdjacentHTML('beforeend', teachingHTML);
        teachingStep = document.getElementById('quizTeachingDisplay');
    }

    // Set content
    document.getElementById('teachingTopic').textContent = `Learning: ${topic}`;
    document.getElementById('teachingContent').innerHTML = content.replace(/\n/g, '<br><br>');

    // Store topic for quiz
    if (thenQuiz) {
        document.getElementById('quizTopicInput').value = topic;
    }

    showQuizStep('quizTeachingDisplay');
}

function proceedToQuizAfterLearning() {
    const topic = document.getElementById('quizTopicInput').value;
    document.getElementById('quizNumQuestions').value = 10;
    generateQuiz();
}

async function generateQuiz() {
    const topic = document.getElementById('quizTopicInput').value.trim();
    const numQuestions = parseInt(document.getElementById('quizNumQuestions').value) || 10;

    if (!topic && quizSource !== 'document') {
        alert('Please enter a topic');
        return;
    }

    showQuizStep('quizLoading');

    try {
        const documentId = quizSource === 'document' ? document.getElementById('documentSelect').value : null;

        const response = await fetch('/api/quiz/generate/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_type: quizSource,
                topic: topic,
                num_questions: numQuestions,
                document_id: documentId
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            currentQuiz = data.quiz;
            quizData = data.questions;
            currentQuestionIndex = 0;
            userAnswers = new Array(quizData.length).fill(null);
            showQuestion();
        } else {
            alert('Error generating quiz: ' + data.message);
            closeQuizModal();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate quiz');
        closeQuizModal();
    }
}

function showQuestion() {
    if (currentQuestionIndex >= quizData.length) {
        completeQuiz();
        return;
    }

    const question = quizData[currentQuestionIndex];

    // Update progress
    const progress = ((currentQuestionIndex) / quizData.length) * 100;
    document.getElementById('quizProgressBar').style.width = progress + '%';

    // Update counter
    document.getElementById('currentQuestionNum').textContent = currentQuestionIndex + 1;
    document.getElementById('totalQuestions').textContent = quizData.length;

    // Show question
    document.getElementById('quizQuestionText').textContent = question.question;

    // Render options
    const optionsContainer = document.getElementById('quizOptionsContainer');
    optionsContainer.innerHTML = question.options.map((option, index) => `
        <div class="quiz-option" onclick="selectOption(${index})">
            ${option}
        </div>
    `).join('');

    // Disable next button until answer selected
    document.getElementById('quizNextBtn').disabled = true;

    showQuizStep('quizQuestionsDisplay');
}

function selectOption(optionIndex) {
    // Remove previous selection
    document.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));

    // Mark selected
    document.querySelectorAll('.quiz-option')[optionIndex].classList.add('selected');

    // Store answer
    const question = quizData[currentQuestionIndex];
    userAnswers[currentQuestionIndex] = question.options[optionIndex];

    // Enable next button
    document.getElementById('quizNextBtn').disabled = false;
}

async function nextQuestion() {
    // Submit current answer
    const question = quizData[currentQuestionIndex];
    const userAnswer = userAnswers[currentQuestionIndex];

    try {
        const response = await fetch(`/api/quiz/${currentQuiz.id}/submit/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: question.id,
                answer: userAnswer
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Store evaluation result
            quizData[currentQuestionIndex].is_correct = data.is_correct;
            quizData[currentQuestionIndex].explanation = data.explanation;
        }
    } catch (error) {
        console.error('Error submitting answer:', error);
    }

    currentQuestionIndex++;
    showQuestion();
}

async function completeQuiz() {
    try {
        const response = await fetch(`/api/quiz/${currentQuiz.id}/complete/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showResults(data);
        }
    } catch (error) {
        console.error('Error completing quiz:', error);
    }
}

function showResults(data) {
    // Update score display
    document.getElementById('quizScoreNum').textContent = data.score;
    document.getElementById('quizScoreTotal').textContent = data.total_questions;
    const percent = Math.round((data.score / data.total_questions) * 100);
    document.getElementById('quizScorePercent').textContent = percent + '%';

    // Show wrong answers
    const wrongContainer = document.getElementById('quizWrongAnswersContainer');
    const wrongAnswers = quizData.filter(q => !q.is_correct);

    if (wrongAnswers.length === 0) {
        wrongContainer.innerHTML = '<p style="text-align: center; color: var(--success);">Perfect score! 🎉</p>';
    } else {
        wrongContainer.innerHTML = wrongAnswers.map((q, index) => `
            <div class="quiz-wrong-answer-item">
                <h4>Question ${quizData.indexOf(q) + 1}</h4>
                <p style="margin-bottom: 1rem;">${q.question}</p>
                <div class="answer-comparison">
                    <div class="answer-row wrong">
                        <strong>Your answer:</strong>
                        <span>${userAnswers[quizData.indexOf(q)]}</span>
                    </div>
                    <div class="answer-row correct">
                        <strong>Correct answer:</strong>
                        <span>${q.correct_answer}</span>
                    </div>
                </div>
                <div class="explanation">
                    <strong>Explanation:</strong> ${q.explanation || 'The correct answer is ' + q.correct_answer}
                </div>
                <button class="btn-learn" onclick="addToLearning(${quizData.indexOf(q)})">
                    <i class="fas fa-plus"></i> Add to Learning Track
                </button>
            </div>
        `).join('');
    }

    showQuizStep('quizResults');
}

// Wikipedia Learn More function
async function learnMoreWikipedia(question, answer) {
    const topic = decodeURIComponent(answer);

    // Show loading
    const modal = document.createElement('div');
    modal.className = 'modal-overlay active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-header">
                <h3><i class="fab fa-wikipedia-w"></i> Learn More from Wikipedia</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <div style="text-align: center; padding: 2rem;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #667eea;"></i>
                    <p style="margin-top: 1rem;">Loading Wikipedia content...</p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    try {
        // Fetch Wikipedia content
        const response = await fetch('/api/wikipedia/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: topic })
        });

        const data = await response.json();

        if (data.status === 'success') {
            modal.querySelector('.modal-body').innerHTML = `
                <div style="line-height: 1.8; padding: 1rem;">
                    <p>${data.content}</p>
                    <a href="https://en.wikipedia.org/wiki/${encodeURIComponent(topic.replace(/ /g, '_'))}" 
                       target="_blank" 
                       class="btn-primary" 
                       style="display: inline-flex; align-items: center; gap: 0.5rem; margin-top: 1.5rem;">
                        Read Full Article <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            `;
        } else {
            modal.querySelector('.modal-body').innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <p style="color: var(--danger);">Could not load Wikipedia content</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching Wikipedia:', error);
        modal.querySelector('.modal-body').innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <p style="color: var(--danger);">Error loading content</p>
            </div>
        `;
    }
}

function retakeQuiz() {
    currentQuestionIndex = 0;
    userAnswers = new Array(quizData.length).fill(null);
    showQuestion();
}

// ===== Learning Track =====
function openLearningTrack() {
    document.getElementById('learningPanel').classList.add('active');
    loadLearningItems();
}

function closeLearningPanel() {
    document.getElementById('learningPanel').classList.remove('active');
}

async function loadLearningItems() {
    try {
        const response = await fetch('/api/learning/');
        const data = await response.json();

        const container = document.getElementById('learningPanelContent');

        if (data.items.length === 0) {
            container.innerHTML = `
                <div class="learning-empty">
                    <i class="fas fa-graduation-cap"></i>
                    <p>No learning items yet</p>
                    <small>Wrong quiz answers will appear here</small>
                </div>
            `;
        } else {
            container.innerHTML = data.items.map(item => `
                <div class="learning-item">
                    <div class="learning-item-header">
                        <span class="learning-item-topic">${item.topic}</span>
                        <div class="learning-item-actions">
                            <button onclick="markAsLearned(${item.id})" title="Mark as learned">
                                <i class="fas fa-check"></i>
                            </button>
                        </div>
                    </div>
                    <h4>${item.question}</h4>
                    <p><strong>Answer:</strong> ${item.correct_answer}</p>
                    ${item.explanation ? `<p><em>${item.explanation}</em></p>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading learning items:', error);
    }
}

async function addToLearning(questionIndex) {
    const question = quizData[questionIndex];

    try {
        const response = await fetch('/api/learning/add/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                quiz_id: currentQuiz.id,
                question_id: question.id,
                topic: currentQuiz.topic,
                question: question.question,
                correct_answer: question.correct_answer,
                user_wrong_answer: userAnswers[questionIndex],
                explanation: question.explanation
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('Added to learning track!');
        }
    } catch (error) {
        console.error('Error adding to learning:', error);
    }
}

async function markAsLearned(itemId) {
    try {
        const response = await fetch(`/api/learning/${itemId}/learned/`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'success') {
            loadLearningItems();
        }
    } catch (error) {
        console.error('Error marking as learned:', error);
    }
}

async function exportLearningPDF() {
    window.open(`/api/learning/export/pdf/`, '_blank');
}

function shareLearningEmail() {
    const email = prompt('Enter email address:');
    if (!email) return;

    fetch('/api/learning/send-email/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Learning track sent to ' + email);
            } else {
                alert('Error sending email: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to send email');
        });
}

// Delete document function
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/documents/${docId}/delete/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('Document deleted successfully');
            // Refresh the documents list
            showExistingDocuments();
        } else {
            alert('Failed to delete document: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('Error deleting document');
    }
}
