from fastapi import APIRouter
from api_models import IntersectionStatus, TrafficLightStatus

router = APIRouter(prefix="/api/system")