from flask import Blueprint

pesa = Blueprint('pesa', __name__)

from . import hooks