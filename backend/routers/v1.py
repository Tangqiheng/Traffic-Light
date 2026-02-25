from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from api_models import IntersectionStatus, TrafficLightStatus, ControlCommand, ControlLog
from database import get_db
from services.traffic_service import TrafficService