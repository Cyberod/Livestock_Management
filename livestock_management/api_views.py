from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    operation_description="Get API health status",
    responses={
        200: openapi.Response(
            description="API is healthy",
            examples={
                "application/json": {
                    "status": "healthy",
                    "message": "Livestock Management API is running",
                    "version": "1.0.0"
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """
    Check API health status
    """
    return Response({
        "status": "healthy",
        "message": "Livestock Management API is running",
        "version": "1.0.0",
        "modules": {
            "feeding": "Ready for implementation",
            "disease_monitoring": "Ready for implementation", 
            "pricing": "Ready for implementation"
        }
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get system information",
    responses={
        200: openapi.Response(
            description="System information",
            examples={
                "application/json": {
                    "system": "Livestock Management System",
                    "target_users": "Small-scale livestock farmers",
                    "supported_animals": ["cattle", "goats", "sheep", "poultry"]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def system_info(request):
    """
    Get system information and supported features
    """
    return Response({
        "system": "Livestock Management System",
        "description": "Decision support system for small-scale livestock farmers",
        "target_users": "Small-scale livestock farmers",
        "supported_animals": ["cattle", "goats", "sheep", "poultry"],
        "key_features": [
            "Feeding recommendations",
            "Disease monitoring and alerts",
            "Market pricing guidance"
        ]
    })
