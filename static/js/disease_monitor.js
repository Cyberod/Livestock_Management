document.addEventListener('DOMContentLoaded', function() {
    initializeDiseaseMonitor();
});

function initializeDiseaseMonitor() {
    loadAnimalTypes();
    loadUserLivestock();
    setupEventHandlers();
}

function setupEventHandlers() {
    // Animal type change
    document.getElementById('animalType').addEventListener('change', function() {
        if (this.value) {
            loadSymptomSuggestions(this.value);
            document.getElementById('preventionBtn').disabled = false;
        } else {
            document.getElementById('symptomCheckboxes').innerHTML = '<p class="text-muted">Please select an animal type first</p>';
            document.getElementById('preventionBtn').disabled = true;
        }
        updateAnalyzeButton();
    });

    // Form submission
    document.getElementById('symptomForm').addEventListener('submit', function(e) {
        e.preventDefault();
        analyzeSymptoms();
    });

    // Prevention button
    document.getElementById('preventionBtn').addEventListener('click', function() {
        const animalTypeId = document.getElementById('animalType').value;
        if (animalTypeId) {
            showPrevention(animalTypeId);
        }
    });

    // Save health record button
    document.getElementById('saveHealthRecordBtn').addEventListener('click', function() {
        saveHealthRecord();
    });
}

async function loadAnimalTypes() {
    try {
        const response = await fetch('/api/animal-types/');
        const animalTypes = await response.json();
        
        const select = document.getElementById('animalType');
        select.innerHTML = '<option value="">Select animal type...</option>';
        
        animalTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading animal types:', error);
    }
}

async function loadUserLivestock() {
    try {
        const response = await fetch('/api/user/livestock/');
        const livestock = await response.json();
        
        const select = document.getElementById('livestockSelect');
        select.innerHTML = '<option value="">Choose from your livestock...</option>';
        
        livestock.forEach(animal => {
            const option = document.createElement('option');
            option.value = animal.id;
            option.textContent = `${animal.tag_number} - ${animal.name || animal.animal_type_name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading livestock:', error);
    }
}

async function loadSymptomSuggestions(animalTypeId) {
    try {
        const response = await fetch(`/api/disease/symptom-suggestions/?animal_type_id=${animalTypeId}`);
        const data = await response.json();
        
        const container = document.getElementById('symptomCheckboxes');
        container.innerHTML = '';
        
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(symptom => {
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'form-check mb-2';
                
                checkboxDiv.innerHTML = `
                    <input class="form-check-input symptom-checkbox" type="checkbox" value="${symptom.id}" id="symptom${symptom.id}">
                    <label class="form-check-label" for="symptom${symptom.id}">
                        <strong>${symptom.name}</strong>
                        ${symptom.description ? `<br><small class="text-muted">${symptom.description}</small>` : ''}
                    </label>
                `;
                
                container.appendChild(checkboxDiv);
            });
            
            // Add event listeners to checkboxes
            document.querySelectorAll('.symptom-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    updateSelectedSymptoms();
                    updateAnalyzeButton();
                });
            });
        } else {
            container.innerHTML = '<p class="text-muted">No symptoms found for this animal type</p>';
        }
    } catch (error) {
        console.error('Error loading symptom suggestions:', error);
        document.getElementById('symptomCheckboxes').innerHTML = '<p class="text-danger">Error loading symptoms</p>';
    }
}

function updateSelectedSymptoms() {
    const selectedCheckboxes = document.querySelectorAll('.symptom-checkbox:checked');
    const container = document.getElementById('selectedSymptomsList');
    const display = document.getElementById('selectedSymptomsDisplay');
    
    if (selectedCheckboxes.length > 0) {
        container.innerHTML = '';
        selectedCheckboxes.forEach(checkbox => {
            const label = document.querySelector(`label[for="${checkbox.id}"]`);
            const symptomName = label.querySelector('strong').textContent;
            
            const badge = document.createElement('span');
            badge.className = 'badge bg-warning text-dark me-1';
            badge.textContent = symptomName;
            container.appendChild(badge);
        });
        display.style.display = 'block';
    } else {
        display.style.display = 'none';
    }
}

function updateAnalyzeButton() {
    const animalType = document.getElementById('animalType').value;
    const selectedSymptoms = document.querySelectorAll('.symptom-checkbox:checked');
    
    document.getElementById('analyzeBtn').disabled = !animalType || selectedSymptoms.length === 0;
}

async function analyzeSymptoms() {
    showLoadingState();
    
    try {
        const animalTypeId = document.getElementById('animalType').value;
        const livestockId = document.getElementById('livestockSelect').value;
        const selectedSymptoms = Array.from(document.querySelectorAll('.symptom-checkbox:checked'))
            .map(cb => parseInt(cb.value));
        
        const requestData = {
            animal_type_id: parseInt(animalTypeId),
            symptoms: selectedSymptoms
        };
        
        if (livestockId) {
            requestData.livestock_id = parseInt(livestockId);
        }
        
        const response = await fetch('/api/disease/analyze-symptoms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayAnalysisResults(data);
        
    } catch (error) {
        console.error('Error analyzing symptoms:', error);
        showErrorState('Failed to analyze symptoms. Please try again.');
    }
}

function displayAnalysisResults(data) {
    // Update analysis summary
    updateAnalysisSummary(data);
    
    // Show critical alerts if any
    updateCriticalAlerts(data.critical_alerts);
    
    // Display disease results
    updateDiseaseResults(data.disease_results);
    
    // Show health record option if livestock selected
    const livestockId = document.getElementById('livestockSelect').value;
    if (livestockId) {
        document.getElementById('healthRecordAction').style.display = 'block';
    }
    
    // Update results count
    document.getElementById('resultsCount').textContent = data.total_diseases_found;
    document.getElementById('resultsCount').style.display = 'inline';
    
    // Show results
    showResultsState();
}

function updateAnalysisSummary(data) {
    const container = document.getElementById('analysisSummaryContent');
    const symptoms = data.input_symptoms.map(s => s.name).join(', ');
    
    let html = `<strong>Animal:</strong> ${data.animal_info.animal_type}<br>`;
    html += `<strong>Symptoms:</strong> ${symptoms}<br>`;
    html += `<strong>Conditions Found:</strong> ${data.total_diseases_found}`;
    
    if (data.highest_confidence > 0) {
        html += ` (Top match: ${(data.highest_confidence * 100).toFixed(1)}% confidence)`;
    }
    
    container.innerHTML = html;
}

function updateCriticalAlerts(criticalAlerts) {
    const container = document.getElementById('criticalAlertsContent');
    const alertDiv = document.getElementById('criticalAlerts');
    
    if (criticalAlerts && criticalAlerts.length > 0) {
        let html = '<p><strong>Immediate attention required for:</strong></p><ul>';
        
        criticalAlerts.forEach(alert => {
            html += `<li><strong>${alert.disease.name}</strong> - ${alert.severity_level} severity`;
            if (alert.requires_vet) {
                html += ' <span class="badge bg-danger">Vet Required</span>';
            }
            html += '</li>';
        });
        
        html += '</ul><p class="mb-0"><strong>Recommendation:</strong> Contact a veterinarian immediately.</p>';
        container.innerHTML = html;
        alertDiv.style.display = 'block';
    } else {
        alertDiv.style.display = 'none';
    }
}

function updateDiseaseResults(diseaseResults) {
    const container = document.getElementById('diseaseResultsList');
    container.innerHTML = '';
    
    if (diseaseResults && diseaseResults.length > 0) {
        diseaseResults.forEach((result, index) => {
            const card = createDiseaseResultCard(result, index + 1);
            container.appendChild(card);
        });
    } else {
        container.innerHTML = '<p class="text-muted">No specific conditions identified with current symptoms.</p>';
    }
}

function createDiseaseResultCard(result, rank) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    const confidencePercentage = (result.confidence_score * 100).toFixed(1);
    const severityBadge = getSeverityBadge(result.severity_level);
    const vetBadge = result.requires_vet ? '<span class="badge bg-danger ms-2">Vet Required</span>' : '';
    
    card.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
                <span class="badge bg-primary me-2">${rank}</span>
                ${result.disease.name}
                ${severityBadge}
                ${vetBadge}
            </h6>
            <span class="badge bg-secondary">${confidencePercentage}% match</span>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <h6>Matching Symptoms</h6>
                    <ul class="list-unstyled">
                        ${result.matching_symptoms.map(s => `<li><i class="bi bi-check text-success me-1"></i>${s.name}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Additional Symptoms to Watch</h6>
                    ${result.missing_symptoms.length > 0 ? `
                        <ul class="list-unstyled">
                            ${result.missing_symptoms.map(s => `<li><i class="bi bi-dash text-muted me-1"></i>${s.name}</li>`).join('')}
                        </ul>
                    ` : '<p class="text-muted small">No additional symptoms</p>'}
                </div>
            </div>
            
            ${result.disease.description ? `
                <div class="mt-2">
                    <h6>About This Condition</h6>
                    <p class="small">${result.disease.description}</p>
                </div>
            ` : ''}
            
            <div class="mt-2">
                <h6>Recommendations</h6>
                <p class="small">${result.recommendations}</p>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mt-2">
                <small class="text-muted">
                    ${result.disease.is_contagious ? '<i class="bi bi-exclamation-triangle text-warning me-1"></i>Contagious' : '<i class="bi bi-check-circle text-success me-1"></i>Non-contagious'}
                </small>
                <small class="text-muted">Confidence: ${confidencePercentage}%</small>
            </div>
        </div>
    `;
    
    return card;
}

function getSeverityBadge(severity) {
    const badges = {
        'CRITICAL': '<span class="badge bg-danger">Critical</span>',
        'HIGH': '<span class="badge bg-warning">High</span>',
        'MEDIUM': '<span class="badge bg-info">Medium</span>',
        'LOW': '<span class="badge bg-secondary">Low</span>'
    };
    return badges[severity] || '<span class="badge bg-secondary">Unknown</span>';
}

async function showPrevention(animalTypeId) {
    try {
        const response = await fetch(`/api/disease/prevention/?animal_type_id=${animalTypeId}`);
        const data = await response.json();
        
        if (response.ok) {
            alert(`Prevention tips for ${data.animal_type} loaded! (Full implementation in next update)`);
        } else {
            throw new Error(data.error || 'Failed to load prevention recommendations');
        }
    } catch (error) {
        console.error('Error loading prevention recommendations:', error);
        alert('Failed to load prevention recommendations.');
    }
}

async function saveHealthRecord() {
    const livestockId = document.getElementById('livestockSelect').value;
    const selectedSymptoms = Array.from(document.querySelectorAll('.symptom-checkbox:checked'))
        .map(cb => parseInt(cb.value));
    
    if (!livestockId || selectedSymptoms.length === 0) {
        alert('Please select a specific animal and symptoms to save health record.');
        return;
    }
    
    try {
        const requestData = {
            livestock_id: parseInt(livestockId),
            symptom_ids: selectedSymptoms,
            notes: 'Health record created from symptom analysis'
        };
        
        const response = await fetch('/api/disease/health-record/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert(`Health record saved successfully for ${result.livestock}!`);
            document.getElementById('saveHealthRecordBtn').disabled = true;
            document.getElementById('saveHealthRecordBtn').innerHTML = '<i class="bi bi-check me-1"></i>Saved';
        } else {
            throw new Error('Failed to save health record');
        }
    } catch (error) {
        console.error('Error saving health record:', error);
        alert('Failed to save health record. Please try again.');
    }
}

// State management functions
function showLoadingState() {
    document.getElementById('initialState').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('loadingState').style.display = 'block';
}

function showErrorState(message) {
    document.getElementById('initialState').style.display = 'none';
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorState').style.display = 'block';
}

function showResultsState() {
    document.getElementById('initialState').style.display = 'none';
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}
