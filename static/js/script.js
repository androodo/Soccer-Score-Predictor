document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const predictionForm = document.getElementById('prediction-form');
    const resultsSection = document.getElementById('results-section');
    const loadingSpinner = document.getElementById('loading-spinner');
    const themeToggle = document.getElementById('theme-toggle');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history');
    
    // Hide results section initially
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Initialize theme
    initTheme();
    
    // Initialize prediction history
    initPredictionHistory();
    
    // Add form submission event listener
    if (predictionForm) {
        predictionForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Add theme toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Add clear history event listener
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearPredictionHistory);
    }
    
    // Form submission handler
    function handleFormSubmit(event) {
        event.preventDefault();
        
        // Get form data
        const formData = new FormData(predictionForm);
        const homeTeam = formData.get('home_team');
        const awayTeam = formData.get('away_team');
        
        // Validate form data
        if (!homeTeam || !awayTeam) {
            showError('Please select both home and away teams');
            return;
        }
        
        if (homeTeam === awayTeam) {
            showError('Home and away teams cannot be the same');
            return;
        }
        
        // Show loading state
        showLoading();
        
        // Make API request to get prediction
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'An error occurred while making the prediction');
                });
            }
            return response.json();
        })
        .then(data => {
            // Update UI with prediction results
            updatePredictionResults(data, homeTeam, awayTeam);
            
            // Add to prediction history
            addToPredictionHistory(data, homeTeam, awayTeam);
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            hideLoading();
        });
    }
    
    // Update the UI with prediction results
    function updatePredictionResults(data, homeTeam, awayTeam) {
        // Update team names
        document.getElementById('home-team-display').textContent = homeTeam;
        document.getElementById('away-team-display').textContent = awayTeam;
        
        // Update team logos
        updateTeamLogo('home-team-logo', homeTeam);
        updateTeamLogo('away-team-logo', awayTeam);
        
        // Update probabilities
        const homeWinProbability = data.home_win_probability;
        const drawProbability = data.draw_probability;
        const awayWinProbability = data.away_win_probability;
        
        document.getElementById('home-win-probability').textContent = `${homeWinProbability}%`;
        document.getElementById('draw-probability').textContent = `${drawProbability}%`;
        document.getElementById('away-win-probability').textContent = `${awayWinProbability}%`;
        
        // Update probability bars with animation
        setTimeout(() => {
            document.querySelector('.home-probability').style.width = `${homeWinProbability}%`;
            document.querySelector('.draw-probability').style.width = `${drawProbability}%`;
            document.querySelector('.away-probability').style.width = `${awayWinProbability}%`;
        }, 100);
        
        // Update prediction result and expected score
        document.getElementById('predicted-result').textContent = data.predicted_result;
        document.getElementById('expected-score').textContent = data.expected_score;
        
        // Show results section with animation
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.classList.add('visible');
        }, 10);
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Update team logo
    function updateTeamLogo(logoId, teamName) {
        const logoElement = document.getElementById(logoId);
        if (!logoElement) return;
        
        // Generate logo file name from team name
        const normalizedTeamName = normalizeTeamName(teamName);
        const logoPath = `/static/images/teams/${normalizedTeamName}.png`;
        
        // Try to load the team logo image
        const img = new Image();
        img.onload = function() {
            // Logo image exists, use it
            logoElement.innerHTML = '';
            logoElement.style.backgroundColor = 'transparent';
            logoElement.appendChild(img);
        };
        
        img.onerror = function() {
            // Logo image doesn't exist, use fallback with first letter
            const firstLetter = teamName.charAt(0).toUpperCase();
            logoElement.textContent = firstLetter;
            
            // Add a unique color based on team name (for visual distinction)
            const hue = getHueFromString(teamName);
            logoElement.style.backgroundColor = `hsl(${hue}, 70%, 60%)`;
        };
        
        // Set image source to try loading
        img.src = logoPath;
        img.alt = `${teamName} logo`;
        img.className = 'team-logo-img';
    }
    
    // Helper function to normalize team names for file paths
    function normalizeTeamName(teamName) {
        // Convert to lowercase, replace spaces with underscores
        // and remove special characters
        return teamName
            .toLowerCase()
            .replace(/\s+/g, '_')
            .replace(/[^a-z0-9_]/g, '');
    }
    
    // Get a consistent hue from a string (for team logo colors)
    function getHueFromString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        return hash % 360;
    }
    
    // Initialize theme from localStorage
    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
    }
    
    // Toggle between light and dark theme
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        updateThemeIcon(newTheme);
    }
    
    // Update theme icon based on current theme
    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
            } else {
                icon.className = 'fas fa-moon';
            }
        }
    }
    
    // Initialize prediction history from localStorage
    function initPredictionHistory() {
        const predictionHistory = getPredictionHistory();
        
        // Clear the history list
        if (historyList) {
            historyList.innerHTML = '';
            
            if (predictionHistory.length === 0) {
                const emptyMessage = document.createElement('div');
                emptyMessage.className = 'empty-history';
                emptyMessage.textContent = 'No prediction history yet. Make your first prediction!';
                historyList.appendChild(emptyMessage);
            } else {
                // Add each prediction to the history list
                predictionHistory.forEach(prediction => {
                    const historyItem = createHistoryItem(prediction);
                    historyList.appendChild(historyItem);
                });
            }
        }
    }
    
    // Get prediction history from localStorage
    function getPredictionHistory() {
        const historyJson = localStorage.getItem('predictionHistory');
        return historyJson ? JSON.parse(historyJson) : [];
    }
    
    // Add prediction to history
    function addToPredictionHistory(data, homeTeam, awayTeam) {
        const prediction = {
            homeTeam,
            awayTeam,
            result: data.predicted_result,
            expectedScore: data.expected_score,
            timestamp: new Date().toISOString()
        };
        
        let predictionHistory = getPredictionHistory();
        
        // Add new prediction at the beginning
        predictionHistory.unshift(prediction);
        
        // Keep only the last 10 predictions
        if (predictionHistory.length > 10) {
            predictionHistory = predictionHistory.slice(0, 10);
        }
        
        // Save to localStorage
        localStorage.setItem('predictionHistory', JSON.stringify(predictionHistory));
        
        // Update UI
        initPredictionHistory();
    }
    
    // Create a history item DOM element
    function createHistoryItem(prediction) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        // Create teams element
        const teamsElement = document.createElement('div');
        teamsElement.className = 'history-teams';
        
        // Create home team container
        const homeTeamContainer = document.createElement('div');
        homeTeamContainer.className = 'history-team-container';
        
        // Create home team logo
        const homeTeamLogo = document.createElement('div');
        homeTeamLogo.className = 'history-team-logo';
        const homeLogoImg = new Image();
        homeLogoImg.src = `/static/images/teams/${normalizeTeamName(prediction.homeTeam)}.png`;
        homeLogoImg.alt = `${prediction.homeTeam} logo`;
        homeLogoImg.className = 'team-logo-img';
        homeLogoImg.onerror = function() {
            // Fallback to first letter if image doesn't exist
            homeTeamLogo.textContent = prediction.homeTeam.charAt(0).toUpperCase();
            // Add a unique color based on team name
            const hue = getHueFromString(prediction.homeTeam);
            homeTeamLogo.style.backgroundColor = `hsl(${hue}, 70%, 60%)`;
        };
        homeTeamLogo.appendChild(homeLogoImg);
        
        const homeTeamElement = document.createElement('span');
        homeTeamElement.className = 'history-team-name';
        homeTeamElement.textContent = prediction.homeTeam;
        
        homeTeamContainer.appendChild(homeTeamLogo);
        homeTeamContainer.appendChild(homeTeamElement);
        
        const vsElement = document.createElement('span');
        vsElement.className = 'history-vs';
        vsElement.textContent = 'vs';
        
        // Create away team container
        const awayTeamContainer = document.createElement('div');
        awayTeamContainer.className = 'history-team-container';
        
        // Create away team logo
        const awayTeamLogo = document.createElement('div');
        awayTeamLogo.className = 'history-team-logo';
        const awayLogoImg = new Image();
        awayLogoImg.src = `/static/images/teams/${normalizeTeamName(prediction.awayTeam)}.png`;
        awayLogoImg.alt = `${prediction.awayTeam} logo`;
        awayLogoImg.className = 'team-logo-img';
        awayLogoImg.onerror = function() {
            // Fallback to first letter if image doesn't exist
            awayTeamLogo.textContent = prediction.awayTeam.charAt(0).toUpperCase();
            // Add a unique color based on team name
            const hue = getHueFromString(prediction.awayTeam);
            awayTeamLogo.style.backgroundColor = `hsl(${hue}, 70%, 60%)`;
        };
        awayTeamLogo.appendChild(awayLogoImg);
        
        const awayTeamElement = document.createElement('span');
        awayTeamElement.className = 'history-team-name';
        awayTeamElement.textContent = prediction.awayTeam;
        
        awayTeamContainer.appendChild(awayTeamLogo);
        awayTeamContainer.appendChild(awayTeamElement);
        
        teamsElement.appendChild(homeTeamContainer);
        teamsElement.appendChild(vsElement);
        teamsElement.appendChild(awayTeamContainer);
        
        // Create result element
        const resultElement = document.createElement('span');
        resultElement.className = 'history-result';
        resultElement.textContent = prediction.result;
        
        // Add appropriate class based on result
        if (prediction.result === 'Home Win') {
            resultElement.classList.add('result-home-win');
        } else if (prediction.result === 'Away Win') {
            resultElement.classList.add('result-away-win');
        } else {
            resultElement.classList.add('result-draw');
        }
        
        // Add elements to history item
        historyItem.appendChild(teamsElement);
        historyItem.appendChild(resultElement);
        
        // Add click handler to reuse this prediction
        historyItem.addEventListener('click', () => {
            // Set form values
            document.getElementById('home-team').value = prediction.homeTeam;
            document.getElementById('away-team').value = prediction.awayTeam;
            
            // Auto-submit the form
            predictionForm.dispatchEvent(new Event('submit'));
        });
        
        return historyItem;
    }
    
    // Clear prediction history
    function clearPredictionHistory() {
        localStorage.removeItem('predictionHistory');
        initPredictionHistory();
    }
    
    // Show error message with nice styling
    function showError(message) {
        // Create error element
        const errorElement = document.createElement('div');
        errorElement.className = 'error-notification';
        errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        
        // Add to document
        document.body.appendChild(errorElement);
        
        // Animate in
        setTimeout(() => {
            errorElement.classList.add('visible');
        }, 10);
        
        // Remove after delay
        setTimeout(() => {
            errorElement.classList.remove('visible');
            setTimeout(() => {
                errorElement.remove();
            }, 300);
        }, 4000);
    }
    
    // Show loading state
    function showLoading() {
        const submitButton = predictionForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting...';
        }
        
        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }
        
        // Hide previous results while loading
        if (resultsSection && resultsSection.classList.contains('visible')) {
            resultsSection.classList.remove('visible');
            setTimeout(() => {
                resultsSection.style.display = 'none';
            }, 300);
        }
    }
    
    // Hide loading state
    function hideLoading() {
        const submitButton = predictionForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-magic"></i> Predict';
        }
        
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
    }
    
    // Reset form handler - hide results when form is reset
    const resetButton = predictionForm ? predictionForm.querySelector('button[type="reset"]') : null;
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (resultsSection) {
                resultsSection.classList.remove('visible');
                setTimeout(() => {
                    resultsSection.style.display = 'none';
                }, 300);
            }
        });
    }
}); 