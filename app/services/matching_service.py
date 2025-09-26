from app.models import Resource, ResourceType
from sqlalchemy import func
import math

class MatchingService:
    def __init__(self):
        pass
    
    def find_nearby_resources(self, resource_type, location, latitude=None, longitude=None, limit=5):
        """Find nearby resources based on location"""
        
        # Base query for active resources of the specified type with available capacity
        query = Resource.query.filter(
            Resource.resource_type == resource_type,
            Resource.is_active == True,
            Resource.available_capacity > 0
        )
        
        # If coordinates are provided, use distance-based sorting
        if latitude and longitude:
            # Calculate distance using Haversine formula (approximate)
            query = query.order_by(
                func.sqrt(
                    func.pow(Resource.latitude - latitude, 2) + 
                    func.pow(Resource.longitude - longitude, 2)
                )
            )
        else:
            # Simple text-based location matching
            # In a real implementation, you'd use geocoding services
            query = query.filter(
                Resource.location.ilike(f'%{location}%')
            ).order_by(Resource.available_capacity.desc())
        
        return query.limit(limit).all()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def get_resource_recommendations(self, user_location, resource_type, max_distance_km=50):
        """Get resource recommendations based on user location and preferences"""
        
        # This would integrate with mapping services in production
        # For now, we'll use simple location-based matching
        
        resources = self.find_nearby_resources(
            resource_type=resource_type,
            location=user_location,
            limit=10
        )
        
        # Score resources based on availability, distance, and capacity
        scored_resources = []
        for resource in resources:
            score = self.calculate_resource_score(resource, user_location)
            scored_resources.append((resource, score))
        
        # Sort by score (higher is better)
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        
        return [resource for resource, score in scored_resources[:5]]
    
    def calculate_resource_score(self, resource, user_location):
        """Calculate a score for resource matching"""
        score = 0
        
        # Availability score (0-40 points)
        if resource.available_capacity > 0:
            capacity_ratio = min(resource.available_capacity / max(resource.total_capacity, 1), 1)
            score += capacity_ratio * 40
        
        # Location relevance score (0-30 points)
        if user_location.lower() in resource.location.lower():
            score += 30
        elif any(word in resource.location.lower() for word in user_location.lower().split()):
            score += 15
        
        # Organization reliability score (0-20 points)
        if resource.organization:
            # Government and established NGOs get higher scores
            if any(keyword in resource.organization.lower() for keyword in ['government', 'ministry', 'nema', 'red cross']):
                score += 20
            elif any(keyword in resource.organization.lower() for keyword in ['ngo', 'foundation', 'charity']):
                score += 15
            else:
                score += 10
        
        # Contact availability score (0-10 points)
        if resource.contact_phone:
            score += 10
        
        return score
    
    def update_resource_availability(self, resource_id, new_capacity):
        """Update resource availability"""
        resource = Resource.query.get(resource_id)
        if resource:
            resource.available_capacity = new_capacity
            return True
        return False
    
    def get_resource_statistics(self, resource_type=None):
        """Get statistics about resource availability"""
        query = Resource.query.filter(Resource.is_active == True)
        
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        
        resources = query.all()
        
        total_resources = len(resources)
        total_capacity = sum(r.total_capacity for r in resources)
        available_capacity = sum(r.available_capacity for r in resources)
        
        return {
            'total_resources': total_resources,
            'total_capacity': total_capacity,
            'available_capacity': available_capacity,
            'utilization_rate': (total_capacity - available_capacity) / max(total_capacity, 1) * 100
        }