"""
Custom exceptions for the middle ear barotrauma model
"""

class BarotraumaError(Exception):
    """Base exception class for all model errors"""
    pass

class PhysiologyError(BarotraumaError):
    """Errors related to physiological parameters"""
    pass

class SimulationError(BarotraumaError):
    """Errors related to simulation execution"""
    pass

class ParameterError(BarotraumaError):
    """Errors related to parameter validation"""
    pass

class ETModelError(BarotraumaError):
    """Errors related to Eustachian tube model"""
    pass

class AnalysisError(BarotraumaError):
    """Errors related to data analysis"""
    pass

class DatabaseError(BarotraumaError):
    """Errors related to database operations"""
    pass 