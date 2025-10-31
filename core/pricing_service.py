from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import date, timedelta
from .models import AnimalType, MarketPrice



@dataclass
class PriceAnalysisInput:
    """Data class for price analysis input parameters"""
    animal_type_id: int
    location: str
    breed_id: Optional[int] = None
    weight_kg: Optional[float] = None
    quality_grade: str = 'AVERAGE'


@dataclass
class PriceAnalysisResult:
    """Data class for price analysis results"""
    current_price_per_kg: float
    price_trend: str  # 'RISING', 'FALLING', 'STABLE'
    trend_percentage: float
    market_recommendation: str
    confidence_level: str
    historical_data: List[Dict]
    location: str
    date_analyzed: str


@dataclass
class ProfitabilityResult:
    """Data class for profitability analysis results"""
    livestock_id: int
    current_market_value: float
    total_investment: float
    estimated_profit: float
    profit_margin_percentage: float
    break_even_price: float
    recommendation: str
    cost_breakdown: Dict


class PricingAnalysisService:
    """
    Service class to handle pricing analysis and market recommendations
    """
    
    def analyze_market_price(self, price_input: PriceAnalysisInput) -> PriceAnalysisResult:
        """
        Analyze current market prices and trends
        
        Args:
            price_input: PriceAnalysisInput object with market query parameters
            
        Returns:
            PriceAnalysisResult object with market analysis
        """
        
        try:
            animal_type = AnimalType.objects.get(id=price_input.animal_type_id)
        except AnimalType.DoesNotExist:
            return self._create_empty_price_result(price_input.location)
        
        # Get recent market prices
        recent_prices = MarketPrice.objects.filter(
            animal_type=animal_type,
            location__icontains=price_input.location,
            date_recorded__gte=date.today() - timedelta(days=90)
        ).order_by('-date_recorded')
        
        # Filter by breed if specified
        if price_input.breed_id:
            recent_prices = recent_prices.filter(breed_id=price_input.breed_id)
        
        # Filter by quality grade
        recent_prices = recent_prices.filter(quality_grade=price_input.quality_grade)
        
        if not recent_prices.exists():
            return self._generate_estimated_price(animal_type, price_input)
        
        # Calculate current average price
        latest_prices = recent_prices[:5]  # Last 5 price records
        current_price = sum(float(p.price_per_kg) for p in latest_prices) / len(latest_prices)
        
        # Calculate trend
        trend_data = self._calculate_price_trend(recent_prices)
        
        # Generate recommendation
        recommendation = self._generate_market_recommendation(trend_data, current_price, animal_type)
        
        # Historical data for charts
        historical_data = self._format_historical_data(recent_prices[:30])
        
        return PriceAnalysisResult(
            current_price_per_kg=round(current_price, 2),
            price_trend=trend_data['trend'],
            trend_percentage=trend_data['percentage'],
            market_recommendation=recommendation,
            confidence_level=self._calculate_confidence_level(recent_prices),
            historical_data=historical_data,
            location=price_input.location,
            date_analyzed=date.today().strftime('%Y-%m-%d')
        )
    
    def analyze_livestock_profitability(self, livestock_id: int) -> ProfitabilityResult:
        """
        Analyze profitability of a specific livestock animal
        
        Args:
            livestock_id: ID of the livestock to analyze
            
        Returns:
            ProfitabilityResult object with profitability analysis
        """
        from .models import Livestock, CostRecord, MarketPrice
        
        try:
            livestock = Livestock.objects.get(id=livestock_id)
        except Livestock.DoesNotExist:
            return None
        
        # Calculate current market value
        current_market_value = self._calculate_current_market_value(livestock)
        
        # Calculate total investment (purchase price + costs)
        total_investment = self._calculate_total_investment(livestock)
        
        # Calculate estimated profit
        estimated_profit = current_market_value - total_investment
        profit_margin = (estimated_profit / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate break-even price
        break_even_price = total_investment / float(livestock.current_weight_kg or 1)
        
        # Generate recommendation
        recommendation = self._generate_profitability_recommendation(
            profit_margin, estimated_profit, livestock
        )
        
        # Cost breakdown
        cost_breakdown = self._get_cost_breakdown(livestock)
        
        return ProfitabilityResult(
            livestock_id=livestock_id,
            current_market_value=round(current_market_value, 2),
            total_investment=round(total_investment, 2),
            estimated_profit=round(estimated_profit, 2),
            profit_margin_percentage=round(profit_margin, 2),
            break_even_price=round(break_even_price, 2),
            recommendation=recommendation,
            cost_breakdown=cost_breakdown
        )
    
    def get_selling_recommendations(self, farmer_id: int) -> List[Dict]:
        """Get selling recommendations for all farmer's livestock"""
        from .models import Livestock
        
        livestock_list = Livestock.objects.filter(
            farmer_id=farmer_id,
            status='HEALTHY'
        )
        
        recommendations = []
        for livestock in livestock_list:
            profitability = self.analyze_livestock_profitability(livestock.id)
            if profitability:
                recommendations.append({
                    'livestock': livestock,
                    'profitability': profitability,
                    'action_priority': self._calculate_action_priority(profitability),
                    'optimal_selling_time': self._estimate_optimal_selling_time(livestock)
                })
        
        # Sort by action priority and profit potential
        recommendations.sort(key=lambda x: (-x['action_priority'], -x['profitability'].estimated_profit))
        
        return recommendations
    
    def _create_empty_price_result(self, location: str) -> PriceAnalysisResult:
        """Create empty result when no data available"""
        return PriceAnalysisResult(
            current_price_per_kg=0.0,
            price_trend='STABLE',
            trend_percentage=0.0,
            market_recommendation='Insufficient market data available. Please check with local markets.',
            confidence_level='LOW',
            historical_data=[],
            location=location,
            date_analyzed=date.today().strftime('%Y-%m-%d')
        )
    
    def _generate_estimated_price(self, animal_type, price_input: PriceAnalysisInput) -> PriceAnalysisResult:
        """Generate estimated prices when no recent data available"""
        # Base estimated prices by animal type (these would come from external APIs in production)
        base_prices = {
            'Cattle': 8.50,
            'Goats': 12.00,
            'Sheep': 10.00,
            'Poultry': 4.50,
            'Pigs': 6.00
        }
        
        estimated_price = base_prices.get(animal_type.name, 7.00)
        
        # Adjust for quality grade
        quality_adjustments = {
            'PREMIUM': 1.3,
            'GOOD': 1.1,
            'AVERAGE': 1.0,
            'POOR': 0.8
        }
        
        adjusted_price = estimated_price * quality_adjustments.get(price_input.quality_grade, 1.0)
        
        return PriceAnalysisResult(
            current_price_per_kg=round(adjusted_price, 2),
            price_trend='STABLE',
            trend_percentage=0.0,
            market_recommendation=f'Estimated price based on regional averages. Recommend checking local markets for current prices.',
            confidence_level='LOW',
            historical_data=[],
            location=price_input.location,
            date_analyzed=date.today().strftime('%Y-%m-%d')
        )
    
    def _calculate_price_trend(self, recent_prices) -> Dict:
        """Calculate price trend from recent data"""
        if len(recent_prices) < 2:
            return {'trend': 'STABLE', 'percentage': 0.0}
        
        # Compare recent average with older average
        recent_avg = sum(float(p.price_per_kg) for p in recent_prices[:5]) / min(5, len(recent_prices))
        older_avg = sum(float(p.price_per_kg) for p in recent_prices[5:15]) / min(10, len(recent_prices[5:15])) if len(recent_prices) > 5 else recent_avg
        
        if older_avg == 0:
            return {'trend': 'STABLE', 'percentage': 0.0}
        
        percentage_change = ((recent_avg - older_avg) / older_avg) * 100
        
        if percentage_change > 5:
            trend = 'RISING'
        elif percentage_change < -5:
            trend = 'FALLING'
        else:
            trend = 'STABLE'
        
        return {'trend': trend, 'percentage': round(percentage_change, 2)}
    
    def _generate_market_recommendation(self, trend_data: Dict, current_price: float, animal_type) -> str:
        """Generate market recommendation based on trends"""
        trend = trend_data['trend']
        percentage = abs(trend_data['percentage'])
        
        if trend == 'RISING' and percentage > 10:
            return f"Strong upward trend (+{percentage:.1f}%). Good time to sell {animal_type.name.lower()}. Consider selling mature animals."
        elif trend == 'RISING':
            return f"Prices rising (+{percentage:.1f}%). Monitor for optimal selling opportunity."
        elif trend == 'FALLING' and percentage > 10:
            return f"Prices declining (-{percentage:.1f}%). Consider holding unless urgent. Focus on cost reduction."
        elif trend == 'FALLING':
            return f"Slight price decline (-{percentage:.1f}%). Monitor market conditions."
        else:
            return f"Stable market conditions. Normal selling/buying activities recommended."
    
    def _calculate_confidence_level(self, recent_prices) -> str:
        """Calculate confidence level based on data availability"""
        price_count = len(recent_prices)
        
        if price_count >= 15:
            return 'HIGH'
        elif price_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _format_historical_data(self, price_records) -> List[Dict]:
        """Format historical data for frontend charts"""
        return [
            {
                'date': record.date_recorded.strftime('%Y-%m-%d'),
                'price': float(record.price_per_kg),
                'location': record.location,
                'quality': record.quality_grade
            }
            for record in price_records
        ]
    
    def _calculate_current_market_value(self, livestock) -> float:
        """Calculate current market value of livestock"""
        from .models import MarketPrice
        
        # Get recent market prices for this animal type and location
        recent_prices = MarketPrice.objects.filter(
            animal_type=livestock.animal_type,
            date_recorded__gte=date.today() - timedelta(days=30)
        ).order_by('-date_recorded')
        
        if livestock.breed:
            breed_prices = recent_prices.filter(breed=livestock.breed)
            if breed_prices.exists():
                recent_prices = breed_prices
        
        if recent_prices.exists():
            # Use average of recent prices
            avg_price_per_kg = sum(float(p.price_per_kg) for p in recent_prices[:5]) / min(5, len(recent_prices))
        else:
            # Use estimated prices
            base_prices = {'Cattle': 8.50, 'Goats': 12.00, 'Sheep': 10.00, 'Poultry': 4.50}
            avg_price_per_kg = base_prices.get(livestock.animal_type.name, 7.00)
        
        current_weight = float(livestock.current_weight_kg or 0)
        return avg_price_per_kg * current_weight
    
    def _calculate_total_investment(self, livestock) -> float:
        """Calculate total investment in livestock"""
        from .models import CostRecord
        
        # Initial purchase price
        total_investment = float(livestock.purchase_price or 0)
        
        # Add all costs associated with this livestock
        costs = CostRecord.objects.filter(livestock=livestock)
        total_costs = sum(float(cost.amount) for cost in costs)
        
        return total_investment + total_costs
    
    def _generate_profitability_recommendation(self, profit_margin: float, estimated_profit: float, livestock) -> str:
        """Generate profitability recommendation"""
        if profit_margin > 20:
            return f"Excellent profit potential ({profit_margin:.1f}%). Consider selling if market conditions are favorable."
        elif profit_margin > 10:
            return f"Good profit margin ({profit_margin:.1f}%). Ready for sale when convenient."
        elif profit_margin > 0:
            return f"Moderate profit expected ({profit_margin:.1f}%). Monitor growth and market prices."
        elif profit_margin > -10:
            return f"Close to break-even ({profit_margin:.1f}%). Hold and reduce costs if possible."
        else:
            return f"Currently at loss ({profit_margin:.1f}%). Review feeding costs and consider veterinary consultation."
    
    def _get_cost_breakdown(self, livestock) -> Dict:
        """Get detailed cost breakdown for livestock"""
        from .models import CostRecord
        
        costs = CostRecord.objects.filter(livestock=livestock)
        
        breakdown = {
            'purchase_price': float(livestock.purchase_price or 0),
            'feed_costs': 0,
            'veterinary_costs': 0,
            'medicine_costs': 0,
            'other_costs': 0
        }
        
        for cost in costs:
            amount = float(cost.amount)
            if cost.category == 'FEED':
                breakdown['feed_costs'] += amount
            elif cost.category == 'VETERINARY':
                breakdown['veterinary_costs'] += amount
            elif cost.category == 'MEDICINE':
                breakdown['medicine_costs'] += amount
            else:
                breakdown['other_costs'] += amount
        
        return breakdown
    
    def _calculate_action_priority(self, profitability: ProfitabilityResult) -> int:
        """Calculate action priority for selling recommendations"""
        if profitability.profit_margin_percentage > 20:
            return 5  # High priority
        elif profitability.profit_margin_percentage > 10:
            return 4  # Medium-high priority
        elif profitability.profit_margin_percentage > 0:
            return 3  # Medium priority
        elif profitability.profit_margin_percentage > -10:
            return 2  # Low priority
        else:
            return 1  # Very low priority
    
    def _estimate_optimal_selling_time(self, livestock) -> str:
        """Estimate optimal selling time"""
        age_months = livestock.age_months or 0
        
        optimal_ages = {
            'Cattle': 24,
            'Goats': 12,
            'Sheep': 12,
            'Poultry': 3
        }
        
        optimal_age = optimal_ages.get(livestock.animal_type.name, 12)
        
        if age_months >= optimal_age:
            return "Ready for sale now"
        else:
            months_to_wait = optimal_age - age_months
            return f"Optimal in {months_to_wait} months"
