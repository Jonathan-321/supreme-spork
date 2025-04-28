from flask import Blueprint, render_template, jsonify, request
import os
import json
from datetime import datetime, timedelta
import random

# Create the blueprint for mobile app routes
mobile_app = Blueprint('mobile_app', __name__)

@mobile_app.route('/')
def mobile_home():
    """Render the mobile app home page"""
    return render_template('mobile_app.html')

@mobile_app.route('/api/weather')
def get_weather():
    """API endpoint to get weather data for the mobile app"""
    # In a production app, this would fetch real data from a weather API
    # using the farmer's location. For now, we'll return simulated data.
    
    # Get the farmer's location (would come from the user profile in real app)
    location = request.args.get('location', 'Eastern Region, Ghana')
    
    # Generate a realistic 5-day forecast
    today = datetime.now()
    forecast = []
    
    # Weather conditions common in Ghana
    conditions = [
        {"condition": "Sunny", "icon": "sun", "min_temp": 24, "max_temp": 34},
        {"condition": "Partly Cloudy", "icon": "cloud-sun", "min_temp": 22, "max_temp": 32},
        {"condition": "Cloudy", "icon": "cloud", "min_temp": 21, "max_temp": 30},
        {"condition": "Light Rain", "icon": "cloud-rain", "min_temp": 20, "max_temp": 28},
        {"condition": "Heavy Rain", "icon": "cloud-showers-heavy", "min_temp": 19, "max_temp": 26},
        {"condition": "Thunderstorm", "icon": "bolt", "min_temp": 18, "max_temp": 25}
    ]
    
    # Generate a realistic pattern (e.g., sunny → clouds → rain → clearing)
    # This is simplified, but could be made more realistic with Markov chains
    pattern = [
        random.choice(conditions[:2]),  # Mostly good weather today
        random.choice(conditions[:3]),  # Slight chance of clouds
        random.choice(conditions[1:4]),  # Higher chance of clouds/light rain
        random.choice(conditions),      # Any condition possible
        random.choice(conditions[:3])   # Return to better weather
    ]
    
    for i in range(5):
        day = today + timedelta(days=i)
        day_name = day.strftime("%a") if i > 0 else "Today"
        
        # Get the weather pattern for this day
        weather = pattern[i]
        
        # Add some randomness to the temperatures
        temp_variation = random.uniform(-2, 2)
        
        forecast.append({
            "date": day.strftime("%Y-%m-%d"),
            "day": day_name,
            "condition": weather["condition"],
            "icon": weather["icon"],
            "temperature": round(random.uniform(
                weather["min_temp"], 
                weather["max_temp"]
            ) + temp_variation),
            "precipitation_chance": round(random.uniform(
                0, 90 if "Rain" in weather["condition"] else 30
            ))
        })
    
    # Generate farming activity recommendations based on weather
    recommendations = []
    
    # Today's recommendation
    today_weather = forecast[0]
    if today_weather["condition"] in ["Sunny", "Partly Cloudy"]:
        if random.random() > 0.5:
            recommendations.append("Good day for harvesting maize in Eastern fields")
        else:
            recommendations.append("Favorable conditions for applying fertilizer")
    elif today_weather["condition"] in ["Cloudy"]:
        recommendations.append("Good day for planting seedlings")
    elif "Rain" in today_weather["condition"]:
        recommendations.append("Delay pesticide application due to expected rainfall")
    
    # Upcoming recommendations
    if any("Rain" in day["condition"] for day in forecast[1:3]):
        recommendations.append("Plan indoor activities for midweek due to rain")
    
    if all(day["temperature"] > 30 for day in forecast):
        recommendations.append("Consider additional irrigation this week due to high temperatures")
    
    return jsonify({
        "location": location,
        "current": {
            "temperature": forecast[0]["temperature"],
            "condition": forecast[0]["condition"],
            "icon": forecast[0]["icon"],
            "humidity": round(random.uniform(60, 85)),
            "wind_speed": round(random.uniform(5, 15)),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "forecast": forecast,
        "recommendations": recommendations
    })

@mobile_app.route('/api/crop-health')
def get_crop_health():
    """API endpoint to get crop health data for the mobile app"""
    # In a production app, this would fetch real NDVI data from satellite imagery
    # For now, we'll return simulated data
    
    farm_id = request.args.get('farm_id', 'farm001')
    crop_type = request.args.get('crop_type', 'maize')
    
    # Base health value - would come from actual NDVI analysis in production
    base_health = random.uniform(0.65, 0.85)
    
    # Convert to percentage for easier understanding by farmers
    health_percent = round(base_health * 100)
    
    # Determine health status text
    health_status = "Poor"
    if health_percent > 25: health_status = "Fair"
    if health_percent > 50: health_status = "Good"
    if health_percent > 75: health_status = "Excellent"
    
    # Generate some realistic issues that might be detected
    possible_issues = [
        {
            "type": "water_stress",
            "icon": "tint-slash",
            "name": "Water stress detected",
            "location": "Northern section (2 acres)",
            "severity": "moderate",
            "recommendation": "Consider irrigation within 48 hours"
        },
        {
            "type": "pest",
            "icon": "bug",
            "name": "Possible pest activity",
            "location": "Eastern edge (0.5 acres)",
            "severity": "mild",
            "recommendation": "Monitor closely for armyworm presence"
        },
        {
            "type": "nutrient",
            "icon": "leaf",
            "name": "Nitrogen deficiency signs",
            "location": "Central plot (1.5 acres)",
            "severity": "mild",
            "recommendation": "Consider supplemental nitrogen application"
        },
        {
            "type": "disease",
            "icon": "virus",
            "name": "Early signs of leaf blight",
            "location": "Southern corner (0.3 acres)",
            "severity": "moderate",
            "recommendation": "Apply approved fungicide treatment"
        }
    ]
    
    # Randomly select 0-2 issues based on the health score
    # Lower health scores = more likely to have issues
    num_issues = 0
    if health_percent < 60:
        num_issues = 2
    elif health_percent < 75:
        num_issues = 1
    elif random.random() < 0.3:  # Even healthy fields might have minor issues
        num_issues = 1
    
    issues = random.sample(possible_issues, min(num_issues, len(possible_issues)))
    
    # Field sections for the visualization (simplified)
    field_sections = []
    
    # Create a grid of sections with health values
    grid_size = 5
    for i in range(grid_size):
        for j in range(grid_size):
            # Base health with some variation
            section_health = min(1.0, max(0.0, base_health + random.uniform(-0.15, 0.15)))
            
            # If there are issues, make those areas show lower health
            for issue in issues:
                if (("Northern" in issue["location"] and i < 2) or
                    ("Southern" in issue["location"] and i > 3) or 
                    ("Eastern" in issue["location"] and j > 3) or
                    ("Western" in issue["location"] and j < 2) or
                    ("Central" in issue["location"] and 1 < i < 4 and 1 < j < 4)):
                    section_health = max(0.3, section_health - random.uniform(0.1, 0.3))
            
            field_sections.append({
                "row": i,
                "col": j,
                "health": round(section_health, 2)
            })
    
    return jsonify({
        "farm_id": farm_id,
        "crop_type": crop_type,
        "planting_date": "2025-03-15",
        "growth_stage": "Vegetative",
        "days_to_harvest": random.randint(45, 60),
        "overall_health": {
            "value": base_health,
            "percent": health_percent,
            "status": health_status,
            "trend": random.choice(["improving", "stable", "declining"])
        },
        "field_health_map": field_sections,
        "detected_issues": issues,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    })

@mobile_app.route('/api/market-prices')
def get_market_prices():
    """API endpoint to get crop market prices for the mobile app"""
    # In a production app, this would fetch real data from market price APIs or databases
    
    crop_type = request.args.get('crop_type', 'all')
    region = request.args.get('region', 'Eastern Region')
    
    # Base prices for common crops in Ghana (in GH₵ per ton)
    base_prices = {
        "maize": 850,
        "rice": 1200,
        "cassava": 650,
        "yam": 950,
        "cocoa": 16500,
        "plantain": 1100
    }
    
    # Generate price history (last 30 days)
    days = 30
    today = datetime.now()
    
    price_history = {}
    for crop, base in base_prices.items():
        history = []
        
        # Start with the current price and work backwards with realistic variations
        current_price = base
        
        for i in range(days):
            day = today - timedelta(days=i)
            
            # Add some daily variation (between -2% and +2%)
            price_change = current_price * random.uniform(-0.02, 0.02)
            
            # Add some trends over time
            trend_factor = random.uniform(-0.005, 0.005)  # Longer term trend
            
            # For the historical prices, work backwards
            if i > 0:
                prev_price = history[0]["price"]
                current_price = max(prev_price * 0.95, 
                                   prev_price + price_change + (prev_price * trend_factor))
            
            history.insert(0, {
                "date": day.strftime("%Y-%m-%d"),
                "price": round(current_price, 2)
            })
        
        price_history[crop] = history
    
    # Calculate price changes for the UI
    price_changes = {}
    for crop, history in price_history.items():
        if len(history) >= 2:
            current = history[-1]["price"]
            week_ago = history[max(0, len(history)-8)]["price"]
            change = current - week_ago
            change_pct = (change / week_ago) * 100 if week_ago > 0 else 0
            
            price_changes[crop] = {
                "current": current,
                "change": round(change, 2),
                "change_percent": round(change_pct, 1),
                "direction": "up" if change > 0 else "down" if change < 0 else "stable"
            }
    
    # Market insights based on price trends
    insights = []
    
    # Identify best selling opportunities
    best_crop = max(price_changes.items(), key=lambda x: x[1]["change_percent"])
    if best_crop[1]["change_percent"] > 5:
        insights.append(f"{best_crop[0].title()} prices are rising significantly. Consider selling soon.")
    
    # Identify concerning trends
    worst_crop = min(price_changes.items(), key=lambda x: x[1]["change_percent"])
    if worst_crop[1]["change_percent"] < -5:
        insights.append(f"{worst_crop[0].title()} prices are falling. Consider holding if possible.")
    
    # Add general market insights
    if random.random() > 0.7:
        insights.append("Overall market prices are stable for the coming weeks.")
    else:
        insights.append("Market analysts predict price increases after the upcoming holiday.")
    
    # Filter by crop type if specified
    if crop_type != 'all' and crop_type in base_prices:
        filtered_prices = {crop_type: price_history[crop_type]}
        filtered_changes = {crop_type: price_changes[crop_type]}
    else:
        filtered_prices = price_history
        filtered_changes = price_changes
    
    return jsonify({
        "region": region,
        "prices": filtered_changes,
        "history": filtered_prices,
        "insights": insights,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@mobile_app.route('/api/credit-score')
def get_credit_score():
    """API endpoint to get farmer credit score data"""
    farmer_id = request.args.get('farmer_id', 'farmer001')
    
    # In a real app, this would be calculated based on multiple factors:
    # - Loan repayment history
    # - Farm productivity data
    # - Weather resilience
    # - Crop diversification
    # - Farm management practices
    
    # Generate a realistic AgriCredit score (typically 300-850 range)
    current_score = random.randint(580, 720)
    
    # Previous score (with small realistic variation)
    prev_score = current_score + random.randint(-15, 10)
    
    # Determine score category
    category = "Poor"
    if current_score >= 500: category = "Fair"
    if current_score >= 650: category = "Good"
    if current_score >= 750: category = "Excellent"
    
    # Generate score components
    components = [
        {
            "name": "Repayment History",
            "score": random.randint(60, 95),
            "weight": 35,
            "description": "Based on timeliness of previous loan payments"
        },
        {
            "name": "Farm Productivity",
            "score": random.randint(55, 90),
            "weight": 25,
            "description": "Based on crop yields relative to regional averages"
        },
        {
            "name": "Climate Resilience",
            "score": random.randint(50, 85),
            "weight": 20,
            "description": "Based on adaptation to weather events and climate patterns"
        },
        {
            "name": "Farm Management",
            "score": random.randint(60, 90),
            "weight": 20,
            "description": "Based on farming practices and resource management"
        }
    ]
    
    # Generate personalized recommendations to improve score
    recommendations = []
    
    # Find the lowest scoring component
    lowest_component = min(components, key=lambda x: x["score"])
    
    if lowest_component["name"] == "Repayment History":
        recommendations.append({
            "title": "Make Your Next Payment Early",
            "description": "Early payments can boost your score by up to 10 points"
        })
    elif lowest_component["name"] == "Farm Productivity":
        recommendations.append({
            "title": "Document Your Crop Rotation Plan",
            "description": "Systematic crop rotation demonstrates good farm management"
        })
    elif lowest_component["name"] == "Climate Resilience":
        recommendations.append({
            "title": "Implement Water Conservation Measures",
            "description": "Documented water management improves your climate resilience score"
        })
    elif lowest_component["name"] == "Farm Management":
        recommendations.append({
            "title": "Complete Your Farm Profile",
            "description": "Add your irrigation details to improve your score"
        })
    
    # Add a general recommendation
    recommendations.append({
        "title": "Attend Financial Literacy Workshop",
        "description": "Completion certificates can add bonus points to your score"
    })
    
    return jsonify({
        "farmer_id": farmer_id,
        "current_score": current_score,
        "previous_score": prev_score,
        "category": category,
        "change": current_score - prev_score,
        "components": components,
        "recommendations": recommendations,
        "history": [
            # 6-month score history
            {"month": (datetime.now() - timedelta(days=150)).strftime("%b"), "score": prev_score - random.randint(5, 15)},
            {"month": (datetime.now() - timedelta(days=120)).strftime("%b"), "score": prev_score - random.randint(0, 10)},
            {"month": (datetime.now() - timedelta(days=90)).strftime("%b"), "score": prev_score - random.randint(-5, 5)},
            {"month": (datetime.now() - timedelta(days=60)).strftime("%b"), "score": prev_score - random.randint(-10, 0)},
            {"month": (datetime.now() - timedelta(days=30)).strftime("%b"), "score": prev_score},
            {"month": datetime.now().strftime("%b"), "score": current_score}
        ],
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    })

@mobile_app.route('/api/loan-status')
def get_loan_status():
    """API endpoint to get farmer's loan status"""
    farmer_id = request.args.get('farmer_id', 'farmer001')
    
    # In a real app, this would fetch from a loans database
    # For now, we'll simulate an active loan
    
    # Loan details
    loan_amount = 5000
    interest_rate = 8.5
    loan_term_months = 12
    start_date = datetime.now() - timedelta(days=random.randint(120, 210))
    
    # Calculate payments made and remaining
    months_elapsed = (datetime.now() - start_date).days / 30
    months_elapsed = min(loan_term_months, max(1, round(months_elapsed)))
    
    # Simple amortization calculation
    monthly_rate = interest_rate / 100 / 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term_months) / ((1 + monthly_rate) ** loan_term_months - 1)
    
    # Calculate remaining balance
    remaining_principal = loan_amount
    for i in range(int(months_elapsed)):
        interest = remaining_principal * monthly_rate
        principal = monthly_payment - interest
        remaining_principal -= principal
    
    remaining_principal = max(0, round(remaining_principal))
    payments_made = int(months_elapsed)
    payments_remaining = loan_term_months - payments_made
    
    # Next payment details
    next_payment_date = start_date + timedelta(days=30 * (payments_made + 1))
    
    # Payment history
    payment_history = []
    current_date = start_date
    current_principal = loan_amount
    
    for i in range(int(months_elapsed)):
        payment_date = current_date + timedelta(days=30)
        interest = current_principal * monthly_rate
        principal = monthly_payment - interest
        current_principal -= principal
        
        # Add some randomness to payment dates (some early, some on time, some slightly late)
        random_days = random.randint(-3, 2)
        actual_date = payment_date + timedelta(days=random_days)
        
        payment_history.append({
            "payment_number": i + 1,
            "due_date": payment_date.strftime("%Y-%m-%d"),
            "amount": round(monthly_payment, 2),
            "principal": round(principal, 2),
            "interest": round(interest, 2),
            "remaining_balance": round(current_principal, 2),
            "status": "paid",
            "payment_date": actual_date.strftime("%Y-%m-%d")
        })
    
    # Loan purpose tags
    purpose_tags = ["Seasonal Planting", "Maize", "Fertilizer", "Seeds"]
    
    # Loan status determination
    if remaining_principal <= 0:
        status = "paid"
    elif next_payment_date < datetime.now() - timedelta(days=15):
        status = "overdue"
    else:
        status = "active"
    
    return jsonify({
        "farmer_id": farmer_id,
        "loan_id": "L" + str(random.randint(10000, 99999)),
        "status": status,
        "loan_type": "Seasonal Planting Loan",
        "purpose_tags": purpose_tags,
        "amount": loan_amount,
        "remaining_balance": remaining_principal,
        "interest_rate": interest_rate,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=30 * loan_term_months)).strftime("%Y-%m-%d"),
        "term_months": loan_term_months,
        "monthly_payment": round(monthly_payment, 2),
        "payments_made": payments_made,
        "payments_remaining": payments_remaining,
        "next_payment": {
            "date": next_payment_date.strftime("%Y-%m-%d"),
            "amount": round(monthly_payment, 2),
            "status": "upcoming"
        },
        "payment_history": payment_history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@mobile_app.route('/api/activities')
def get_activities():
    """API endpoint to get farmer's recent activities and notifications"""
    farmer_id = request.args.get('farmer_id', 'farmer001')
    
    # Current time for realistic timestamps
    now = datetime.now()
    
    # Activity types that might be relevant to farmers
    activity_types = [
        {
            "type": "weather_alert",
            "icon": "cloud-rain",
            "title_templates": [
                "Weather Alert: Rain Expected",
                "Weather Alert: High Temperatures",
                "Weather Alert: Wind Advisory",
                "Weather Alert: Drought Conditions"
            ],
            "description_templates": [
                "Heavy rain expected in your region in the next 24 hours. Consider delaying pesticide application.",
                "Temperatures exceeding 35°C expected this week. Ensure adequate irrigation.",
                "Strong winds forecasted. Secure any loose equipment on your farm.",
                "Continued dry conditions expected. Consider water conservation measures."
            ]
        },
        {
            "type": "crop_health",
            "icon": "seedling",
            "title_templates": [
                "Crop Health Alert",
                "NDVI Update Available",
                "Potential Disease Detected",
                "Crop Development Milestone"
            ],
            "description_templates": [
                "Possible water stress detected in your northern maize field. Consider irrigating within 48 hours.",
                "Latest satellite imagery shows improving crop health in your eastern fields.",
                "Early signs of fungal disease detected in your cassava plots. Consider preventative treatment.",
                "Your maize crop has reached the flowering stage. Optimal time for second fertilizer application."
            ]
        },
        {
            "type": "loan_update",
            "icon": "hand-holding-usd",
            "title_templates": [
                "Loan Payment Successful",
                "Loan Application Update",
                "Payment Reminder",
                "Loan Milestone Reached"
            ],
            "description_templates": [
                "Your monthly loan payment of GH₵ 750 was successfully processed.",
                "Your loan application has moved to the approval stage.",
                "Your next loan payment of GH₵ 750 is due in 5 days.",
                "Congratulations! You've reached the halfway point in your loan repayment."
            ]
        },
        {
            "type": "market_update",
            "icon": "chart-line",
            "title_templates": [
                "Market Price Alert",
                "Selling Opportunity",
                "Market Forecast Update",
                "New Buyer Available"
            ],
            "description_templates": [
                "Maize prices have increased by 5% in your region this week.",
                "Current rice prices are at a 3-month high. Consider selling your surplus.",
                "Market analysts predict declining cassava prices next month.",
                "New bulk buyer interested in organic produce in your area."
            ]
        }
    ]
    
    # Generate a realistic mix of activities
    num_activities = random.randint(5, 10)
    activities = []
    
    for i in range(num_activities):
        # Select a random activity type
        activity_type = random.choice(activity_types)
        
        # Generate a timestamp (more recent for earlier activities)
        days_ago = int(i * random.uniform(0.5, 2.5))
        hours_ago = int(random.uniform(0, 24))
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        
        # Select random title and description templates
        title = random.choice(activity_type["title_templates"])
        description = random.choice(activity_type["description_templates"])
        
        activities.append({
            "id": f"act-{random.randint(1000, 9999)}",
            "type": activity_type["type"],
            "icon": activity_type["icon"],
            "title": title,
            "description": description,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "read": random.random() > 0.3,  # 70% chance of being read
            "action_url": f"/mobile/{activity_type['type']}/{random.randint(1000, 9999)}"
        })
    
    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Count unread notifications
    unread_count = sum(1 for activity in activities if not activity["read"])
    
    return jsonify({
        "farmer_id": farmer_id,
        "activities": activities,
        "unread_count": unread_count,
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S")
    })
