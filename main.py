import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import supabase

app = FastAPI()
