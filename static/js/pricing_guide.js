/**
 * Pricing Guide JavaScript
 * Handles market price analysis and selling recommendations
 */

class PricingGuide {
    constructor() {
        this.apiUrls = {
            animalTypes: '/api/animal-types/',
            analyzeMarket: '/api/pricing/analyze-market/',
            sellingRecommendations: '/api/pricing/selling-recommendations/',
            livestockProfitability: '/api/pricing/livestock/{id}/profitability/',
            userLivestock: '/api/user/livestock/'
        };
        
        this.priceChart = null;
        this.init();
    }
    
    init() {
        this.loadAnimalTypes();
        this.loadSellingRecommendations();
        this.loadQuickStats();
        this.bindEvents();
    }
    
    bindEvents() {
        // Price analysis form
        document.getElementById('priceAnalysisForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzePrices();
        });
        
        // Refresh recommendations
        document.getElementById('refreshRecommendations').addEventListener('click', () => {
            this.loadSellingRecommendations();
        });
    }
    
    async loadAnimalTypes() {
        try {
            const response = await fetch(this.apiUrls.animalTypes);
            const data = await response.json();
            
            const select = document.getElementById('animalType');
            select.innerHTML = '<option value="">Select animal type...</option>';
            
            data.forEach(animalType => {
                const option = document.createElement('option');
                option.value = animalType.id;
                option.textContent = animalType.name;
                select.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading animal types:', error);
            this.showToast('Error loading animal types', 'error');
        }
    }
    
    async analyzePrices() {
        const submitBtn = document.querySelector('#priceAnalysisForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Analyzing...';
        submitBtn.disabled = true;
        
        try {
            const formData = {
                animal_type_id: parseInt(document.getElementById('animalType').value),
                location: document.getElementById('location').value,
                quality_grade: document.getElementById('qualityGrade').value
            };
            
            const response = await fetch(this.apiUrls.analyzeMarket, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to analyze prices');
            }
            
            const data = await response.json();
            this.displayPriceResults(data);
            
        } catch (error) {
            console.error('Error analyzing prices:', error);
            this.showToast('Error analyzing market prices', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    displayPriceResults(data) {
        document.getElementById('currentPrice').textContent = data.current_price_per_kg.toFixed(2);
        document.getElementById('dateAnalyzed').textContent = data.date_analyzed;
        document.getElementById('marketRecommendation').textContent = data.market_recommendation;
        
        // Display trend
        const trendIcon = document.getElementById('trendIcon');
        const trendText = document.getElementById('trendText');
        const trendPercentage = data.trend_percentage;
        
        trendText.textContent = `${trendPercentage > 0 ? '+' : ''}${trendPercentage.toFixed(1)}%`;
        
        if (data.price_trend === 'RISING') {
            trendIcon.className = 'bi bi-arrow-up me-2 trend-up';
            trendText.className = 'trend-up';
        } else if (data.price_trend === 'FALLING') {
            trendIcon.className = 'bi bi-arrow-down me-2 trend-down';
            trendText.className = 'trend-down';
        } else {
            trendIcon.className = 'bi bi-arrow-right me-2 trend-stable';
            trendText.className = 'trend-stable';
        }
        
        // Display confidence level
        const confidenceBadge = document.getElementById('confidenceLevel');
        confidenceBadge.textContent = data.confidence_level;
        confidenceBadge.className = `badge bg-${this.getConfidenceColor(data.confidence_level)}`;
        
        // Show results section
        document.getElementById('priceResults').style.display = 'block';
        
        // Update price chart
        this.updatePriceChart(data.historical_data);
    }
    
    updatePriceChart(historicalData) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        if (this.priceChart) {
            this.priceChart.destroy();
        }
        
        const labels = historicalData.map(item => item.date);
        const prices = historicalData.map(item => item.price);
        
        this.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price per kg ($)',
                    data: prices,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Price ($)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }
    
    async loadSellingRecommendations() {
        const container = document.getElementById('sellingRecommendations');
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading recommendations...</p>
            </div>
        `;
        
        try {
            const response = await fetch(this.apiUrls.sellingRecommendations);
            if (!response.ok) {
                throw new Error('Failed to load recommendations');
            }
            
            const data = await response.json();
            this.displaySellingRecommendations(data);
            
        } catch (error) {
            console.error('Error loading selling recommendations:', error);
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Unable to load selling recommendations. Please try again later.
                </div>
            `;
        }
    }
    
    displaySellingRecommendations(data) {
        const container = document.getElementById('sellingRecommendations');
        
        if (data.recommendations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-clipboard-x text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-2">No livestock available for sale recommendations.</p>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="mb-3">
                <div class="row text-center">
                    <div class="col-md-3">
                        <h5 class="text-primary">${data.total_livestock}</h5>
                        <small class="text-muted">Total Animals</small>
                    </div>
                    <div class="col-md-3">
                        <h5 class="text-success">${data.high_priority_count}</h5>
                        <small class="text-muted">High Priority</small>
                    </div>
                    <div class="col-md-3">
                        <h5 class="text-warning">$${data.total_potential_profit.toFixed(2)}</h5>
                        <small class="text-muted">Potential Profit</small>
                    </div>
                    <div class="col-md-3">
                        <button class="btn btn-sm btn-outline-primary" onclick="pricingGuide.exportRecommendations()">
                            <i class="bi bi-download me-1"></i>Export
                        </button>
                    </div>
                </div>
            </div>
            <hr>
            <div class="row">
        `;
        
        data.recommendations.forEach(recommendation => {
            const livestock = recommendation.livestock;
            const profitability = recommendation.profitability;
            const priorityClass = this.getPriorityClass(recommendation.action_priority);
            const profitColor = profitability.estimated_profit >= 0 ? 'text-success' : 'text-danger';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="price-card ${priorityClass}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-0">${livestock.name || livestock.tag_number}</h6>
                            <span class="badge bg-secondary">${livestock.animal_type_name}</span>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Current Value</small>
                                <div class="fw-bold">$${profitability.current_market_value.toFixed(2)}</div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Estimated Profit</small>
                                <div class="fw-bold ${profitColor}">$${profitability.estimated_profit.toFixed(2)}</div>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Profit Margin</small>
                                <div class="fw-bold ${profitColor}">${profitability.profit_margin_percentage.toFixed(1)}%</div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Selling Time</small>
                                <div class="fw-bold">${recommendation.optimal_selling_time}</div>
                            </div>
                        </div>
                        <hr>
                        <p class="mb-2"><small>${profitability.recommendation}</small></p>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="pricingGuide.viewProfitability(${livestock.id})">
                                <i class="bi bi-graph-up me-1"></i>Analysis
                            </button>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-success">
                                    <i class="bi bi-check-circle me-1"></i>Mark for Sale
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    async viewProfitability(livestockId) {
        try {
            const url = this.apiUrls.livestockProfitability.replace('{id}', livestockId);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Failed to load profitability data');
            }
            
            const data = await response.json();
            this.showProfitabilityModal(data);
            
        } catch (error) {
            console.error('Error loading profitability data:', error);
            this.showToast('Error loading profitability analysis', 'error');
        }
    }
    
    showProfitabilityModal(data) {
        const modalContent = document.getElementById('profitabilityContent');
        const costBreakdown = data.cost_breakdown;
        
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Financial Summary</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>Current Market Value:</td>
                            <td class="fw-bold">$${data.current_market_value.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td>Total Investment:</td>
                            <td class="fw-bold">$${data.total_investment.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td>Estimated Profit:</td>
                            <td class="fw-bold ${data.estimated_profit >= 0 ? 'text-success' : 'text-danger'}">
                                $${data.estimated_profit.toFixed(2)}
                            </td>
                        </tr>
                        <tr>
                            <td>Profit Margin:</td>
                            <td class="fw-bold ${data.profit_margin_percentage >= 0 ? 'text-success' : 'text-danger'}">
                                ${data.profit_margin_percentage.toFixed(1)}%
                            </td>
                        </tr>
                        <tr>
                            <td>Break-even Price:</td>
                            <td class="fw-bold">$${data.break_even_price.toFixed(2)}/kg</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Cost Breakdown</h6>
                    <div class="mb-3">
                        <canvas id="costBreakdownChart" width="300" height="300"></canvas>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    <h6>Recommendation</h6>
                    <div class="alert alert-info">
                        <i class="bi bi-lightbulb me-2"></i>
                        ${data.recommendation}
                    </div>
                </div>
            </div>
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('profitabilityModal'));
        modal.show();
        
        // Create cost breakdown chart
        setTimeout(() => {
            this.createCostBreakdownChart(costBreakdown);
        }, 300);
    }
    
    createCostBreakdownChart(costBreakdown) {
        const ctx = document.getElementById('costBreakdownChart').getContext('2d');
        
        const data = {
            labels: ['Purchase Price', 'Feed Costs', 'Veterinary', 'Medicine', 'Other'],
            datasets: [{
                data: [
                    costBreakdown.purchase_price,
                    costBreakdown.feed_costs,
                    costBreakdown.veterinary_costs,
                    costBreakdown.medicine_costs,
                    costBreakdown.other_costs
                ],
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#ffc107',
                    '#dc3545',
                    '#6c757d'
                ]
            }]
        };
        
        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadQuickStats() {
        try {
            const response = await fetch(this.apiUrls.userLivestock);
            const data = await response.json();
            
            const totalLivestock = data.length;
            const readyForSale = data.filter(livestock => 
                livestock.current_weight_kg > 0 && 
                ['HEALTHY', 'PREGNANT'].includes(livestock.status)
            ).length;
            
            document.getElementById('totalLivestock').textContent = totalLivestock;
            document.getElementById('readyForSale').textContent = readyForSale;
            
            // Estimate total value (simplified calculation)
            const estimatedValue = data.reduce((total, livestock) => {
                const weight = livestock.current_weight_kg || 0;
                const basePrice = 8.0; // Default price per kg
                return total + (weight * basePrice);
            }, 0);
            
            document.getElementById('totalValue').textContent = `$${estimatedValue.toFixed(2)}`;
            
        } catch (error) {
            console.error('Error loading quick stats:', error);
        }
    }
    
    exportRecommendations() {
        // Simple CSV export functionality
        this.showToast('Export functionality coming soon!', 'info');
    }
    
    getPriorityClass(priority) {
        if (priority >= 4) return 'priority-high';
        if (priority >= 3) return 'priority-medium';
        return 'priority-low';
    }
    
    getConfidenceColor(level) {
        switch (level) {
            case 'HIGH': return 'success';
            case 'MEDIUM': return 'warning';
            case 'LOW': return 'danger';
            default: return 'secondary';
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    showToast(message, type = 'info') {
        // Create and show a toast notification
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Initialize the pricing guide when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pricingGuide = new PricingGuide();
});
